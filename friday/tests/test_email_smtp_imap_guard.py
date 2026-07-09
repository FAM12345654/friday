"""Tests for email SMTP/IMAP helpers and send guard."""

from __future__ import annotations

from friday import config
from friday.app.email_account_store import build_email_account_from_preset
from friday.app.email_imap_reader import check_imap_login, read_recent_inbox_emails
from friday.app.email_send_guard import (
    EMAIL_SEND_TOKEN,
    check_email_send_allowed,
    log_email_send,
)
from friday.app.email_smtp_sender import check_smtp_login, send_single_email
from friday.storage.database import setup_local_database


class _FakeSmtp:
    sent_messages: list[object] = []
    starttls_used = False

    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_exc) -> None:
        return None

    def starttls(self, **_kwargs) -> None:
        type(self).starttls_used = True

    def login(self, username: str, password: str) -> None:
        assert username == "user@example.test"
        assert password == "secret"

    def send_message(self, message) -> None:
        type(self).sent_messages.append(message)


class _FakeImap:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_exc) -> None:
        return None

    def login(self, username: str, password: str) -> None:
        assert username == "user@example.test"
        assert password == "secret"

    def select(self, mailbox: str, readonly: bool = False):
        assert mailbox == "INBOX"
        assert readonly is True
        return "OK", []

    def search(self, *_args):
        return "OK", [b"1"]

    def fetch(self, _message_id, query):
        assert query == "(BODY.PEEK[])"
        message = (
            b"From: sender@example.test\r\n"
            b"Subject: Hallo\r\n"
            b"Date: Thu, 9 Jul 2026 10:00:00 +0000\r\n"
            b"\r\n"
            b"Kurzer Text aus der Mail."
        )
        return "OK", [(b"1", message)]


def _account(last_test_ok: bool = True):
    return build_email_account_from_preset(
        preset_name="gmail",
        email_address="user@example.test",
        username="user@example.test",
        app_password="secret",
        last_test_ok=last_test_ok,
        protector=lambda _secret: ("encrypted", "test"),
    )


def test_smtp_sender_uses_tls_and_sends_one_message() -> None:
    result = send_single_email(
        account=_account(),
        app_password="secret",
        recipient="friend@example.test",
        subject="Betreff",
        body="Hallo",
        smtp_ssl_factory=_FakeSmtp,
    )

    assert result.ok is True
    assert result.sent is True
    assert len(_FakeSmtp.sent_messages) >= 1


def test_smtp_login_test_does_not_send() -> None:
    before = len(_FakeSmtp.sent_messages)

    result = check_smtp_login(
        account=_account(),
        app_password="secret",
        smtp_ssl_factory=_FakeSmtp,
    )

    assert result.ok is True
    assert len(_FakeSmtp.sent_messages) == before


def test_imap_reader_peeks_recent_mail() -> None:
    result = read_recent_inbox_emails(
        account=_account(),
        app_password="secret",
        imap_ssl_factory=_FakeImap,
    )

    assert result.ok is True
    assert result.read_only is True
    assert result.items[0].sender == "sender@example.test"
    assert result.items[0].text_preview == "Kurzer Text aus der Mail."


def test_imap_login_test_does_not_fetch() -> None:
    result = check_imap_login(
        account=_account(),
        app_password="secret",
        imap_ssl_factory=_FakeImap,
    )

    assert result.ok is True
    assert result.items == ()


def test_email_send_guard_blocks_when_real_email_flag_is_false(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)

    guard = check_email_send_allowed(
        recipient="friend@example.test",
        subject="Hallo",
        approval_token=EMAIL_SEND_TOKEN,
        account=_account(),
        db_path=db_path,
    )

    assert guard.allowed is False
    assert "real_email_disabled" in guard.blocked_reasons


def test_email_send_guard_requires_contact_token_account_and_limit(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    monkeypatch.setattr(config, "ENABLE_REAL_EMAIL", True)

    from friday.storage.database import get_connection

    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO contacts (name, contact_type, email_address) VALUES (?, ?, ?)",
            ("Friend", "work", "friend@example.test"),
        )

    allowed = check_email_send_allowed(
        recipient="friend@example.test",
        subject="Hallo",
        approval_token=EMAIL_SEND_TOKEN,
        account=_account(last_test_ok=True),
        db_path=db_path,
        daily_limit=2,
    )
    blocked_token = check_email_send_allowed(
        recipient="friend@example.test",
        subject="Hallo",
        approval_token="wrong",
        account=_account(last_test_ok=True),
        db_path=db_path,
        daily_limit=2,
    )
    log_email_send(
        recipient="friend@example.test",
        subject="Hallo",
        message_id="m1",
        status="sent",
        db_path=db_path,
    )
    log_email_send(
        recipient="friend@example.test",
        subject="Hallo",
        message_id="m2",
        status="sent",
        db_path=db_path,
    )
    blocked_limit = check_email_send_allowed(
        recipient="friend@example.test",
        subject="Hallo",
        approval_token=EMAIL_SEND_TOKEN,
        account=_account(last_test_ok=True),
        db_path=db_path,
        daily_limit=2,
    )

    assert allowed.allowed is True
    assert blocked_token.allowed is False
    assert "approval_token_invalid" in blocked_token.blocked_reasons
    assert blocked_limit.allowed is False
    assert "daily_limit_reached" in blocked_limit.blocked_reasons
