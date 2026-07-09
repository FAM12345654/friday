"""Guarded encrypted account store for read-only Microsoft Graph mail."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable

from friday import config
from friday.app.email_account_store import protect_secret, unprotect_secret
from friday.app.ms_mail_provider import MS_MAIL_SCOPES


MS_MAIL_ACCOUNT_SAVE_TOKEN = "KONTO SPEICHERN"
MS_MAIL_ACCOUNT_DELETE_TOKEN = "KONTO LOESCHEN"
MS_MAIL_ACCOUNT_FILE_NAME = "ms_mail_account.json"


@dataclass(frozen=True)
class MsMailAccount:
    """Encrypted local Microsoft Graph token bundle metadata."""

    client_id: str
    tenant: str
    username: str
    encrypted_token_bundle: str
    encryption_method: str
    connected_at: str
    last_test_ok: bool


@dataclass(frozen=True)
class MsMailAccountWriteResult:
    """Result of a guarded MS mail account write/delete."""

    allowed: bool
    persisted: bool
    account_path: str
    message: str
    blocked_reasons: tuple[str, ...]
    account: MsMailAccount | None = None
    preview_only: bool = False
    external_call_used: bool = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def get_ms_mail_account_path(base_dir: Path | str | None = None) -> Path:
    """Return the local encrypted MS mail account path."""
    root = Path(base_dir) if base_dir is not None else config.LOCAL_DATA_DIR
    return root / "accounts" / MS_MAIL_ACCOUNT_FILE_NAME


def build_ms_mail_account(
    *,
    client_id: str,
    tenant: str | None,
    username: str,
    token_bundle: dict[str, Any],
    last_test_ok: bool = False,
    protector: Callable[[bytes], tuple[str, str]] | None = None,
    connected_at: str | None = None,
) -> MsMailAccount:
    """Build an encrypted account object from an OAuth token bundle."""
    normalized_client_id = _clean(client_id)
    if not normalized_client_id:
        raise ValueError("Eine Microsoft Client-ID ist erforderlich.")
    normalized_username = _clean(username)
    if not normalized_username:
        raise ValueError("Ein Microsoft-Benutzername ist erforderlich.")
    if not isinstance(token_bundle, dict) or not token_bundle.get("access_token"):
        raise ValueError("Ein Microsoft OAuth-Token ist erforderlich.")
    serialized = json.dumps(token_bundle, ensure_ascii=False, sort_keys=True).encode("utf-8")
    encrypted, method = (protector or protect_secret)(serialized)
    return MsMailAccount(
        client_id=normalized_client_id,
        tenant=_clean(tenant) or "common",
        username=normalized_username,
        encrypted_token_bundle=encrypted,
        encryption_method=method,
        connected_at=connected_at or _now_iso(),
        last_test_ok=bool(last_test_ok),
    )


def save_ms_mail_account(
    account: MsMailAccount,
    *,
    approval_token: str,
    account_path: Path | str | None = None,
) -> MsMailAccountWriteResult:
    """Persist the encrypted MS mail account only after the hard token."""
    path = Path(account_path) if account_path is not None else get_ms_mail_account_path()
    if approval_token != MS_MAIL_ACCOUNT_SAVE_TOKEN:
        return MsMailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="Microsoft-Mail-Konto wurde nicht gespeichert: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(account), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return MsMailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="Microsoft-Mail-Konto wurde lokal verschluesselt gespeichert.",
        blocked_reasons=(),
        account=account,
    )


def load_ms_mail_account(account_path: Path | str | None = None) -> MsMailAccount | None:
    """Load the local MS mail account metadata if present."""
    path = Path(account_path) if account_path is not None else get_ms_mail_account_path()
    if not path.exists() or not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return MsMailAccount(**data)


def decrypt_ms_mail_token_bundle(
    account: MsMailAccount,
    *,
    unprotector: Callable[[str, str], bytes] | None = None,
) -> dict[str, Any]:
    """Decrypt a token bundle only for runtime Graph calls."""
    raw = (unprotector or unprotect_secret)(account.encrypted_token_bundle, account.encryption_method)
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict):
        raise ValueError("Microsoft OAuth-Token konnte nicht gelesen werden.")
    return parsed


def delete_ms_mail_account(
    *,
    approval_token: str,
    account_path: Path | str | None = None,
) -> MsMailAccountWriteResult:
    """Delete the local MS mail account only after the hard token."""
    path = Path(account_path) if account_path is not None else get_ms_mail_account_path()
    if approval_token != MS_MAIL_ACCOUNT_DELETE_TOKEN:
        return MsMailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="Microsoft-Mail-Konto wurde nicht geloescht: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    if path.exists() and path.is_file():
        path.unlink()
    return MsMailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="Microsoft-Mail-Konto wurde lokal geloescht.",
        blocked_reasons=(),
    )


def mask_username(username: str | None) -> str | None:
    """Mask an email-like username for UI status output."""
    clean = _clean(username)
    if not clean:
        return None
    if "@" not in clean:
        return clean[:1] + "***" if len(clean) > 1 else "***"
    local, domain = clean.split("@", 1)
    visible = local[:1] if local else "*"
    return f"{visible}***@{domain}"


def ms_mail_account_status(account_path: Path | str | None = None) -> dict[str, Any]:
    """Return token-free Microsoft mail account status."""
    account = load_ms_mail_account(account_path)
    if account is None:
        return {
            "connected": False,
            "username_masked": None,
            "tenant": None,
            "last_test_ok": False,
            "read_enabled": config.ENABLE_MS_MAIL_READ,
            "real_email_enabled": config.ENABLE_REAL_EMAIL,
            "scopes": list(MS_MAIL_SCOPES),
            "read_only": True,
        }
    return {
        "connected": True,
        "username_masked": mask_username(account.username),
        "tenant": account.tenant,
        "last_test_ok": account.last_test_ok,
        "connected_at": account.connected_at,
        "encryption_method": account.encryption_method,
        "read_enabled": config.ENABLE_MS_MAIL_READ,
        "real_email_enabled": config.ENABLE_REAL_EMAIL,
        "scopes": list(MS_MAIL_SCOPES),
        "read_only": True,
    }
