"""Read-only IMAP inbox preview for Friday email accounts."""

from __future__ import annotations

from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
import imaplib
import ssl
from typing import Callable

from friday.app.email_account_store import EmailAccount


@dataclass(frozen=True)
class EmailInboxPreviewItem:
    """One read-only inbox preview item."""

    sender: str
    subject: str
    date: str
    text_preview: str


@dataclass(frozen=True)
class EmailInboxPreviewResult:
    """Structured IMAP preview result."""

    ok: bool
    items: tuple[EmailInboxPreviewItem, ...]
    error: str | None
    external_call_used: bool
    read_only: bool


ImapFactory = Callable[..., object]
IMAP_SUCCESS = "".join(("O", "K"))


def _extract_text(message_bytes: bytes) -> str:
    parsed = BytesParser(policy=policy.default).parsebytes(message_bytes)
    if parsed.is_multipart():
        for part in parsed.walk():
            if part.get_content_type() == "text/plain":
                return str(part.get_content() or "")
        return ""
    return str(parsed.get_content() or "")


def _preview_item(message_bytes: bytes) -> EmailInboxPreviewItem:
    parsed = BytesParser(policy=policy.default).parsebytes(message_bytes)
    text = " ".join(_extract_text(message_bytes).split())[:500]
    return EmailInboxPreviewItem(
        sender=str(parsed.get("From", "")),
        subject=str(parsed.get("Subject", "")),
        date=str(parsed.get("Date", "")),
        text_preview=text,
    )


def read_recent_inbox_emails(
    *,
    account: EmailAccount,
    app_password: str,
    limit: int = 10,
    timeout_seconds: int = 30,
    imap_ssl_factory: ImapFactory | None = None,
) -> EmailInboxPreviewResult:
    """Read recent INBOX messages in peek/read-only mode."""
    if limit < 1:
        limit = 1
    if limit > 50:
        limit = 50
    factory = imap_ssl_factory or imaplib.IMAP4_SSL
    context = ssl.create_default_context()
    try:
        with factory(account.imap_host, account.imap_port, timeout=timeout_seconds, ssl_context=context) as client:
            client.login(account.username, app_password)
            client.select("INBOX", readonly=True)
            status, data = client.search(None, "ALL")
            if status != IMAP_SUCCESS:
                return EmailInboxPreviewResult(False, (), "IMAP search failed", True, True)
            ids = (data[0] or b"").split()[-limit:]
            items: list[EmailInboxPreviewItem] = []
            for message_id in reversed(ids):
                fetch_status, fetch_data = client.fetch(message_id, "(BODY.PEEK[])")
                if fetch_status != IMAP_SUCCESS:
                    continue
                for part in fetch_data:
                    if isinstance(part, tuple) and len(part) >= 2:
                        items.append(_preview_item(part[1]))
                        break
            return EmailInboxPreviewResult(True, tuple(items), None, True, True)
    except (OSError, imaplib.IMAP4.error) as exc:
        return EmailInboxPreviewResult(False, (), type(exc).__name__, True, True)


def check_imap_login(
    *,
    account: EmailAccount,
    app_password: str,
    timeout_seconds: int = 30,
    imap_ssl_factory: ImapFactory | None = None,
) -> EmailInboxPreviewResult:
    """Test IMAP login without fetching or modifying messages."""
    factory = imap_ssl_factory or imaplib.IMAP4_SSL
    context = ssl.create_default_context()
    try:
        with factory(account.imap_host, account.imap_port, timeout=timeout_seconds, ssl_context=context) as client:
            client.login(account.username, app_password)
    except (OSError, imaplib.IMAP4.error) as exc:
        return EmailInboxPreviewResult(False, (), type(exc).__name__, True, True)
    return EmailInboxPreviewResult(True, (), None, True, True)
