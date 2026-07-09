"""Encrypted local Outlook ICS account URL storage."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from friday import config
from friday.app.account_policy_store import POLICY_SAVE_TOKEN
from friday.app.email_account_store import protect_secret, unprotect_secret


OUTLOOK_ICS_ACCOUNT_FILE_NAME = "outlook_ics_accounts.json"


@dataclass(frozen=True)
class OutlookIcsAccount:
    """One locally stored encrypted Outlook ICS URL for an account policy."""

    policy_id: int
    encrypted_ics_url: str
    encryption_method: str
    saved_at: str
    last_test_ok: bool = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_outlook_ics_account_path(base_dir: Path | str | None = None) -> Path:
    root = Path(base_dir) if base_dir is not None else config.LOCAL_DATA_DIR
    return root / "accounts" / OUTLOOK_ICS_ACCOUNT_FILE_NAME


def build_outlook_ics_account(
    *,
    policy_id: int,
    ics_url: str,
    last_test_ok: bool = False,
) -> OutlookIcsAccount:
    """Build an encrypted Outlook ICS account object without exposing the URL."""
    clean_url = str(ics_url or "").strip()
    if not clean_url:
        raise ValueError("Outlook-ICS-URL fehlt.")
    encrypted, method = protect_secret(clean_url.encode("utf-8"))
    return OutlookIcsAccount(
        policy_id=int(policy_id),
        encrypted_ics_url=encrypted,
        encryption_method=method,
        saved_at=_now_iso(),
        last_test_ok=bool(last_test_ok),
    )


def _load_all(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def save_outlook_ics_account(
    account: OutlookIcsAccount,
    *,
    approval_token: str,
    account_path: Path | str | None = None,
) -> dict[str, Any]:
    """Persist an encrypted ICS URL only after the hard policy token."""
    path = Path(account_path) if account_path is not None else get_outlook_ics_account_path()
    if approval_token != POLICY_SAVE_TOKEN:
        return {
            "allowed": False,
            "persisted": False,
            "message": "Outlook-ICS-Quelle wurde nicht gespeichert: Token fehlt.",
            "blocked_reasons": ("approval_token_invalid",),
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _load_all(path)
    data[str(account.policy_id)] = asdict(account)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "allowed": True,
        "persisted": True,
        "message": "Outlook-ICS-Quelle wurde lokal verschluesselt gespeichert.",
        "blocked_reasons": (),
    }


def load_outlook_ics_account(
    policy_id: int,
    account_path: Path | str | None = None,
) -> OutlookIcsAccount | None:
    """Load one encrypted Outlook ICS account by policy id."""
    path = Path(account_path) if account_path is not None else get_outlook_ics_account_path()
    data = _load_all(path)
    raw = data.get(str(int(policy_id)))
    if not isinstance(raw, dict):
        return None
    return OutlookIcsAccount(**raw)


def decrypt_outlook_ics_url(account: OutlookIcsAccount) -> str:
    """Decrypt the stored ICS URL for runtime use only."""
    return unprotect_secret(
        account.encrypted_ics_url,
        account.encryption_method,
    ).decode("utf-8")


def outlook_ics_account_status(
    policy_id: int,
    account_path: Path | str | None = None,
) -> dict[str, Any]:
    """Return URL-free Outlook ICS connection status."""
    account = load_outlook_ics_account(policy_id, account_path)
    if account is None:
        return {
            "connected": False,
            "policy_id": int(policy_id),
            "last_test_ok": False,
            "provider": "outlook_ics",
        }
    return {
        "connected": True,
        "policy_id": account.policy_id,
        "saved_at": account.saved_at,
        "last_test_ok": account.last_test_ok,
        "encryption_method": account.encryption_method,
        "provider": "outlook_ics",
    }
