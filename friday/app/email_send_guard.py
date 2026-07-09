"""Guard real email sending behind local account, contact and token checks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from friday import config
from friday.app.email_account_store import EmailAccount, load_email_account
from friday.storage.database import get_connection, setup_local_database


EMAIL_SEND_TOKEN = "EMAIL SENDEN"


@dataclass(frozen=True)
class EmailSendGuardResult:
    """Decision for one possible real email send."""

    allowed: bool
    blocked_reasons: tuple[str, ...]
    recipient: str
    subject: str
    daily_limit: int
    sent_today_count: int
    account_connected: bool
    last_test_ok: bool
    recipient_is_contact: bool
    real_email_enabled: bool
    approval_token_required: str = EMAIL_SEND_TOKEN
    preview_only: bool = True
    external_send_enabled: bool = False


def _today_prefix() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def normalize_email(value: Any) -> str:
    return " ".join(str(value or "").strip().split()).lower()


def count_sent_emails_today(db_path: Path | str | None = None) -> int:
    """Count successful email sends for the current UTC day."""
    setup_local_database(db_path)
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM email_send_log
            WHERE status = 'sent' AND sent_at LIKE ?
            """,
            (f"{_today_prefix()}%",),
        ).fetchone()
        return int(row["count"] if row is not None else 0)


def log_email_send(
    *,
    recipient: str,
    subject: str,
    message_id: str | None,
    status: str,
    db_path: Path | str | None = None,
) -> None:
    """Persist one local send audit row."""
    setup_local_database(db_path)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO email_send_log (sent_at, recipient, subject, message_id, status)
            VALUES (:sent_at, :recipient, :subject, :message_id, :status)
            """,
            {
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "recipient": normalize_email(recipient),
                "subject": subject.strip() or "(ohne Betreff)",
                "message_id": message_id,
                "status": status.strip().lower() or "unknown",
            },
        )


def recipient_exists_in_contacts(recipient: str, db_path: Path | str | None = None) -> bool:
    """Return True only when recipient is stored on a local contact."""
    setup_local_database(db_path)
    normalized = normalize_email(recipient)
    if not normalized:
        return False
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM contacts
            WHERE LOWER(COALESCE(email_address, '')) = ?
            LIMIT 1
            """,
            (normalized,),
        ).fetchone()
        return row is not None


def check_email_send_allowed(
    *,
    recipient: str,
    subject: str,
    approval_token: str,
    account: EmailAccount | None = None,
    db_path: Path | str | None = None,
    account_path: Path | str | None = None,
    daily_limit: int | None = None,
) -> EmailSendGuardResult:
    """Check all conditions before a real email send may happen."""
    resolved_account = account or load_email_account(account_path)
    normalized_recipient = normalize_email(recipient)
    limit = daily_limit if daily_limit is not None else config.EMAIL_DAILY_SEND_LIMIT
    sent_today = count_sent_emails_today(db_path)
    is_contact = recipient_exists_in_contacts(normalized_recipient, db_path)
    blocked: list[str] = []

    if not config.ENABLE_REAL_EMAIL:
        blocked.append("real_email_disabled")
    if resolved_account is None:
        blocked.append("email_account_missing")
    elif not resolved_account.last_test_ok:
        blocked.append("email_account_test_not_ok")
    if approval_token != EMAIL_SEND_TOKEN:
        blocked.append("approval_token_invalid")
    if not is_contact:
        blocked.append("recipient_not_stored_contact")
    if sent_today >= limit:
        blocked.append("daily_limit_reached")
    if not normalized_recipient:
        blocked.append("recipient_missing")

    allowed = not blocked
    return EmailSendGuardResult(
        allowed=allowed,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        recipient=normalized_recipient,
        subject=subject.strip() or "(ohne Betreff)",
        daily_limit=limit,
        sent_today_count=sent_today,
        account_connected=resolved_account is not None,
        last_test_ok=bool(resolved_account and resolved_account.last_test_ok),
        recipient_is_contact=is_contact,
        real_email_enabled=config.ENABLE_REAL_EMAIL,
        external_send_enabled=allowed,
    )
