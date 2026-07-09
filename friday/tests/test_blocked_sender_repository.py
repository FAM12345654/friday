"""Tests for Friday's local-only sender blocklist."""

from __future__ import annotations

from friday.storage.database import get_connection, setup_local_database
from friday.storage.repositories import BlockedSenderRepository, normalize_blocked_sender_key


def test_blocked_sender_repository_normalizes_email_and_deduplicates(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = BlockedSenderRepository(db_path)

    first = repo.block_sender(source="ms_mail", sender=" Kunde@Example.Test ", label="Kunde")
    second = repo.block_sender(source="ms_mail", sender="Kunde <kunde@example.test>", label="Kunde 2")

    assert first["id"] == second["id"]
    assert repo.is_sender_blocked(source="ms_mail", sender="kunde@example.test") is True
    assert repo.list_blocked_senders()[0]["label"] == "Kunde 2"


def test_blocked_sender_repository_hashes_whatsapp_keys(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = BlockedSenderRepository(db_path)

    blocked = repo.block_sender(source="whatsapp", sender="+43 660 1234567", label="Kontakt")

    assert len(blocked["sender_key"]) == 64
    assert blocked["sender_key"] == normalize_blocked_sender_key("whatsapp", "+43 660 1234567")
    assert repo.is_sender_blocked(source="whatsapp", sender=blocked["sender_key"]) is True


def test_unblock_sender_restores_local_message_visibility(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = BlockedSenderRepository(db_path)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO messages (id, sender, text, received_at, contact_type)
            VALUES (1, 'Spam Sender', 'Spam Text', '2026-07-09T10:00:00', 'other')
            """
        )

    marked = repo.mark_source_message_spam(source="message", message_id=1)
    assert marked is not None

    with get_connection(db_path) as connection:
        row = connection.execute("SELECT is_spam FROM messages WHERE id = 1").fetchone()
        assert row["is_spam"] == 1

    repo.unblock_sender(marked["blocked_sender"]["id"])

    with get_connection(db_path) as connection:
        row = connection.execute("SELECT is_spam FROM messages WHERE id = 1").fetchone()
        assert row["is_spam"] == 0
