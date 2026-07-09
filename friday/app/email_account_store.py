"""Local guarded email account storage with Windows DPAPI support."""

from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
from typing import Any, Callable

from friday import config


EMAIL_ACCOUNT_SAVE_TOKEN = "KONTO SPEICHERN"
EMAIL_ACCOUNT_DELETE_TOKEN = "KONTO LOESCHEN"
EMAIL_ACCOUNT_FILE_NAME = "email_account.json"


EMAIL_PROVIDER_PRESETS: dict[str, dict[str, Any]] = {
    "gmail": {
        "display_name": "Gmail",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 465,
        "imap_host": "imap.gmail.com",
        "imap_port": 993,
    },
    "outlook": {
        "display_name": "Outlook",
        "smtp_host": "smtp.office365.com",
        "smtp_port": 587,
        "imap_host": "outlook.office365.com",
        "imap_port": 993,
    },
    "gmx": {
        "display_name": "GMX",
        "smtp_host": "mail.gmx.net",
        "smtp_port": 587,
        "imap_host": "imap.gmx.net",
        "imap_port": 993,
    },
    "web.de": {
        "display_name": "web.de",
        "smtp_host": "smtp.web.de",
        "smtp_port": 587,
        "imap_host": "imap.web.de",
        "imap_port": 993,
    },
}


@dataclass(frozen=True)
class EmailAccount:
    """One locally stored email account without plaintext password."""

    display_name: str
    email_address: str
    smtp_host: str
    smtp_port: int
    imap_host: str
    imap_port: int
    username: str
    encrypted_app_password: str
    encryption_method: str
    connected_at: str
    last_test_ok: bool
    agent_notes: str = ""


@dataclass(frozen=True)
class EmailAccountWriteResult:
    """Result of a guarded email account write/delete operation."""

    allowed: bool
    persisted: bool
    account_path: str
    message: str
    blocked_reasons: tuple[str, ...]
    account: EmailAccount | None = None
    plaintext_password_persisted: bool = False
    preview_only: bool = False
    external_call_used: bool = False


def get_email_account_path(base_dir: Path | str | None = None) -> Path:
    """Return the local account JSON path under local_data/accounts."""
    root = Path(base_dir) if base_dir is not None else config.LOCAL_DATA_DIR
    return root / "accounts" / EMAIL_ACCOUNT_FILE_NAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _validate_port(port: int | str) -> int:
    parsed = int(port)
    if parsed not in {465, 587, 993} and not (1 <= parsed <= 65535):
        raise ValueError("Ungueltiger Port.")
    return parsed


def build_email_account_from_plain_password(
    *,
    display_name: str,
    email_address: str,
    smtp_host: str,
    smtp_port: int,
    imap_host: str,
    imap_port: int,
    username: str,
    app_password: str,
    last_test_ok: bool = False,
    protector: Callable[[bytes], tuple[str, str]] | None = None,
    connected_at: str | None = None,
    agent_notes: str | None = "",
) -> EmailAccount:
    """Build an account object, encrypting the app password immediately."""
    if not _clean(email_address) or "@" not in _clean(email_address):
        raise ValueError("Eine gueltige E-Mail-Adresse ist erforderlich.")
    if not _clean(username):
        raise ValueError("Ein Benutzername ist erforderlich.")
    if not str(app_password or "").strip():
        raise ValueError("Ein App-Passwort ist erforderlich.")

    encrypted, method = (protector or protect_secret)(str(app_password).encode("utf-8"))
    return EmailAccount(
        display_name=_clean(display_name) or _clean(email_address),
        email_address=_clean(email_address),
        smtp_host=_clean(smtp_host),
        smtp_port=_validate_port(smtp_port),
        imap_host=_clean(imap_host),
        imap_port=_validate_port(imap_port),
        username=_clean(username),
        encrypted_app_password=encrypted,
        encryption_method=method,
        connected_at=connected_at or _now_iso(),
        last_test_ok=bool(last_test_ok),
        agent_notes=str(agent_notes or "").strip(),
    )


def build_email_account_from_preset(
    *,
    preset_name: str,
    email_address: str,
    username: str,
    app_password: str,
    last_test_ok: bool = False,
    protector: Callable[[bytes], tuple[str, str]] | None = None,
    agent_notes: str | None = "",
) -> EmailAccount:
    """Build an account from a known provider preset."""
    preset_key = _clean(preset_name).lower()
    if preset_key not in EMAIL_PROVIDER_PRESETS:
        raise ValueError("Unbekanntes E-Mail-Preset.")
    preset = EMAIL_PROVIDER_PRESETS[preset_key]
    return build_email_account_from_plain_password(
        display_name=preset["display_name"],
        email_address=email_address,
        smtp_host=preset["smtp_host"],
        smtp_port=int(preset["smtp_port"]),
        imap_host=preset["imap_host"],
        imap_port=int(preset["imap_port"]),
        username=username,
        app_password=app_password,
        last_test_ok=last_test_ok,
        protector=protector,
        agent_notes=agent_notes,
    )


def save_email_account(
    account: EmailAccount,
    *,
    approval_token: str,
    account_path: Path | str | None = None,
) -> EmailAccountWriteResult:
    """Persist one encrypted email account only after the hard token."""
    path = Path(account_path) if account_path is not None else get_email_account_path()
    if approval_token != EMAIL_ACCOUNT_SAVE_TOKEN:
        return EmailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="E-Mail-Konto wurde nicht gespeichert: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    serialized = asdict(account)
    text = json.dumps(serialized, ensure_ascii=False, indent=2, sort_keys=True)
    if account.encrypted_app_password and account.encrypted_app_password in text:
        plaintext_password_persisted = False
    else:
        plaintext_password_persisted = False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
    return EmailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="E-Mail-Konto wurde lokal verschluesselt gespeichert.",
        blocked_reasons=(),
        account=account,
        plaintext_password_persisted=plaintext_password_persisted,
    )


def load_email_account(account_path: Path | str | None = None) -> EmailAccount | None:
    """Load the stored email account if present."""
    path = Path(account_path) if account_path is not None else get_email_account_path()
    if not path.exists() or not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    data.setdefault("agent_notes", "")
    return EmailAccount(**data)


def save_email_account_agent_notes(
    agent_notes: str | None,
    *,
    account_path: Path | str | None = None,
) -> EmailAccountWriteResult:
    """Update only local AI-readable email account notes without touching providers."""
    path = Path(account_path) if account_path is not None else get_email_account_path()
    account = load_email_account(path)
    if account is None:
        return EmailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="Keine lokale E-Mail-Konto-Datei zum Speichern der Agent-Notiz gefunden.",
            blocked_reasons=("email_account_missing",),
        )
    updated = replace(account, agent_notes=str(agent_notes or "").strip())
    result = save_email_account(
        updated,
        approval_token=EMAIL_ACCOUNT_SAVE_TOKEN,
        account_path=path,
    )
    if not result.persisted:
        return result
    return EmailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="E-Mail-Agent-Notiz wurde lokal gespeichert.",
        blocked_reasons=(),
        account=updated,
        plaintext_password_persisted=False,
    )


def delete_email_account(
    *,
    approval_token: str,
    account_path: Path | str | None = None,
) -> EmailAccountWriteResult:
    """Delete the local email account only after the hard token."""
    path = Path(account_path) if account_path is not None else get_email_account_path()
    if approval_token != EMAIL_ACCOUNT_DELETE_TOKEN:
        return EmailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="E-Mail-Konto wurde nicht geloescht: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    if path.exists() and path.is_file():
        path.unlink()
    return EmailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="E-Mail-Konto wurde lokal geloescht.",
        blocked_reasons=(),
    )


def decrypt_email_account_password(
    account: EmailAccount,
    *,
    unprotector: Callable[[str, str], bytes] | None = None,
) -> str:
    """Decrypt the stored app password for runtime login only."""
    raw = (unprotector or unprotect_secret)(account.encrypted_app_password, account.encryption_method)
    return raw.decode("utf-8")


class _DataBlob(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


def _dpapi_available() -> bool:
    return platform.system().lower() == "windows"


def _dpapi_protect(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    input_buffer = ctypes.create_string_buffer(data)
    input_blob = _DataBlob(len(data), ctypes.cast(input_buffer, ctypes.POINTER(ctypes.c_byte)))
    output_blob = _DataBlob()
    if not crypt32.CryptProtectData(
        ctypes.byref(input_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(output_blob),
    ):
        raise OSError("DPAPI CryptProtectData fehlgeschlagen.")
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree(output_blob.pbData)


def _dpapi_unprotect(data: bytes) -> bytes:
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    input_buffer = ctypes.create_string_buffer(data)
    input_blob = _DataBlob(len(data), ctypes.cast(input_buffer, ctypes.POINTER(ctypes.c_byte)))
    output_blob = _DataBlob()
    if not crypt32.CryptUnprotectData(
        ctypes.byref(input_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(output_blob),
    ):
        raise OSError("DPAPI CryptUnprotectData fehlgeschlagen.")
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree(output_blob.pbData)


def protect_secret(secret_bytes: bytes) -> tuple[str, str]:
    """Protect secret bytes with DPAPI when available, else warning base64."""
    if _dpapi_available():
        try:
            return base64.b64encode(_dpapi_protect(secret_bytes)).decode("ascii"), "windows-dpapi"
        except OSError:
            pass
    return base64.b64encode(secret_bytes).decode("ascii"), "base64-warning-no-dpapi"


def unprotect_secret(encrypted_value: str, method: str) -> bytes:
    """Reverse ``protect_secret`` for runtime use."""
    data = base64.b64decode(encrypted_value.encode("ascii"))
    if method == "windows-dpapi":
        return _dpapi_unprotect(data)
    if method == "base64-warning-no-dpapi":
        return data
    raise ValueError("Unbekannte Passwort-Verschluesselungsmethode.")


def email_account_status(account_path: Path | str | None = None) -> dict[str, Any]:
    """Return password-free account status for CLI/API/mobile."""
    account = load_email_account(account_path)
    if account is None:
        return {
            "connected": False,
            "email_address": None,
            "display_name": None,
            "agent_notes": "",
            "agent_notes_configured": False,
            "last_test_ok": False,
            "real_email_enabled": config.ENABLE_REAL_EMAIL,
            "send_limit_per_day": config.EMAIL_DAILY_SEND_LIMIT,
        }
    return {
        "connected": True,
        "email_address": account.email_address,
        "display_name": account.display_name,
        "agent_notes": account.agent_notes,
        "agent_notes_configured": bool(account.agent_notes.strip()),
        "smtp_host": account.smtp_host,
        "imap_host": account.imap_host,
        "last_test_ok": account.last_test_ok,
        "connected_at": account.connected_at,
        "encryption_method": account.encryption_method,
        "real_email_enabled": config.ENABLE_REAL_EMAIL,
        "send_limit_per_day": config.EMAIL_DAILY_SEND_LIMIT,
    }
