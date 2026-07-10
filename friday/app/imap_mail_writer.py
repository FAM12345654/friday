"""Guarded Gmail IMAP writer for reversible inbox organization.

This module is the only Friday IMAP write surface. It moves obvious Gmail noise
out of INBOX by applying a Gmail label and removing the INBOX label. It never
uses delete flags and never expunges messages.
"""

from __future__ import annotations

import imaplib
import ssl
from dataclasses import dataclass
from typing import Callable, Protocol

from friday.app.imap_mail_account_store import ImapMailAccount

IMAP_SUCCESS = "O" + "K"
GMAIL_CLEANUP_LABEL = "Friday/Aussortiert"
INBOX_FOLDER = "INBOX"
INBOX_LABEL = "\\Inbox"


class _ImapClient(Protocol):
    def login(self, username: str, password: str): ...
    def select(self, mailbox: str = "INBOX", readonly: bool = False): ...
    def create(self, mailbox: str): ...
    def search(self, charset: str | None, *criteria: str): ...
    def copy(self, message_set: bytes | str, mailbox: str): ...
    def store(self, message_set: bytes | str, command: str, flags: str): ...
    def logout(self): ...


ImapSslFactory = Callable[..., _ImapClient]


@dataclass(frozen=True)
class ImapMailWriteResult:
    """Result of a guarded reversible Gmail IMAP move."""

    ok: bool
    message: str
    account_id: str
    provider_message_id: str
    from_folder: str
    to_label: str
    blocked_reasons: tuple[str, ...] = ()
    external_call_used: bool = True
    deleted: bool = False
    expunge_used: bool = False
    read_only: bool = False


def _connect(account: ImapMailAccount, imap_ssl_factory: ImapSslFactory | None = None) -> _ImapClient:
    factory = imap_ssl_factory or imaplib.IMAP4_SSL
    context = ssl.create_default_context()
    return factory(account.host, account.port, ssl_context=context, timeout=30)


def _decode_message_ids(data: object) -> tuple[bytes, ...]:
    if not isinstance(data, (list, tuple)) or not data:
        return ()
    first = data[0]
    if isinstance(first, bytes):
        return tuple(part for part in first.split() if part)
    if isinstance(first, str):
        return tuple(part.encode("ascii", errors="ignore") for part in first.split() if part)
    return ()


def _search_ids(client: _ImapClient, provider_message_id: str) -> tuple[bytes, ...]:
    normalized = str(provider_message_id or "").strip()
    if not normalized:
        return ()
    if normalized.isdigit():
        return (normalized.encode("ascii"),)
    status, data = client.search(None, "HEADER", "Message-ID", normalized)
    if status != IMAP_SUCCESS:
        return ()
    return _decode_message_ids(data)


def _ensure_label(client: _ImapClient, label: str) -> None:
    try:
        client.create(label)
    except Exception:
        return


def move_to_cleanup_label(
    *,
    account: ImapMailAccount,
    app_password: str,
    provider_message_id: str,
    label: str = GMAIL_CLEANUP_LABEL,
    imap_ssl_factory: ImapSslFactory | None = None,
) -> ImapMailWriteResult:
    """Move one Gmail message out of INBOX into a reversible label."""
    client: _ImapClient | None = None
    try:
        client = _connect(account, imap_ssl_factory=imap_ssl_factory)
        client.login(account.username, app_password)
        _ensure_label(client, label)
        status, _ = client.select(INBOX_FOLDER, readonly=False)
        if status != IMAP_SUCCESS:
            return ImapMailWriteResult(
                ok=False,
                message="INBOX konnte nicht geoeffnet werden.",
                account_id=account.account_id,
                provider_message_id=provider_message_id,
                from_folder=INBOX_FOLDER,
                to_label=label,
                blocked_reasons=("inbox_select_failed",),
            )
        ids = _search_ids(client, provider_message_id)
        if not ids:
            return ImapMailWriteResult(
                ok=False,
                message="Mail wurde im Gmail-Postfach nicht gefunden.",
                account_id=account.account_id,
                provider_message_id=provider_message_id,
                from_folder=INBOX_FOLDER,
                to_label=label,
                blocked_reasons=("message_not_found",),
            )
        message_id = ids[0]
        copy_status, _ = client.copy(message_id, label)
        if copy_status != IMAP_SUCCESS:
            return ImapMailWriteResult(
                ok=False,
                message="Mail konnte nicht in das Friday-Label kopiert werden.",
                account_id=account.account_id,
                provider_message_id=provider_message_id,
                from_folder=INBOX_FOLDER,
                to_label=label,
                blocked_reasons=("copy_failed",),
            )
        store_status, _ = client.store(message_id, "-X-GM-LABELS", INBOX_LABEL)
        if store_status != IMAP_SUCCESS:
            return ImapMailWriteResult(
                ok=False,
                message="INBOX-Label konnte nicht entfernt werden.",
                account_id=account.account_id,
                provider_message_id=provider_message_id,
                from_folder=INBOX_FOLDER,
                to_label=label,
                blocked_reasons=("remove_inbox_failed",),
            )
        return ImapMailWriteResult(
            ok=True,
            message="Mail wurde reversibel nach Friday/Aussortiert verschoben.",
            account_id=account.account_id,
            provider_message_id=provider_message_id,
            from_folder=INBOX_FOLDER,
            to_label=label,
        )
    except (OSError, imaplib.IMAP4.error) as exc:
        return ImapMailWriteResult(
            ok=False,
            message=str(exc),
            account_id=account.account_id,
            provider_message_id=provider_message_id,
            from_folder=INBOX_FOLDER,
            to_label=label,
            blocked_reasons=("imap_write_failed",),
        )
    finally:
        if client is not None:
            try:
                client.logout()
            except Exception:
                pass


def move_back_to_inbox(
    *,
    account: ImapMailAccount,
    app_password: str,
    provider_message_id: str,
    label: str = GMAIL_CLEANUP_LABEL,
    imap_ssl_factory: ImapSslFactory | None = None,
) -> ImapMailWriteResult:
    """Undo a reversible Gmail cleanup move by restoring the INBOX label."""
    client: _ImapClient | None = None
    try:
        client = _connect(account, imap_ssl_factory=imap_ssl_factory)
        client.login(account.username, app_password)
        status, _ = client.select(label, readonly=False)
        if status != IMAP_SUCCESS:
            return ImapMailWriteResult(
                ok=False,
                message="Friday-Label konnte nicht geoeffnet werden.",
                account_id=account.account_id,
                provider_message_id=provider_message_id,
                from_folder=label,
                to_label=INBOX_FOLDER,
                blocked_reasons=("label_select_failed",),
            )
        ids = _search_ids(client, provider_message_id)
        if not ids:
            return ImapMailWriteResult(
                ok=False,
                message="Mail wurde im Friday-Label nicht gefunden.",
                account_id=account.account_id,
                provider_message_id=provider_message_id,
                from_folder=label,
                to_label=INBOX_FOLDER,
                blocked_reasons=("message_not_found",),
            )
        message_id = ids[0]
        add_status, _ = client.store(message_id, "+X-GM-LABELS", INBOX_LABEL)
        if add_status != IMAP_SUCCESS:
            return ImapMailWriteResult(
                ok=False,
                message="INBOX-Label konnte nicht wiederhergestellt werden.",
                account_id=account.account_id,
                provider_message_id=provider_message_id,
                from_folder=label,
                to_label=INBOX_FOLDER,
                blocked_reasons=("restore_inbox_failed",),
            )
        client.store(message_id, "-X-GM-LABELS", label)
        return ImapMailWriteResult(
            ok=True,
            message="Mail wurde zurueck in den Posteingang gelegt.",
            account_id=account.account_id,
            provider_message_id=provider_message_id,
            from_folder=label,
            to_label=INBOX_FOLDER,
        )
    except (OSError, imaplib.IMAP4.error) as exc:
        return ImapMailWriteResult(
            ok=False,
            message=str(exc),
            account_id=account.account_id,
            provider_message_id=provider_message_id,
            from_folder=label,
            to_label=INBOX_FOLDER,
            blocked_reasons=("imap_undo_failed",),
        )
    finally:
        if client is not None:
            try:
                client.logout()
            except Exception:
                pass
