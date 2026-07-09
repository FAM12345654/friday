"""Guarded SMTP sender for exactly one email message."""

from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
import smtplib
import ssl
from typing import Callable

from friday.app.email_account_store import EmailAccount


@dataclass(frozen=True)
class EmailSmtpSendResult:
    """Structured SMTP send result without exposing credentials."""

    ok: bool
    message_id: str | None
    error: str | None
    external_call_used: bool
    sent: bool


SmtpFactory = Callable[..., object]


def _message_id(email_message: EmailMessage) -> str:
    return str(email_message["Message-ID"] or "")


def build_email_message(
    *,
    account: EmailAccount,
    recipient: str,
    subject: str,
    body: str,
) -> EmailMessage:
    """Build a UTF-8 single-recipient email message."""
    if "," in recipient or ";" in recipient:
        raise ValueError("Nur ein Empfaenger ist erlaubt.")
    message = EmailMessage()
    message["From"] = account.email_address
    message["To"] = recipient.strip()
    message["Subject"] = (subject or "").strip() or "(ohne Betreff)"
    message.set_content(body or "", subtype="plain", charset="utf-8")
    return message


def send_single_email(
    *,
    account: EmailAccount,
    app_password: str,
    recipient: str,
    subject: str,
    body: str,
    timeout_seconds: int = 30,
    smtp_ssl_factory: SmtpFactory | None = None,
    smtp_starttls_factory: SmtpFactory | None = None,
) -> EmailSmtpSendResult:
    """Send exactly one email with TLS and no attachments/CC/BCC."""
    if timeout_seconds > 30:
        return EmailSmtpSendResult(False, None, "Timeout darf hoechstens 30 Sekunden sein.", False, False)
    message = build_email_message(
        account=account,
        recipient=recipient,
        subject=subject,
        body=body,
    )
    context = ssl.create_default_context()
    ssl_factory = smtp_ssl_factory or smtplib.SMTP_SSL
    starttls_factory = smtp_starttls_factory or smtplib.SMTP
    try:
        if account.smtp_port == 465:
            with ssl_factory(account.smtp_host, account.smtp_port, timeout=timeout_seconds, context=context) as server:
                server.login(account.username, app_password)
                server.send_message(message)
        else:
            with starttls_factory(account.smtp_host, account.smtp_port, timeout=timeout_seconds) as server:
                server.starttls(context=context)
                server.login(account.username, app_password)
                server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        return EmailSmtpSendResult(False, None, type(exc).__name__, True, False)
    return EmailSmtpSendResult(True, _message_id(message) or None, None, True, True)


def check_smtp_login(
    *,
    account: EmailAccount,
    app_password: str,
    timeout_seconds: int = 30,
    smtp_ssl_factory: SmtpFactory | None = None,
    smtp_starttls_factory: SmtpFactory | None = None,
) -> EmailSmtpSendResult:
    """Test SMTP login with TLS without sending a message."""
    context = ssl.create_default_context()
    ssl_factory = smtp_ssl_factory or smtplib.SMTP_SSL
    starttls_factory = smtp_starttls_factory or smtplib.SMTP
    try:
        if account.smtp_port == 465:
            with ssl_factory(account.smtp_host, account.smtp_port, timeout=timeout_seconds, context=context) as server:
                server.login(account.username, app_password)
        else:
            with starttls_factory(account.smtp_host, account.smtp_port, timeout=timeout_seconds) as server:
                server.starttls(context=context)
                server.login(account.username, app_password)
    except (OSError, smtplib.SMTPException) as exc:
        return EmailSmtpSendResult(False, None, type(exc).__name__, True, False)
    return EmailSmtpSendResult(True, None, None, True, False)
