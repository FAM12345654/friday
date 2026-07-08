"""Tests for local message suggestion repository."""

from __future__ import annotations

import sqlite3

import pytest

from friday.storage.database import initialize_database
from friday.storage.repositories import MessageSuggestionRepository


def _build_repo(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return MessageSuggestionRepository(db_file)


def _row_count(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def test_create_suggestion_stores_pending_record(tmp_path) -> None:
    """Repository must store a pending suggestion draft with required values."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=77, draft_text="Antworttext")

    assert suggestion["message_id"] == 77
    assert suggestion["draft_text"] == "Antworttext"
    assert suggestion["suggestion_type"] == "reply"
    assert suggestion["status"] == "pending"
    assert suggestion["id"] > 0


def test_create_suggestion_does_not_duplicate_same_message_and_type(tmp_path) -> None:
    """A duplicate suggestion request should return the existing local row."""
    repository = _build_repo(tmp_path)
    first = repository.create_suggestion(message_id=11, draft_text="Erste Version")
    second = repository.create_suggestion(message_id=11, draft_text="Andere Version")

    assert first["id"] == second["id"]
    assert second["draft_text"] == "Erste Version"

    with sqlite3.connect(tmp_path / "friday.db") as connection:
        assert _row_count(connection, "message_suggestions") == 1


def test_get_pending_suggestions_only_returns_pending(tmp_path) -> None:
    """Only non-final records are shown in the review list."""
    repository = _build_repo(tmp_path)
    repository.create_suggestion(message_id=1, draft_text="Ein Vorschlag")
    approved = repository.create_suggestion(message_id=2, draft_text="Noch einer")
    repository.update_suggestion_status(approved["id"], status="approved")

    pending = repository.get_pending_suggestions()
    assert len(pending) == 1
    assert pending[0]["message_id"] == 1


def test_edited_suggestion_remains_pending_reviewable(tmp_path) -> None:
    """Edited suggestions stay visible until approved or rejected."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=3, draft_text="Ursprünglich")
    edited = repository.edit_suggestion_draft(suggestion["id"], draft_text="Überarbeitet")

    pending = repository.get_pending_suggestions()
    assert len(pending) == 1
    assert pending[0]["id"] == edited["id"]
    assert pending[0]["status"] == "edited"


def test_approved_suggestion_not_in_pending_review(tmp_path) -> None:
    """Approved suggestions are removed from the local review queue."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=4, draft_text="Zweites Beispiel")
    repository.update_suggestion_status(suggestion["id"], status="approved")

    pending = repository.get_pending_suggestions()
    assert all(item["id"] != suggestion["id"] for item in pending)


def test_rejected_suggestion_not_in_pending_review(tmp_path) -> None:
    """Rejected suggestions are removed from the local review queue."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=5, draft_text="Drittes Beispiel")
    repository.update_suggestion_status(suggestion["id"], status="rejected")

    pending = repository.get_pending_suggestions()
    assert all(item["id"] != suggestion["id"] for item in pending)


def test_update_suggestion_status_approves_record(tmp_path) -> None:
    """Updating a suggestion status should store the new state."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=3, draft_text="Test")
    updated = repository.update_suggestion_status(suggestion["id"], status="approved")

    assert updated is not None
    assert updated["status"] == "approved"


def test_update_suggestion_status_invalid_value_raises(tmp_path) -> None:
    """Only documented suggestion statuses may be written."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=4, draft_text="Test")

    with pytest.raises(ValueError, match="Ungültiger Vorschlagsstatus"):
        repository.update_suggestion_status(suggestion["id"], status="komisch")


def test_edit_suggestion_draft_changes_text_and_marks_edited(tmp_path) -> None:
    """Editing local draft text marks it as edited."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=5, draft_text="Alt")
    updated = repository.edit_suggestion_draft(suggestion["id"], draft_text="Neu")

    assert updated is not None
    assert updated["draft_text"] == "Neu"
    assert updated["status"] == "edited"


def test_edit_suggestion_draft_rejects_empty_text(tmp_path) -> None:
    """Editing to an empty string is not allowed."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_suggestion(message_id=6, draft_text="Text")

    with pytest.raises(ValueError, match="Ein Vorschlag braucht Text"):
        repository.edit_suggestion_draft(suggestion["id"], draft_text="   ")
