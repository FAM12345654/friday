"""Encrypted local Google Calendar account token storage."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

from friday import config
from friday.app.email_account_store import protect_secret, unprotect_secret


GOOGLE_CALENDAR_ACCOUNT_FILE_NAME = "google_calendar_account.json"
GOOGLE_CALENDAR_CONNECT_TOKEN = "KALENDER VERBINDEN"


@dataclass(frozen=True)
class GoogleCalendarAccount:
    """One locally stored Google Calendar OAuth token bundle."""

    calendar_id: str
    encrypted_credentials_json: str
    encryption_method: str
    connected_at: str
    last_test_ok: bool


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_google_calendar_account_path(base_dir: Path | str | None = None) -> Path:
    root = Path(base_dir) if base_dir is not None else config.LOCAL_DATA_DIR
    return root / "accounts" / GOOGLE_CALENDAR_ACCOUNT_FILE_NAME


def build_google_calendar_account(
    *,
    calendar_id: str,
    credentials_json: str | dict[str, Any],
    last_test_ok: bool = False,
) -> GoogleCalendarAccount:
    """Build an encrypted Google Calendar account object."""
    clean_calendar_id = " ".join(str(calendar_id or "primary").strip().split()) or "primary"
    raw_json = json.dumps(credentials_json, ensure_ascii=False, sort_keys=True) if isinstance(credentials_json, dict) else str(credentials_json)
    encrypted, method = protect_secret(raw_json.encode("utf-8"))
    return GoogleCalendarAccount(
        calendar_id=clean_calendar_id,
        encrypted_credentials_json=encrypted,
        encryption_method=method,
        connected_at=_now_iso(),
        last_test_ok=bool(last_test_ok),
    )


def decrypt_google_calendar_credentials(account: GoogleCalendarAccount) -> dict[str, Any]:
    """Decrypt the stored OAuth credentials JSON for runtime use only."""
    raw = unprotect_secret(
        account.encrypted_credentials_json,
        account.encryption_method,
    ).decode("utf-8")
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Google-Kalender-Credentials sind ungueltig.")
    return parsed


def google_calendar_account_fingerprint(account: GoogleCalendarAccount) -> str:
    """Return a non-secret binding for approvals targeting this exact account snapshot."""
    material = "\0".join(
        (
            account.calendar_id,
            account.encryption_method,
            account.encrypted_credentials_json,
            account.connected_at,
        )
    ).encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def save_google_calendar_account(
    account: GoogleCalendarAccount,
    *,
    approval_token: str,
    account_path: Path | str | None = None,
) -> dict[str, Any]:
    """Persist encrypted Google Calendar credentials only after the hard token."""
    path = Path(account_path) if account_path is not None else get_google_calendar_account_path()
    if approval_token != GOOGLE_CALENDAR_CONNECT_TOKEN:
        return {
            "allowed": False,
            "persisted": False,
            "message": "Google-Kalender wurde nicht gespeichert: Token fehlt.",
            "blocked_reasons": ("approval_token_invalid",),
        }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(account), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "allowed": True,
        "persisted": True,
        "message": "Google-Kalender-Konto wurde lokal verschluesselt gespeichert.",
        "blocked_reasons": (),
    }


def load_google_calendar_account(
    account_path: Path | str | None = None,
) -> GoogleCalendarAccount | None:
    """Load the encrypted Google Calendar account if it exists."""
    path = Path(account_path) if account_path is not None else get_google_calendar_account_path()
    if not path.exists() or not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return GoogleCalendarAccount(**data)


def google_calendar_account_status(account_path: Path | str | None = None) -> dict[str, Any]:
    """Return password/token-free Google Calendar connection status."""
    account = load_google_calendar_account(account_path)
    if account is None:
        return {
            "connected": False,
            "calendar_id": None,
            "last_test_ok": False,
            "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
        }
    return {
        "connected": True,
        "calendar_id": account.calendar_id,
        "account_fingerprint": google_calendar_account_fingerprint(account),
        "connected_at": account.connected_at,
        "last_test_ok": account.last_test_ok,
        "encryption_method": account.encryption_method,
        "real_calendar_enabled": config.ENABLE_REAL_CALENDAR,
    }
