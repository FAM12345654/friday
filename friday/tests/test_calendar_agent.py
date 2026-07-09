"""Tests for local calendar suggestion generation in CalendarAgent."""

from __future__ import annotations

from friday.agents.calendar_agent import CalendarAgent
from friday.config import (
    ENABLE_REAL_CALENDAR,
    ENABLE_REAL_EMAIL,
    ENABLE_REAL_MUSIC,
    ENABLE_REAL_SMS,
    ENABLE_REAL_WEATHER,
    ENABLE_REAL_WHATSAPP,
    REQUIRE_USER_APPROVAL,
    USE_SQLITE_STORAGE,
)
from friday.storage.database import setup_local_database


def _build_calendar_agent(tmp_path):
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    return CalendarAgent(db_path=db_file)


def test_generate_calendar_suggestions_for_message_creates_rows(tmp_path) -> None:
    """CalendarAgent should create local slot suggestions for local free slots."""
    agent = _build_calendar_agent(tmp_path)
    suggestions = agent.generate_calendar_suggestions_for_message(message_id=1)

    assert len(suggestions) > 0
    assert suggestions[0]["message_id"] == 1
    assert suggestions[0]["status"] == "pending"


def test_generate_calendar_suggestions_for_message_does_not_duplicate(tmp_path) -> None:
    """Calling generation twice should keep one row per identical slot."""
    agent = _build_calendar_agent(tmp_path)
    first = agent.generate_calendar_suggestions_for_message(message_id=1)
    second = agent.generate_calendar_suggestions_for_message(message_id=1)

    first_ids = [item["id"] for item in first]
    second_ids = [item["id"] for item in second]
    assert first_ids == second_ids
    assert len(first_ids) == len(set(first_ids))


def test_get_pending_calendar_suggestions_for_message_returns_created_slots(tmp_path) -> None:
    """Pending slot suggestions are returned per message."""
    agent = _build_calendar_agent(tmp_path)
    _ = agent.generate_calendar_suggestions_for_message(message_id=1)
    agent.select_calendar_suggestion(agent.get_calendar_suggestions_for_message(1)[0]["id"])
    pending = agent.get_pending_calendar_suggestions_for_message(1)

    assert all(slot["status"] == "pending" for slot in pending)
    assert all(slot["message_id"] == 1 for slot in pending)


def test_select_calendar_suggestion_marks_selected(tmp_path) -> None:
    """Selecting a slot changes its status locally."""
    agent = _build_calendar_agent(tmp_path)
    suggestion = agent.generate_calendar_suggestions_for_message(message_id=1)[0]

    updated = agent.select_calendar_suggestion(suggestion["id"])
    assert updated is not None
    assert updated["status"] == "selected"


def test_reject_calendar_suggestion_marks_rejected(tmp_path) -> None:
    """Rejecting a slot changes status locally and keeps history."""
    agent = _build_calendar_agent(tmp_path)
    suggestion = agent.generate_calendar_suggestions_for_message(message_id=1)[0]

    updated = agent.reject_calendar_suggestion(suggestion["id"])
    assert updated is not None
    assert updated["status"] == "rejected"


def test_calendar_agent_uses_only_local_configuration() -> None:
    """Calendar features remain local in this build."""
    assert USE_SQLITE_STORAGE is True
    assert ENABLE_REAL_EMAIL is False
    assert ENABLE_REAL_WHATSAPP is False
    assert ENABLE_REAL_SMS is False
    assert ENABLE_REAL_CALENDAR is True
    assert ENABLE_REAL_WEATHER is False
    assert ENABLE_REAL_MUSIC is False
    assert REQUIRE_USER_APPROVAL is True
