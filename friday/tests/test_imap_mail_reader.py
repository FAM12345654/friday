"""Tests for the read-only IMAP mail reader."""

from __future__ import annotations

import imaplib

from friday.app.imap_mail_account_store import ImapMailAccount
from friday.app.imap_mail_reader import check_imap_mail_login, read_imap_mail_messages


RAW_MESSAGE = b"\r\n".join(
    [
        b"Message-ID: <gmail-1@example.test>",
        b"From: Kollegin <kollegin@example.test>",
        b"To: Philip <philip07102000@gmail.com>",
        b"Cc: Team <team@example.test>",
        b"Subject: Bitte Rechnung pruefen",
        b"Date: Thu, 09 Jul 2026 10:00:00 +0200",
        b"Content-Type: text/plain; charset=utf-8",
        b"",
        "Hallo Philip, bitte pruefe die Rechnung.".encode("utf-8"),
    ]
)


def _account() -> ImapMailAccount:
    return ImapMailAccount(
        account_id="gmail_philip07102000_gmail_com",
        provider="gmail",
        host="imap.gmail.com",
        port=993,
        username="philip07102000@gmail.com",
        encrypted_app_password="encrypted",
        encryption_method="test",
        connected_at="2026-07-10T10:00:00+00:00",
        last_test_ok=True,
    )


class FakeImapClient:
    instances: list["FakeImapClient"] = []

    def __init__(self, host, port, timeout=None, ssl_context=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.ssl_context = ssl_context
        self.login_args = None
        self.selected_readonly = None
        self.fetch_queries = []
        FakeImapClient.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def login(self, username, password):
        self.login_args = (username, password)
        return ("OK", [b"logged in"])

    def select(self, mailbox, readonly=False):
        self.selected_readonly = readonly
        return ("OK", [b"2"])

    def search(self, charset, *criteria):
        return ("OK", [b"1"])

    def fetch(self, message_id, query):
        self.fetch_queries.append(query)
        return ("OK", [(b"1 (BODY[])", RAW_MESSAGE)])


class FailingImapClient(FakeImapClient):
    def login(self, username, password):
        raise imaplib.IMAP4.error("invalid credentials")


def test_check_imap_mail_login_uses_runtime_password_without_fetching() -> None:
    FakeImapClient.instances = []

    result = check_imap_mail_login(
        account=_account(),
        app_password="runtime-secret",
        imap_ssl_factory=FakeImapClient,
    )

    assert result.ok is True
    assert result.messages == ()
    assert result.read_only is True
    assert FakeImapClient.instances[0].login_args == ("philip07102000@gmail.com", "runtime-secret")
    assert FakeImapClient.instances[0].fetch_queries == []


def test_read_imap_mail_messages_uses_readonly_select_and_body_peek() -> None:
    FakeImapClient.instances = []

    result = read_imap_mail_messages(
        account=_account(),
        app_password="runtime-secret",
        limit=10,
        imap_ssl_factory=FakeImapClient,
    )

    assert result.ok is True
    assert result.external_call_used is True
    assert result.read_only is True
    assert FakeImapClient.instances[0].selected_readonly is True
    assert FakeImapClient.instances[0].fetch_queries == ["(BODY.PEEK[])"]
    assert len(result.messages) == 1
    message = result.messages[0]
    assert message.provider_message_id == "<gmail-1@example.test>"
    assert message.sender == "Kollegin <kollegin@example.test>"
    assert message.subject == "Bitte Rechnung pruefen"
    assert message.recipients[0]["address"] == "philip07102000@gmail.com"
    assert message.to_repository_item()["source"] == "imap_mail"


def test_read_imap_mail_messages_reports_reconnect_on_auth_failure() -> None:
    result = read_imap_mail_messages(
        account=_account(),
        app_password="wrong",
        imap_ssl_factory=FailingImapClient,
    )

    assert result.ok is False
    assert "reconnect_required" in result.blocked_reasons
    assert "imap_auth_or_login_failed" in result.blocked_reasons
