"""Tests for repository read behavior on temporary databases."""

from __future__ import annotations

from friday.config import DEMO_DATE
from friday.storage.database import setup_local_database
from friday.storage.repositories import CalendarRepository, ContactRepository, MessageRepository, TaskRepository


def _build_repo_db(tmp_path):
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    return db_file


def test_task_repository_returns_open_tasks(tmp_path) -> None:
    """Task repository should return only non-done tasks."""
    db_file = _build_repo_db(tmp_path)
    repo = TaskRepository(db_file)
    open_tasks = repo.get_open_tasks()

    assert isinstance(open_tasks, list)
    assert open_tasks
    assert all(task.get("status", "").lower() != "done" for task in open_tasks)


def test_message_repository_reads_messages(tmp_path) -> None:
    """Message repository reads sample messages from local DB."""
    db_file = _build_repo_db(tmp_path)
    repo = MessageRepository(db_file)
    messages = repo.get_messages()

    assert isinstance(messages, list)
    assert messages
    assert "sender" in messages[0]


def test_calendar_repository_reads_for_date_and_free_slots(tmp_path) -> None:
    """Calendar repository should read day items and return free slots."""
    db_file = _build_repo_db(tmp_path)
    repo = CalendarRepository(db_file)
    items = repo.get_items_for_date(DEMO_DATE)
    free_slots = repo.get_free_slots_for_date(DEMO_DATE)

    assert items
    assert all(item["date"] == DEMO_DATE for item in items)
    assert isinstance(free_slots, list)


def test_contact_repository_reads_and_defaults(tmp_path) -> None:
    """Contact repository returns known categories and German fallback."""
    db_file = _build_repo_db(tmp_path)
    repo = ContactRepository(db_file)

    contacts = repo.get_contacts()
    assert isinstance(contacts, list)
    assert contacts
    assert repo.get_contact_type_by_name("Kundenbetreuung Blau") in {"kunde", "sonstiges"}
    assert repo.get_contact_type_by_name("Keine Person") == "sonstiges"
