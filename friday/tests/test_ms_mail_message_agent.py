"""Tests for Microsoft mail integration in MessageAgent."""

from __future__ import annotations

from friday.agents.message_agent import MessageAgent, MS_MAIL_MESSAGE_ID_OFFSET
from friday.storage.database import setup_local_database
from friday.storage.repositories import ContactRepository, MsMailMessageRepository


def test_message_agent_exposes_ms_mail_as_local_messages(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    repo = MsMailMessageRepository(db_path)
    stored = repo.upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "kunde@example.test",
                "subject": "Termin morgen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Passt 15.07.2026 10:00?",
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )[0]

    messages = MessageAgent(db_path=db_path).get_ms_mail_messages_as_local_messages()

    assert messages[0]["id"] == MS_MAIL_MESSAGE_ID_OFFSET + stored["id"]
    assert messages[0]["source"] == "ms_mail"
    assert messages[0]["account_id"] == "office_familienhelden_at"
    assert messages[0]["account_username"] == "office@familienhelden.at"
    assert "Termin morgen" in messages[0]["text"]


def test_message_agent_creates_task_suggestion_only_when_relevant(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    ContactRepository(db_path).create_contact(
        name="kunde@example.test",
        contact_type="kunde",
        email_address="kunde@example.test",
        betreuer="philip",
    )
    MsMailMessageRepository(db_path).upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "kunde@example.test",
                "subject": "Bitte Unterlagen prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Bitte erledigen.",
            }
        ]
    )
    agent = MessageAgent(db_path=db_path)

    result = agent.process_unprocessed_ms_mail_messages()

    assert result["processed_count"] == 1
    assert result["task_suggestions_created"] == 1
    assert agent.get_pending_task_suggestions()[0]["title"] == "Aufgabe aus E-Mail von kunde@example.test"
