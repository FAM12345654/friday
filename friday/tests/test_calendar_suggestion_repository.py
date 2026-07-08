"""Tests for local calendar suggestion repository."""

from __future__ import annotations

import sqlite3

import pytest

from friday.storage.database import initialize_database
from friday.storage.repositories import CalendarSuggestionRepository


def _build_repo(tmp_path):
    db_file = tmp_path / "friday.db"
    initialize_database(db_file)
    return CalendarSuggestionRepository(db_file)


def test_create_calendar_suggestion_stores_pending_record(tmp_path) -> None:
    """Repository must store a pending calendar suggestion row."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_calendar_suggestion(
        message_id=10,
        slot_date="2026-07-05",
        start="10:00",
        end="11:00",
    )

    assert suggestion["message_id"] == 10
    assert suggestion["slot_date"] == "2026-07-05"
    assert suggestion["start"] == "10:00"
    assert suggestion["end"] == "11:00"
    assert suggestion["status"] == "pending"
    assert suggestion["id"] > 0


def test_create_calendar_suggestion_does_not_duplicate_same_slot(tmp_path) -> None:
    """Duplicate calendar suggestions for the same message/date/time should be deduplicated."""
    repository = _build_repo(tmp_path)
    first = repository.create_calendar_suggestion(
        message_id=11,
        slot_date="2026-07-05",
        start="10:00",
        end="11:00",
    )
    second = repository.create_calendar_suggestion(
        message_id=11,
        slot_date="2026-07-05",
        start="10:00",
        end="11:00",
    )

    assert first["id"] == second["id"]
    assert second["start"] == first["start"]
    with sqlite3.connect(tmp_path / "friday.db") as connection:
        assert int(connection.execute("SELECT COUNT(*) FROM calendar_suggestions").fetchone()[0]) == 1


def test_get_calendar_suggestions_for_message_returns_rows(tmp_path) -> None:
    """Getting suggestions by message should return the generated rows."""
    repository = _build_repo(tmp_path)
    repository.create_calendar_suggestion(message_id=12, slot_date="2026-07-05", start="10:00", end="11:00")
    repository.create_calendar_suggestion(message_id=12, slot_date="2026-07-05", start="11:00", end="12:00")
    repository.create_calendar_suggestion(message_id=13, slot_date="2026-07-05", start="12:00", end="13:00")

    suggestions = repository.get_calendar_suggestions_for_message(12)
    assert len(suggestions) == 2
    assert all(suggestion["message_id"] == 12 for suggestion in suggestions)


def test_get_pending_calendar_suggestions_for_message_only_returns_pending(tmp_path) -> None:
    """Only pending status entries should be returned for local review."""
    repository = _build_repo(tmp_path)
    pending = repository.create_calendar_suggestion(message_id=14, slot_date="2026-07-05", start="10:00", end="11:00")
    selected = repository.create_calendar_suggestion(message_id=15, slot_date="2026-07-05", start="11:00", end="12:00")
    repository.select_calendar_suggestion(selected["id"])

    pending_suggestions = repository.get_pending_calendar_suggestions_for_message(15)
    assert all(item["status"] == "pending" for item in pending_suggestions)
    assert len(pending_suggestions) == 0
    pending_for_other = repository.get_pending_calendar_suggestions_for_message(14)
    assert len(pending_for_other) == 1
    assert pending_for_other[0]["id"] == pending["id"]


def test_select_calendar_suggestion_sets_status_selected(tmp_path) -> None:
    """Selecting a calendar suggestion changes its local state."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_calendar_suggestion(message_id=16, slot_date="2026-07-05", start="10:00", end="11:00")

    updated = repository.select_calendar_suggestion(suggestion["id"])
    assert updated is not None
    assert updated["status"] == "selected"


def test_reject_calendar_suggestion_sets_status_rejected(tmp_path) -> None:
    """Rejecting a calendar suggestion changes its local state."""
    repository = _build_repo(tmp_path)
    suggestion = repository.create_calendar_suggestion(message_id=17, slot_date="2026-07-05", start="10:00", end="11:00")

    updated = repository.reject_calendar_suggestion(suggestion["id"])
    assert updated is not None
    assert updated["status"] == "rejected"


def test_create_calendar_suggestion_invalid_status_raises(tmp_path) -> None:
    """Only documented calendar statuses may be written."""
    repository = _build_repo(tmp_path)
    with pytest.raises(ValueError, match="Ungültiger Kalender-Vorschlagsstatus"):
        repository.create_calendar_suggestion(
            message_id=18,
            slot_date="2026-07-05",
            start="10:00",
            end="11:00",
            status="komisch",
        )


def test_create_calendar_suggestion_requires_slot_fields(tmp_path) -> None:
    """Empty date/start/end must be rejected."""
    repository = _build_repo(tmp_path)
    with pytest.raises(ValueError, match="Ein Kalender-Vorschlag braucht Datum, Start und Ende"):
        repository.create_calendar_suggestion(message_id=19, slot_date="", start="10:00", end="11:00")
    with pytest.raises(ValueError, match="Ein Kalender-Vorschlag braucht Datum, Start und Ende"):
        repository.create_calendar_suggestion(message_id=19, slot_date="2026-07-05", start="", end="11:00")
    with pytest.raises(ValueError, match="Ein Kalender-Vorschlag braucht Datum, Start und Ende"):
        repository.create_calendar_suggestion(message_id=19, slot_date="2026-07-05", start="10:00", end="")
