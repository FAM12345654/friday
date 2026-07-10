from __future__ import annotations

from friday.app.imap_mail_account_store import build_imap_mail_account
from friday.app.imap_mail_writer import move_back_to_inbox, move_to_cleanup_label


class FakeImapClient:
    def __init__(self, *args, **kwargs) -> None:
        self.calls = []

    def login(self, username, password):
        self.calls.append(("login", username, password))
        return "OK", []

    def select(self, mailbox="INBOX", readonly=False):
        self.calls.append(("select", mailbox, readonly))
        return "OK", []

    def create(self, mailbox):
        self.calls.append(("create", mailbox))
        return "OK", []

    def search(self, charset, *criteria):
        self.calls.append(("search", charset, criteria))
        return "OK", [b"7"]

    def copy(self, message_set, mailbox):
        self.calls.append(("copy", message_set, mailbox))
        return "OK", []

    def store(self, message_set, command, flags):
        self.calls.append(("store", message_set, command, flags))
        return "OK", []

    def logout(self):
        self.calls.append(("logout",))
        return "OK", []


def _account():
    return build_imap_mail_account(
        provider="gmail",
        host="imap.gmail.com",
        port=993,
        username="test@example.com",
        app_password="pw",
        last_test_ok=True,
    )


def test_move_to_cleanup_label_is_reversible_without_delete_or_expunge() -> None:
    fake = FakeImapClient()
    result = move_to_cleanup_label(
        account=_account(),
        app_password="pw",
        provider_message_id="<abc@example.com>",
        imap_ssl_factory=lambda *args, **kwargs: fake,
    )

    assert result.ok is True
    assert result.deleted is False
    assert result.expunge_used is False
    assert ("copy", b"7", "Friday/Aussortiert") in fake.calls
    assert ("store", b"7", "-X-GM-LABELS", "\\Inbox") in fake.calls
    assert not any(call[0] == "expunge" for call in fake.calls)
    assert not any("\\Deleted" in str(call) for call in fake.calls)


def test_move_back_to_inbox_restores_inbox_without_delete_or_expunge() -> None:
    fake = FakeImapClient()
    result = move_back_to_inbox(
        account=_account(),
        app_password="pw",
        provider_message_id="<abc@example.com>",
        imap_ssl_factory=lambda *args, **kwargs: fake,
    )

    assert result.ok is True
    assert result.deleted is False
    assert result.expunge_used is False
    assert ("store", b"7", "+X-GM-LABELS", "\\Inbox") in fake.calls
    assert not any(call[0] == "expunge" for call in fake.calls)
    assert not any("\\Deleted" in str(call) for call in fake.calls)
