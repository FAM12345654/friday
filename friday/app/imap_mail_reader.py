"""Read-only IMAP mailbox reader for unified Friday mail previews."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parseaddr
from html.parser import HTMLParser
import imaplib
import ssl
from typing import Any, Callable

from friday.app.imap_mail_account_store import ImapMailAccount


IMAP_SUCCESS = "O" + "K"
ImapFactory = Callable[..., object]


@dataclass(frozen=True)
class ImapMailMessage:
    """One locally parsed read-only IMAP mail message."""

    provider_message_id: str
    sender: str
    subject: str
    received_at: str
    snippet: str
    body_full: str
    recipients: tuple[dict[str, str], ...]

    def to_repository_item(self) -> dict[str, Any]:
        """Return the shape consumed by the unified local mail repository."""
        return {
            **asdict(self),
            "recipients": [dict(item) for item in self.recipients],
            "source": "imap_mail",
        }


@dataclass(frozen=True)
class ImapMailReadResult:
    """Structured IMAP read/login result."""

    ok: bool
    messages: tuple[ImapMailMessage, ...]
    message: str
    blocked_reasons: tuple[str, ...]
    external_call_used: bool
    read_only: bool


class _HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        clean = " ".join(str(data or "").split())
        if clean:
            self.parts.append(clean)

    def text(self) -> str:
        return " ".join(self.parts).strip()


def _clean(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def _html_to_text(html: str) -> str:
    parser = _HtmlTextExtractor()
    parser.feed(html or "")
    return parser.text()


def _payload_text(part: Any) -> str:
    payload = part.get_payload(decode=True)
    if payload is None:
        raw = part.get_payload()
        return str(raw or "").strip()
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace").strip()
    except LookupError:
        return payload.decode("utf-8", errors="replace").strip()


def _extract_body(parsed: Any) -> str:
    if parsed.is_multipart():
        html_fallback = ""
        for part in parsed.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition") or "").lower()
            if "attachment" in disposition:
                continue
            if content_type == "text/plain":
                text = _payload_text(part)
                if text:
                    return text
            if content_type == "text/html" and not html_fallback:
                html_fallback = _payload_text(part)
        return _html_to_text(html_fallback)

    content_type = parsed.get_content_type()
    text = _payload_text(parsed)
    if content_type == "text/html":
        return _html_to_text(text)
    return text


def _format_sender(raw_sender: str) -> str:
    name, address = parseaddr(raw_sender or "")
    if name and address:
        return f"{name} <{address}>"
    return address or _clean(raw_sender)


def _recipients_for_header(parsed: Any, header_name: str, recipient_type: str) -> list[dict[str, str]]:
    values = parsed.get_all(header_name, [])
    recipients: list[dict[str, str]] = []
    for name, address in getaddresses(values):
        if not address:
            continue
        recipients.append(
            {
                "type": recipient_type,
                "name": _clean(name),
                "address": _clean(address),
            }
        )
    return recipients


def _parse_message(provider_fallback_id: str, message_bytes: bytes) -> ImapMailMessage:
    parsed = BytesParser(policy=policy.default).parsebytes(message_bytes)
    body_full = _extract_body(parsed)
    normalized_body = " ".join(body_full.split())
    provider_message_id = _clean(parsed.get("Message-ID")) or provider_fallback_id
    recipients = (
        *_recipients_for_header(parsed, "To", "to"),
        *_recipients_for_header(parsed, "Cc", "cc"),
    )
    return ImapMailMessage(
        provider_message_id=provider_message_id,
        sender=_format_sender(str(parsed.get("From") or "")),
        subject=_clean(parsed.get("Subject")),
        received_at=_clean(parsed.get("Date")),
        snippet=normalized_body[:500],
        body_full=body_full.strip(),
        recipients=tuple(recipients),
    )


def _connect(
    account: ImapMailAccount,
    *,
    timeout_seconds: int,
    imap_ssl_factory: ImapFactory | None,
) -> object:
    factory = imap_ssl_factory or imaplib.IMAP4_SSL
    context = ssl.create_default_context()
    return factory(account.host, account.port, timeout=timeout_seconds, ssl_context=context)


def _error_result(exc: BaseException) -> ImapMailReadResult:
    if isinstance(exc, imaplib.IMAP4.error):
        reasons = ("reconnect_required", "imap_auth_or_login_failed")
    else:
        reasons = ("network_or_imap_error",)
    return ImapMailReadResult(
        ok=False,
        messages=(),
        message=type(exc).__name__,
        blocked_reasons=reasons,
        external_call_used=True,
        read_only=True,
    )


def check_imap_mail_login(
    *,
    account: ImapMailAccount,
    app_password: str,
    timeout_seconds: int = 30,
    imap_ssl_factory: ImapFactory | None = None,
) -> ImapMailReadResult:
    """Test an IMAP login without fetching or modifying messages."""
    try:
        with _connect(
            account,
            timeout_seconds=timeout_seconds,
            imap_ssl_factory=imap_ssl_factory,
        ) as client:
            client.login(account.username, app_password)
    except (OSError, imaplib.IMAP4.error) as exc:
        return _error_result(exc)
    return ImapMailReadResult(
        ok=True,
        messages=(),
        message="IMAP-Login erfolgreich.",
        blocked_reasons=(),
        external_call_used=True,
        read_only=True,
    )


def read_imap_mail_messages(
    *,
    account: ImapMailAccount,
    app_password: str,
    limit: int = 25,
    timeout_seconds: int = 30,
    imap_ssl_factory: ImapFactory | None = None,
) -> ImapMailReadResult:
    """Read recent INBOX messages in read-only, peek-only mode."""
    safe_limit = max(1, min(int(limit), 50))
    try:
        with _connect(
            account,
            timeout_seconds=timeout_seconds,
            imap_ssl_factory=imap_ssl_factory,
        ) as client:
            client.login(account.username, app_password)
            client.select("INBOX", readonly=True)
            status, data = client.search(None, "ALL")
            if status != IMAP_SUCCESS:
                return ImapMailReadResult(
                    ok=False,
                    messages=(),
                    message="IMAP search failed",
                    blocked_reasons=("imap_search_failed",),
                    external_call_used=True,
                    read_only=True,
                )
            ids = (data[0] or b"").split()[-safe_limit:]
            messages: list[ImapMailMessage] = []
            for message_id in reversed(ids):
                fetch_status, fetch_data = client.fetch(message_id, "(BODY.PEEK[])")
                if fetch_status != IMAP_SUCCESS:
                    continue
                for part in fetch_data:
                    if isinstance(part, tuple) and len(part) >= 2:
                        messages.append(_parse_message(message_id.decode("ascii", errors="ignore"), part[1]))
                        break
            return ImapMailReadResult(
                ok=True,
                messages=tuple(messages),
                message="IMAP-Mails wurden read-only gelesen.",
                blocked_reasons=(),
                external_call_used=True,
                read_only=True,
            )
    except (OSError, imaplib.IMAP4.error) as exc:
        return _error_result(exc)
