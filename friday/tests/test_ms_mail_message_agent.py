"""Tests for Microsoft mail integration in MessageAgent."""

from __future__ import annotations

from friday.agents.message_agent import MessageAgent, MS_MAIL_MESSAGE_ID_OFFSET
from friday.storage.database import setup_local_database
from friday.storage.repositories import BlockedSenderRepository, ContactRepository, MsMailMessageRepository


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


def test_message_agent_processes_ms_mail_from_all_accounts_with_existing_relevance_rule(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    ContactRepository(db_path).create_contact(
        name="kunde@example.test",
        contact_type="kunde",
        email_address="kunde@example.test",
        betreuer="philip",
    )
    repo = MsMailMessageRepository(db_path)
    repo.upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "kunde@example.test",
                "subject": "Bitte Unterlagen prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Bitte erledigen.",
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )
    repo.upsert_messages(
        [
            {
                "message_id": "graph-1",
                "sender": "info@example.test",
                "subject": "Nur zur Info",
                "received_at": "2026-07-09T10:05:00Z",
                "snippet": "Allgemeines Update ohne Aufgabe.",
            }
        ],
        account_id="philip_familienhelden_at",
        account_username="philip@familienhelden.at",
    )

    agent = MessageAgent(db_path=db_path)
    result = agent.process_unprocessed_ms_mail_messages()

    assert result["processed_count"] == 2
    assert result["task_suggestions_created"] == 1
    assert repo.get_unprocessed_messages() == []
    local_messages = agent.get_ms_mail_messages_as_local_messages()
    assert {message["account_id"] for message in local_messages} == {
        "office_familienhelden_at",
        "philip_familienhelden_at",
    }


def test_message_agent_skips_blocked_ms_mail_sender_for_suggestions(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    ContactRepository(db_path).create_contact(
        name="spam@example.test",
        contact_type="kunde",
        email_address="spam@example.test",
        betreuer="philip",
    )
    BlockedSenderRepository(db_path).block_sender(
        source="ms_mail",
        sender="spam@example.test",
        label="Spam Sender",
    )
    repo = MsMailMessageRepository(db_path)
    repo.upsert_messages(
        [
            {
                "message_id": "graph-spam",
                "sender": "spam@example.test",
                "subject": "Bitte Unterlagen prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Bitte erledigen.",
            }
        ]
    )

    agent = MessageAgent(db_path=db_path)
    result = agent.process_unprocessed_ms_mail_messages()

    assert result["processed_count"] == 0
    assert result["task_suggestions_created"] == 0
    assert agent.get_pending_task_suggestions() == []
    assert agent.get_ms_mail_messages_as_local_messages() == []
    assert agent.get_ms_mail_messages_as_local_messages(include_spam=True)[0]["is_spam"] == 1
