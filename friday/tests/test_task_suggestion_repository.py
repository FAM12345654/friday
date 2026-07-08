"""Tests for local task suggestion repository."""

from __future__ import annotations

import sqlite3

import pytest

from friday.storage.database import initialize_database
from friday.storage.repositories import TaskSuggestionRepository


def _build_repo(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return TaskSuggestionRepository(db_file)


def _row_count(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def test_create_task_suggestion_stores_pending_record(tmp_path) -> None:
    """Repository should store a pending task suggestion."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_task_suggestion(
        message_id=77,
        title="Aufgabe aus Nachricht",
        category="arbeit",
        due_date="2026-07-05",
        notes="Bitte prüfen",
        priority="high",
    )

    assert suggestion["message_id"] == 77
    assert suggestion["title"] == "Aufgabe aus Nachricht"
    assert suggestion["category"] == "arbeit"
    assert suggestion["due_date"] == "2026-07-05"
    assert suggestion["notes"] == "Bitte prüfen"
    assert suggestion["priority"] == "high"
    assert suggestion["status"] == "pending"
    assert suggestion["created_task_id"] is None


def test_create_task_suggestion_does_not_duplicate_same_message(tmp_path) -> None:
    """Duplicate creation should return the existing suggestion."""
    repository = _build_repo(tmp_path)
    first = repository.create_task_suggestion(message_id=11, title="Erste Version")
    second = repository.create_task_suggestion(message_id=11, title="Andere Version")

    assert first["id"] == second["id"]
    assert second["title"] == "Erste Version"
    assert _row_count(sqlite3.connect(tmp_path / "friday.db"), "task_suggestions") == 1


def test_get_pending_task_suggestions_returns_pending_and_edited(tmp_path) -> None:
    """Pending list should contain both pending and edited items only."""
    repository = _build_repo(tmp_path)
    pending = repository.create_task_suggestion(message_id=1, title="Erste")
    edited = repository.create_task_suggestion(message_id=2, title="Zweite")
    repository.update_task_suggestion_status(edited["id"], status="edited")

    pending_suggestions = repository.get_pending_task_suggestions()
    assert len(pending_suggestions) == 2
    assert {item["id"] for item in pending_suggestions} == {pending["id"], edited["id"]}


def test_approved_rejected_and_converted_not_pending(tmp_path) -> None:
    """Only open task suggestion states remain in the review list."""
    repository = _build_repo(tmp_path)
    approved = repository.create_task_suggestion(message_id=3, title="Geprüft")
    rejected = repository.create_task_suggestion(message_id=4, title="Abgelehnt")
    converted = repository.create_task_suggestion(message_id=5, title="Konvertiert")

    repository.update_task_suggestion_status(approved["id"], status="approved")
    repository.update_task_suggestion_status(rejected["id"], status="rejected")
    repository.mark_task_suggestion_converted(converted["id"], created_task_id=99)

    pending = repository.get_pending_task_suggestions()
    assert all(item["status"] in {"pending", "edited"} for item in pending)
    assert approved["id"] not in {item["id"] for item in pending}
    assert rejected["id"] not in {item["id"] for item in pending}
    assert converted["id"] not in {item["id"] for item in pending}


def test_edit_task_suggestion_changes_fields_and_sets_status(tmp_path) -> None:
    """Editing task suggestion fields should mark it as edited."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_task_suggestion(message_id=6, title="Alt")

    edited = repository.edit_task_suggestion(
        suggestion["id"],
        title="Neu",
        category="kunde",
        due_date="2026-07-10",
        notes="Neue Notiz",
        priority="urgent",
    )
    assert edited is not None
    assert edited["title"] == "Neu"
    assert edited["category"] == "kunde"
    assert edited["due_date"] == "2026-07-10"
    assert edited["notes"] == "Neue Notiz"
    assert edited["priority"] == "urgent"
    assert edited["status"] == "edited"


def test_create_task_suggestion_rejects_empty_title(tmp_path) -> None:
    """Empty titles are not accepted for task suggestions."""
    repository = _build_repo(tmp_path)
    with pytest.raises(ValueError, match="Ein Aufgaben-Vorschlag braucht einen Titel"):
        repository.create_task_suggestion(message_id=7, title="   ")


def test_update_task_suggestion_status_rejects_invalid_value(tmp_path) -> None:
    """Invalid status values must be rejected."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_task_suggestion(message_id=8, title="Ungültig testen")

    with pytest.raises(ValueError, match="Ungültiger Aufgaben-Vorschlagsstatus"):
        repository.update_task_suggestion_status(suggestion["id"], status="komisch")


def test_mark_task_suggestion_converted_stores_created_task_id(tmp_path) -> None:
    """Converting creates a link to the local task."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_task_suggestion(message_id=9, title="Konvertieren")
    converted = repository.mark_task_suggestion_converted(suggestion["id"], created_task_id=123)

    assert converted is not None
    assert converted["status"] == "converted"
    assert converted["created_task_id"] == 123
