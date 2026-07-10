from __future__ import annotations

from friday.storage.database import setup_local_database
from friday.storage.repositories import MailboxCleanupLogRepository


def test_mailbox_cleanup_log_repository_records_and_marks_undo(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repository = MailboxCleanupLogRepository(db_path)

    entry = repository.create_entry(
        account_id="gmail",
        provider_message_id="<m1@example.com>",
        sender="Noise <noise@example.com>",
        subject="Newsletter",
    )
    items = repository.list_entries()
    undone = repository.mark_undone(entry["id"])

    assert items[0]["provider_message_id"] == "<m1@example.com>"
    assert undone is not None
    assert undone["undone"] == 1
    assert repository.list_entries() == []
    assert len(repository.list_entries(include_undone=True)) == 1
