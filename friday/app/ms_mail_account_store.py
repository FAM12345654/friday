"""Guarded encrypted multi-account store for read-only Microsoft Graph mail."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Callable

from friday import config
from friday.app.email_account_store import protect_secret, unprotect_secret
from friday.app.ms_mail_provider import MS_MAIL_SCOPES


MS_MAIL_ACCOUNT_SAVE_TOKEN = "KONTO SPEICHERN"
MS_MAIL_ACCOUNT_DELETE_TOKEN = "KONTO LOESCHEN"
MS_MAIL_ACCOUNT_FILE_NAME = "ms_mail_account.json"
MS_MAIL_ACCOUNTS_DIR_NAME = "ms_mail_accounts"


@dataclass(frozen=True)
class MsMailAccount:
    """Encrypted local Microsoft Graph token bundle metadata."""

    account_id: str
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


def normalize_ms_mail_account_id(username: str | None) -> str:
    """Return a stable filesystem-safe account id from a mailbox username."""
    base = _clean(username).lower()
    safe = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
    return (safe or "ms_mail_account")[:80]


def get_ms_mail_account_path(base_dir: Path | str | None = None) -> Path:
    """Return the legacy single-account path."""
    root = Path(base_dir) if base_dir is not None else config.LOCAL_DATA_DIR
    return root / "accounts" / MS_MAIL_ACCOUNT_FILE_NAME


def get_ms_mail_accounts_dir(base_dir: Path | str | None = None) -> Path:
    """Return the multi-account directory for encrypted MS mail accounts."""
    root = Path(base_dir) if base_dir is not None else config.LOCAL_DATA_DIR
    return root / "accounts" / MS_MAIL_ACCOUNTS_DIR_NAME


def get_ms_mail_multi_account_path(
    account_id: str,
    *,
    base_dir: Path | str | None = None,
    accounts_dir: Path | str | None = None,
) -> Path:
    """Return the encrypted account file path for one account id."""
    normalized = normalize_ms_mail_account_id(account_id)
    root = Path(accounts_dir) if accounts_dir is not None else get_ms_mail_accounts_dir(base_dir)
    return root / f"{normalized}.json"


def _account_from_mapping(data: dict[str, Any]) -> MsMailAccount:
    username = _clean(data.get("username"))
    account_id = _clean(data.get("account_id")) or normalize_ms_mail_account_id(username)
    return MsMailAccount(
        account_id=account_id,
        client_id=_clean(data.get("client_id")),
        tenant=_clean(data.get("tenant")) or "common",
        username=username,
        encrypted_token_bundle=str(data.get("encrypted_token_bundle") or ""),
        encryption_method=str(data.get("encryption_method") or ""),
        connected_at=str(data.get("connected_at") or ""),
        last_test_ok=bool(data.get("last_test_ok")),
    )


def _load_account_file(path: Path) -> MsMailAccount | None:
    if not path.exists() or not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Microsoft-Mail-Konto konnte nicht gelesen werden.")
    return _account_from_mapping(data)


def _write_account_file(path: Path, account: MsMailAccount) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(account), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def migrate_legacy_ms_mail_account(
    *,
    legacy_path: Path | str | None = None,
    accounts_dir: Path | str | None = None,
) -> MsMailAccount | None:
    """Copy the old single account into the multi-account store idempotently.

    The legacy file is deliberately kept in place so the existing live token is never lost.
    """
    source = Path(legacy_path) if legacy_path is not None else get_ms_mail_account_path()
    legacy = _load_account_file(source)
    if legacy is None:
        return None
    target = get_ms_mail_multi_account_path(legacy.account_id, accounts_dir=accounts_dir)
    if not target.exists():
        _write_account_file(target, legacy)
    return legacy


def build_ms_mail_account(
    *,
    client_id: str,
    tenant: str | None,
    username: str,
    token_bundle: dict[str, Any],
    account_id: str | None = None,
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
    normalized_account_id = normalize_ms_mail_account_id(account_id or normalized_username)
    return MsMailAccount(
        account_id=normalized_account_id,
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
    accounts_dir: Path | str | None = None,
) -> MsMailAccountWriteResult:
    """Persist one encrypted MS mail account only after the hard token."""
    path = (
        Path(account_path)
        if account_path is not None
        else get_ms_mail_multi_account_path(account.account_id, accounts_dir=accounts_dir)
    )
    if approval_token != MS_MAIL_ACCOUNT_SAVE_TOKEN:
        return MsMailAccountWriteResult(
            allowed=False,
            persisted=False,
            account_path=str(path),
            message="Microsoft-Mail-Konto wurde nicht gespeichert: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    _write_account_file(path, account)
    return MsMailAccountWriteResult(
        allowed=True,
        persisted=True,
        account_path=str(path),
        message="Microsoft-Mail-Konto wurde lokal verschluesselt gespeichert.",
        blocked_reasons=(),
        account=account,
    )


def list_ms_mail_accounts(
    *,
    base_dir: Path | str | None = None,
    accounts_dir: Path | str | None = None,
    migrate_legacy: bool = True,
) -> tuple[MsMailAccount, ...]:
    """Load all encrypted MS mail accounts, migrating the legacy account if present."""
    root = Path(accounts_dir) if accounts_dir is not None else get_ms_mail_accounts_dir(base_dir)
    legacy_path = get_ms_mail_account_path(base_dir)
    if migrate_legacy:
        migrate_legacy_ms_mail_account(legacy_path=legacy_path, accounts_dir=root)
    if not root.exists() or not root.is_dir():
        return ()
    accounts: list[MsMailAccount] = []
    for path in sorted(root.glob("*.json")):
        account = _load_account_file(path)
        if account is not None:
            accounts.append(account)
    return tuple(accounts)


def load_ms_mail_account(
    account_path: Path | str | None = None,
    *,
    account_id: str | None = None,
    base_dir: Path | str | None = None,
    accounts_dir: Path | str | None = None,
) -> MsMailAccount | None:
    """Load one local MS mail account metadata if present.

    Passing account_path keeps backwards compatibility with the old single-account tests.
    Without arguments, the first multi-account entry is returned for legacy callers.
    """
    if account_path is not None:
        return _load_account_file(Path(account_path))
    if account_id:
        return _load_account_file(
            get_ms_mail_multi_account_path(account_id, base_dir=base_dir, accounts_dir=accounts_dir)
        )
    accounts = list_ms_mail_accounts(base_dir=base_dir, accounts_dir=accounts_dir)
    return accounts[0] if accounts else None


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
    account_id: str | None = None,
    accounts_dir: Path | str | None = None,
) -> MsMailAccountWriteResult:
    """Delete one local MS mail account only after the hard token."""
    if account_path is not None:
        path = Path(account_path)
    elif account_id:
        path = get_ms_mail_multi_account_path(account_id, accounts_dir=accounts_dir)
    else:
        accounts = list_ms_mail_accounts(accounts_dir=accounts_dir)
        if len(accounts) != 1:
            return MsMailAccountWriteResult(
                allowed=False,
                persisted=False,
                account_path=str(get_ms_mail_accounts_dir() if accounts_dir is None else accounts_dir),
                message="Microsoft-Mail-Konto wurde nicht geloescht: Konto-ID fehlt.",
                blocked_reasons=("account_id_required",),
            )
        path = get_ms_mail_multi_account_path(accounts[0].account_id, accounts_dir=accounts_dir)

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


def _account_status_payload(account: MsMailAccount) -> dict[str, Any]:
    return {
        "id": account.account_id,
        "account_id": account.account_id,
        "username_masked": mask_username(account.username),
        "username": account.username,
        "tenant": account.tenant,
        "last_test_ok": account.last_test_ok,
        "connected_at": account.connected_at,
        "encryption_method": account.encryption_method,
        "read_only": True,
    }


def ms_mail_account_status(account_path: Path | str | None = None) -> dict[str, Any]:
    """Return token-free Microsoft mail account status."""
    if account_path is not None:
        account = load_ms_mail_account(account_path)
        accounts = (account,) if account is not None else ()
    else:
        accounts = list_ms_mail_accounts()
        account = accounts[0] if accounts else None

    account_payloads = [_account_status_payload(item) for item in accounts]
    connected = bool(accounts)
    return {
        "connected": connected,
        "account_count": len(accounts),
        "accounts": account_payloads,
        "username_masked": mask_username(account.username) if account else None,
        "tenant": account.tenant if account else None,
        "last_test_ok": any(item.last_test_ok for item in accounts),
        "connected_at": account.connected_at if account else None,
        "encryption_method": account.encryption_method if account else None,
        "read_enabled": config.ENABLE_MS_MAIL_READ,
        "real_email_enabled": config.ENABLE_REAL_EMAIL,
        "scopes": list(MS_MAIL_SCOPES),
        "read_only": True,
    }
