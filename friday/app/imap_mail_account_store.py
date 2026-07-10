"""Guarded encrypted multi-account store for read-only IMAP mail."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Callable

from friday import config
from friday.app.email_account_store import protect_secret, unprotect_secret


IMAP_MAIL_ACCOUNT_SAVE_TOKEN = "KONTO SPEICHERN"
IMAP_MAIL_ACCOUNT_DELETE_TOKEN = "KONTO LOESCHEN"
IMAP_MAIL_ACCOUNTS_DIR_NAME = "imap_mail_accounts"
GMAIL_IMAP_HOST = "imap.gmail.com"
GMAIL_IMAP_PORT = 993


@dataclass(frozen=True)
class ImapMailAccount:
    """Encrypted local read-only IMAP account metadata."""

    account_id: str
    provider: str
    host: str
    port: int
    username: str
    encrypted_app_password: str
    encryption_method: str
    connected_at: str
    last_test_ok: bool


@dataclass(frozen=True)
class ImapMailAccountWriteResult:
    """Result of a guarded IMAP mail account write/delete."""

    allowed: bool
    persisted: bool
    account_path: str
    message: str
    blocked_reasons: tuple[str, ...]
    account: ImapMailAccount | None = None
    plaintext_password_persisted: bool = False
    preview_only: bool = False
    external_call_used: bool = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def normalize_imap_mail_account_id(username: str | None, provider: str | None = "gmail") -> str:
    """Return a stable filesystem-safe account id for one read-only IMAP mailbox."""
    normalized_provider = re.sub(r"[^a-z0-9]+", "_", _clean(provider).lower()).strip("_") or "imap"
    normalized_username = re.sub(r"[^a-z0-9]+", "_", _clean(username).lower()).strip("_")
    return f"{normalized_provider}_{normalized_username or 'mail_account'}"[:100]


def _safe_account_file_stem(account_id: str | None) -> str:
    """Return a filesystem-safe file stem without changing the logical account id."""
    return re.sub(r"[^a-z0-9_]+", "_", _clean(account_id).lower()).strip("_") or "imap_mail_account"


def get_imap_mail_accounts_dir(base_dir: Path | str | None = None) -> Path:
    """Return the multi-account directory for encrypted read-only IMAP accounts."""
    root = Path(base_dir) if base_dir is not None else config.LOCAL_DATA_DIR
    return root / "accounts" / IMAP_MAIL_ACCOUNTS_DIR_NAME


def get_imap_mail_account_path(
    account_id: str,
    *,
    base_dir: Path | str | None = None,
    accounts_dir: Path | str | None = None,
) -> Path:
    """Return the encrypted account file path for one IMAP account id."""
    root = Path(accounts_dir) if accounts_dir is not None else get_imap_mail_accounts_dir(base_dir)
    return root / f"{_safe_account_file_stem(account_id)}.json"


def _account_from_mapping(data: dict[str, Any]) -> ImapMailAccount:
    provider = _clean(data.get("provider")) or "gmail"
    username = _clean(data.get("username"))
    account_id = _clean(data.get("account_id")) or normalize_imap_mail_account_id(username, provider)
    return ImapMailAccount(
        account_id=account_id,
        provider=provider,
        host=_clean(data.get("host")) or GMAIL_IMAP_HOST,
        port=int(data.get("port") or GMAIL_IMAP_PORT),
        username=username,
        encrypted_app_password=str(data.get("encrypted_app_password") or ""),
        encryption_method=str(data.get("encryption_method") or ""),
        connected_at=str(data.get("connected_at") or ""),
        last_test_ok=bool(data.get("last_test_ok")),
    )


def _load_account_file(path: Path) -> ImapMailAccount | None:
    if not path.exists() or not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("IMAP-Mail-Konto konnte nicht gelesen werden.")
    return _account_from_mapping(data)


def _write_account_file(path: Path, account: ImapMailAccount) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(account), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_imap_mail_account(
    *,
    username: str,
    app_password: str,
    provider: str | None = "gmail",
    host: str | None = GMAIL_IMAP_HOST,
    port: int | None = GMAIL_IMAP_PORT,
    account_id: str | None = None,
    last_test_ok: bool = False,
    protector: Callable[[bytes], tuple[str, str]] | None = None,
    connected_at: str | None = None,
) -> ImapMailAccount:
    """Build an encrypted read-only IMAP account from a plain runtime app password."""
    normalized_username = _clean(username)
    if not normalized_username or "@" not in normalized_username:
        raise ValueError("Ein IMAP-Benutzername als E-Mail-Adresse ist erforderlich.")
    if not str(app_password or "").strip():
        raise ValueError("Ein IMAP-App-Passwort ist erforderlich.")
    normalized_provider = _clean(provider).lower() or "gmail"
    normalized_host = _clean(host) or GMAIL_IMAP_HOST
    normalized_port = int(port or GMAIL_IMAP_PORT)
    encrypted, method = (protector or protect_secret)(str(app_password).encode("utf-8"))
    normalized_account_id = (
        _safe_account_file_stem(account_id)
        if account_id
        else normalize_imap_mail_account_id(normalized_username, normalized_provider)
    )
    return ImapMailAccount(
        account_id=normalized_account_id,
        provider=normalized_provider,
        host=normalized_host,
        port=normalized_port,
        username=normalized_username,
        encrypted_app_password=encrypted,
        encryption_method=method,
        connected_at=connected_at or _now_iso(),
        last_test_ok=bool(last_test_ok),
    )


def save_imap_mail_account(
    account: ImapMailAccount,
    *,
    approval_token: str,
    account_path: Path | str | None = None,
    accounts_dir: Path | str | None = None,
) -> ImapMailAccountWriteResult:
    """Persist one encrypted IMAP mail account only after the hard token."""
    path = (
        Path(account_path)
        if account_path is not None
        else get_imap_mail_account_path(account.account_id, accounts_dir=accounts_dir)
    )
    if approval_token != IMAP_MAIL_ACCOUNT_SAVE_TOKEN:
        return ImapMailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="IMAP-Mail-Konto wurde nicht gespeichert: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    _write_account_file(path, account)
    return ImapMailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="IMAP-Mail-Konto wurde lokal verschluesselt gespeichert.",
        blocked_reasons=(),
        account=account,
    )


def list_imap_mail_accounts(
    *,
    base_dir: Path | str | None = None,
    accounts_dir: Path | str | None = None,
) -> tuple[ImapMailAccount, ...]:
    """Load all encrypted read-only IMAP accounts."""
    root = Path(accounts_dir) if accounts_dir is not None else get_imap_mail_accounts_dir(base_dir)
    if not root.exists() or not root.is_dir():
        return ()
    accounts: list[ImapMailAccount] = []
    for path in sorted(root.glob("*.json")):
        account = _load_account_file(path)
        if account is not None:
            accounts.append(account)
    return tuple(accounts)


def load_imap_mail_account(
    account_path: Path | str | None = None,
    *,
    account_id: str | None = None,
    base_dir: Path | str | None = None,
    accounts_dir: Path | str | None = None,
) -> ImapMailAccount | None:
    """Load one local IMAP mail account metadata if present."""
    if account_path is not None:
        return _load_account_file(Path(account_path))
    if account_id:
        return _load_account_file(
            get_imap_mail_account_path(account_id, base_dir=base_dir, accounts_dir=accounts_dir)
        )
    accounts = list_imap_mail_accounts(base_dir=base_dir, accounts_dir=accounts_dir)
    return accounts[0] if accounts else None


def decrypt_imap_mail_app_password(
    account: ImapMailAccount,
    *,
    unprotector: Callable[[str, str], bytes] | None = None,
) -> str:
    """Decrypt the stored IMAP app password only for runtime login."""
    raw = (unprotector or unprotect_secret)(account.encrypted_app_password, account.encryption_method)
    return raw.decode("utf-8")


def delete_imap_mail_account(
    *,
    approval_token: str,
    account_path: Path | str | None = None,
    account_id: str | None = None,
    accounts_dir: Path | str | None = None,
) -> ImapMailAccountWriteResult:
    """Delete one local IMAP mail account only after the hard token."""
    if account_path is not None:
        path = Path(account_path)
    elif account_id:
        path = get_imap_mail_account_path(account_id, accounts_dir=accounts_dir)
    else:
        accounts = list_imap_mail_accounts(accounts_dir=accounts_dir)
        if len(accounts) != 1:
            return ImapMailAccountWriteResult(
                allowed=False,
                persisted=False,
                account_path=str(get_imap_mail_accounts_dir() if accounts_dir is None else accounts_dir),
                message="IMAP-Mail-Konto wurde nicht geloescht: Konto-ID fehlt.",
                blocked_reasons=("account_id_required",),
            )
        path = get_imap_mail_account_path(accounts[0].account_id, accounts_dir=accounts_dir)

    if approval_token != IMAP_MAIL_ACCOUNT_DELETE_TOKEN:
        return ImapMailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="IMAP-Mail-Konto wurde nicht geloescht: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    if path.exists() and path.is_file():
        path.unlink()
    return ImapMailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="IMAP-Mail-Konto wurde lokal geloescht.",
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


def _account_status_payload(account: ImapMailAccount) -> dict[str, Any]:
    return {
        "id": account.account_id,
        "account_id": account.account_id,
        "provider": account.provider,
        "host": account.host,
        "port": account.port,
        "username_masked": mask_username(account.username),
        "username": account.username,
        "last_test_ok": account.last_test_ok,
        "connected_at": account.connected_at,
        "encryption_method": account.encryption_method,
        "read_only": True,
    }


def imap_mail_account_status(accounts_dir: Path | str | None = None) -> dict[str, Any]:
    """Return password-free read-only IMAP mail account status."""
    accounts = list_imap_mail_accounts(accounts_dir=accounts_dir)
    account = accounts[0] if accounts else None
    return {
        "connected": bool(accounts),
        "account_count": len(accounts),
        "accounts": [_account_status_payload(item) for item in accounts],
        "username_masked": mask_username(account.username) if account else None,
        "last_test_ok": any(item.last_test_ok for item in accounts),
        "connected_at": account.connected_at if account else None,
        "encryption_method": account.encryption_method if account else None,
        "read_enabled": config.ENABLE_IMAP_MAIL_READ,
        "real_email_enabled": config.ENABLE_REAL_EMAIL,
        "read_only": True,
    }
