"""Tests for deterministic local calendar event extraction."""

from __future__ import annotations

from friday.agents.message_agent import MessageAgent
from friday.app.calendar_event_extraction import extract_calendar_event_candidate
from friday.config import ENABLE_REAL_CALENDAR
from friday.storage.database import setup_local_database


def test_extract_calendar_event_with_explicit_date_and_time() -> None:
    result = extract_calendar_event_candidate(
        "Termin am 15.07.2026 um 10:00 im Buero",
        base_date="2026-07-09",
    )

    assert result.has_event is True
    assert result.proposed_date == "2026-07-15"
    assert result.proposed_start == "10:00"
    assert result.needs_review is True
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
    assert "calendar.google.com" in result.calendar_link


def test_extract_calendar_event_resolves_weekday_from_python_base_date() -> None:
    result = extract_calendar_event_candidate(
        "Donnerstag um 10 Uhr Termin mit Max",
        base_date="2026-07-09",
    )

    assert result.has_event is True
    assert result.proposed_date == "2026-07-09"
    assert result.proposed_start == "10:00"
    assert "donnerstag" in result.raw_time_text


def test_extract_calendar_event_resolves_halb_vier_as_1530() -> None:
    result = extract_calendar_event_candidate(
        "Morgen halb 4 Projektbesprechung",
        base_date="2026-07-09",
    )

    assert result.has_event is True
    assert result.proposed_date == "2026-07-10"
    assert result.proposed_start == "15:30"
    assert "halb 4" in result.raw_time_text


def test_extract_calendar_event_rejects_text_without_complete_event() -> None:
    result = extract_calendar_event_candidate(
        "Bitte pruefe irgendwann die Unterlagen.",
        base_date="2026-07-09",
    )

    assert result.has_event is False
    assert result.calendar_link is None
    assert result.external_action_used is False


def test_message_agent_creates_calendar_event_suggestion_without_calendar_write(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    agent = MessageAgent(db_path=db_file)

    suggestion = agent.create_calendar_event_suggestion(
        {
            "id": 77,
            "sender": "Chef",
            "text": "Termin am 15.07.2026 um 10:00 im Buero",
        }
    )

    assert ENABLE_REAL_CALENDAR is False
    assert suggestion is not None
    assert suggestion["message_id"] == 77
    assert suggestion["suggestion_type"] == "calendar_event"
    assert suggestion["status"] == "pending"
    assert "Es wurde kein Kalendertermin erstellt." in suggestion["draft_text"]
