"""Tests for local message suggestion lifecycle in MessageAgent."""

from __future__ import annotations

import sqlite3

from friday.agents.message_agent import MessageAgent
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
from friday.storage.database import get_connection


def _build_message_agent(tmp_path):
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    return MessageAgent(db_path=db_file)


def _insert_message(db_file, message_id: int, sender: str, text: str) -> None:
    with get_connection(db_file) as connection:
        connection.execute(
            """
            INSERT INTO messages (id, sender, text, received_at, contact_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, sender, text, "2026-07-05T12:00:00", "other"),
        )


def test_generate_local_suggestions_creates_for_scheduling_messages(tmp_path) -> None:
    """Only scheduling-related messages should create local suggestions."""
    agent = _build_message_agent(tmp_path)
    suggestions = agent.generate_local_suggestions()

    assert len(suggestions) == 1
    assert suggestions[0]["message_id"] == 1
    assert suggestions[0]["status"] == "pending"
    assert suggestions[0]["draft_text"].startswith("[Platzhalter]")


def test_generate_local_task_suggestions_creates_for_task_messages(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_message(db_file, 10, "Chef", "Kannst du bitte die Rechnung prüfen?")
    agent = MessageAgent(db_path=db_file)

    suggestions = agent.generate_local_task_suggestions()
    assert len(suggestions) == 1
    assert suggestions[0]["message_id"] == 10
    assert suggestions[0]["status"] == "pending"
    assert suggestions[0]["title"] == "Aufgabe aus Nachricht von Chef"
    assert suggestions[0]["notes"] == "Kannst du bitte die Rechnung prüfen?"


def test_generate_local_suggestions_does_not_duplicate_existing(tmp_path) -> None:
    """Calling generation twice should not create duplicate rows."""
    agent = _build_message_agent(tmp_path)
    first = agent.generate_local_suggestions()
    second = agent.generate_local_suggestions()

    assert len(first) == 1
    assert len(second) == 1
    assert first[0]["id"] == second[0]["id"]


def test_generate_local_task_suggestions_does_not_duplicate(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_message(db_file, 11, "Chef", "Bitte bitte einen Bericht fertig machen.")
    agent = MessageAgent(db_path=db_file)
    first = agent.generate_local_task_suggestions()
    second = agent.generate_local_task_suggestions()

    assert len(first) == 1
    assert len(second) == 1
    assert first[0]["id"] == second[0]["id"]
    with sqlite3.connect(db_file) as connection:
        assert int(connection.execute("SELECT COUNT(*) FROM task_suggestions").fetchone()[0]) == 1


def test_generate_local_task_suggestions_only_for_task_intents(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_message(db_file, 12, "Kollege", "Kannst du bitte die Unterlagen vorbereiten?")
    _insert_message(db_file, 13, "Kollege", "Wie ist der Stand?")
    agent = MessageAgent(db_path=db_file)
    agent.generate_local_suggestions()

    suggestions = agent.generate_local_task_suggestions()
    assert {item["message_id"] for item in suggestions} == {12}


def test_generate_local_task_suggestions_does_not_create_for_non_task_messages(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_message(db_file, 14, "Kollege", "Kannst du morgen den Termin bestätigen?")
    agent = MessageAgent(db_path=db_file)
    suggestions = agent.generate_local_task_suggestions()

    assert suggestions == []


def test_get_pending_task_suggestions_returns_rows(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_message(db_file, 15, "Chef", "Kannst du bitte eine Notiz prüfen?")
    agent = MessageAgent(db_path=db_file)
    agent.generate_local_task_suggestions()

    pending = agent.get_pending_task_suggestions()
    assert len(pending) == 1
    assert pending[0]["status"] == "pending"


def test_get_pending_suggestions_returns_pending(tmp_path) -> None:
    """Pending suggestions from the local DB should be returned."""
    agent = _build_message_agent(tmp_path)
    agent.generate_local_suggestions()

    pending = agent.get_pending_suggestions()
    assert len(pending) == 1
    assert pending[0]["status"] == "pending"


def test_detect_intent_scheduling(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    intent = agent.detect_intent("Hast du morgen um 10 Uhr Zeit für ein Treffen?")
    assert intent == "scheduling"


def test_detect_intent_task(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    intent = agent.detect_intent("Kannst du bitte die Unterlagen vorbereiten?")
    assert intent == "task"


def test_detect_intent_question(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    intent = agent.detect_intent("Was ist der aktuelle Status?")
    assert intent == "question"


def test_detect_intent_info(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    intent = agent.detect_intent("Zur Info: Der Kunde hat angerufen.")
    assert intent == "info"


def test_detect_intent_unclear(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    intent = agent.detect_intent("Alles klar")
    assert intent == "unclear"


def test_scheduling_priority_over_question(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    intent = agent.detect_intent("Hast du morgen Zeit?")
    assert intent == "scheduling"


def test_task_priority_over_question(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    intent = agent.detect_intent("Kannst du bitte die Datei schicken?")
    assert intent == "task"


def test_is_scheduling_related_uses_detect_intent(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    assert agent.is_scheduling_related("Kannst du morgen einen Termin bestätigen?")
    assert not agent.is_scheduling_related("Kannst du bitte die Unterlagen schicken?")


def test_generate_local_suggestions_only_for_scheduling(tmp_path) -> None:
    agent = _build_message_agent(tmp_path)

    suggestions = agent.generate_local_suggestions()
    assert {item["message_id"] for item in suggestions} == {1}


def test_approve_suggestion_marks_suggestion_approved(tmp_path) -> None:
    """Approving stays local and only changes local status."""
    agent = _build_message_agent(tmp_path)
    suggestion = agent.generate_local_suggestions()[0]

    approved = agent.approve_suggestion(suggestion["id"])
    assert approved is not None
    assert approved["status"] == "approved"


def test_approve_task_suggestion_marks_rejected(tmp_path) -> None:
    """Rejecting task suggestions moves status to rejected."""
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_message(db_file, 16, "Chef", "Bitte bitte das Dokument absenden.")
    agent = MessageAgent(db_path=db_file)
    suggestion = agent.generate_local_task_suggestions()[0]

    rejected = agent.reject_task_suggestion(suggestion["id"])
    assert rejected is not None
    assert rejected["status"] == "rejected"


def test_edit_task_suggestion_updates_task_fields(tmp_path) -> None:
    """Editing task suggestion fields updates local row and marks edited."""
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_message(db_file, 17, "Chef", "Bitte prüfe den Entwurf.")
    agent = MessageAgent(db_path=db_file)
    suggestion = agent.generate_local_task_suggestions()[0]

    edited = agent.edit_task_suggestion(
        suggestion["id"],
        title="Neue Aufgabe",
        category="arbeit",
        due_date="2026-07-06",
        notes="Bitte sofort prüfen.",
        priority="high",
    )
    assert edited is not None
    assert edited["title"] == "Neue Aufgabe"
    assert edited["category"] == "arbeit"
    assert edited["due_date"] == "2026-07-06"
    assert edited["notes"] == "Bitte sofort prüfen."
    assert edited["priority"] == "high"
    assert edited["status"] == "edited"


def test_reject_suggestion_marks_suggestion_rejected(tmp_path) -> None:
    """Rejecting keeps the local suggestion record for history."""
    agent = _build_message_agent(tmp_path)
    suggestion = agent.generate_local_suggestions()[0]
    rejected = agent.reject_suggestion(suggestion["id"])

    assert rejected is not None
    assert rejected["status"] == "rejected"


def test_edit_suggestion_updates_text_and_status_locally(tmp_path) -> None:
    """Editing suggestion text stays local and sets edited status."""
    agent = _build_message_agent(tmp_path)
    suggestion = agent.generate_local_suggestions()[0]

    edited = agent.edit_suggestion(suggestion["id"], "Neue Formulierung")
    assert edited is not None
    assert edited["draft_text"] == "Neue Formulierung"
    assert edited["status"] == "edited"


def test_edit_then_approve_suggestion(tmp_path) -> None:
    """Edited suggestions remain reviewable and can be approved."""
    agent = _build_message_agent(tmp_path)
    suggestion = agent.generate_local_suggestions()[0]

    edited = agent.edit_suggestion(suggestion["id"], "Neu formuliert")
    assert edited is not None
    assert edited["status"] == "edited"

    pending = agent.get_pending_suggestions()
    assert any(item["id"] == edited["id"] for item in pending)

    approved = agent.approve_suggestion(edited["id"])
    assert approved is not None
    assert approved["status"] == "approved"

    pending_after = agent.get_pending_suggestions()
    assert all(item["id"] != edited["id"] for item in pending_after)


def test_message_agent_uses_only_local_configuration() -> None:
    """Verify setup still forbids external integrations."""
    assert USE_SQLITE_STORAGE is True
    assert ENABLE_REAL_EMAIL is False
    assert ENABLE_REAL_WHATSAPP is False
    assert ENABLE_REAL_SMS is False
    assert ENABLE_REAL_CALENDAR is False
    assert ENABLE_REAL_WEATHER is False
    assert ENABLE_REAL_MUSIC is False
    assert REQUIRE_USER_APPROVAL is True
