"""Tests for local Microsoft mail preview repository."""

from __future__ import annotations

from friday.storage.database import setup_local_database
from friday.storage.repositories import MsMailMessageRepository


def test_ms_mail_repository_upserts_and_deduplicates(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)

    repo.upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "kunde@example.test",
                "subject": "Bitte Philip prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Kurz",
            }
        ]
    )
    repo.upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "kunde@example.test",
                "subject": "Bitte Philip prüfen aktualisiert",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Kurz",
            }
        ]
    )

    items = repo.list_messages()

    assert len(items) == 1
    assert items[0]["subject"] == "Bitte Philip prüfen aktualisiert"
    assert "body" not in items[0]


def test_ms_mail_repository_marks_processed(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)
    item = repo.upsert_messages([{"message_id": "graph-1", "subject": "A"}])[0]

    repo.mark_processed(item["id"], suggestion_created=True)

    assert repo.get_unprocessed_messages() == []
    assert repo.list_messages()[0]["suggestion_created"] == 1
