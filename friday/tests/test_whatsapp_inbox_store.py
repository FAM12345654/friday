"""Tests for the local WhatsApp read bridge store."""

from __future__ import annotations

from friday.agents.message_agent import MessageAgent
from friday.app.whatsapp_inbox_store import (
    WHATSAPP_MESSAGE_ID_OFFSET,
    bridge_token_matches,
    ensure_whatsapp_bridge_token,
    get_whatsapp_bridge_status,
    insert_whatsapp_message,
    load_whatsapp_agent_notes,
    read_recent_whatsapp_messages,
    resolve_whatsapp_conversation,
    save_whatsapp_agent_notes,
)
from friday.storage.database import setup_local_database
from friday.storage.repositories import BlockedSenderRepository


def test_bridge_token_is_required_and_created_with_strong_value(tmp_path) -> None:
    token_path = tmp_path / "bridge-token.txt"

    assert bridge_token_matches(None, token_path=token_path) is False
    token = ensure_whatsapp_bridge_token(token_path=token_path)

    assert len(token) >= 32
    assert bridge_token_matches(token, token_path=token_path) is True
    assert bridge_token_matches("wrong", token_path=token_path) is False


def test_insert_whatsapp_message_hashes_identifiers_and_deduplicates(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)

    first = insert_whatsapp_message(
        chat_id="local-chat",
        sender_name="Kontakt",
        sender_number="local-number",
        body="[redacted]",
        received_at="2026-07-09T10:00:00+00:00",
        db_path=db_path,
    )
    duplicate = insert_whatsapp_message(
        chat_id="local-chat",
        sender_name="Kontakt",
        sender_number="local-number",
        body="[redacted]",
        received_at="2026-07-09T10:00:00+00:00",
        db_path=db_path,
    )

    assert first.stored is True
    assert duplicate.duplicate is True
    items = read_recent_whatsapp_messages(db_path=db_path)
    assert len(items) == 1
    assert items[0]["sender_number_masked"].startswith("hash:")
    assert "sender_number_hash" not in items[0]
    assert items[0]["synthetic_message_id"] == WHATSAPP_MESSAGE_ID_OFFSET + first.message_id


def test_process_whatsapp_message_creates_review_suggestions(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    insert_whatsapp_message(
        chat_id="task-chat",
        sender_name="Kontakt",
        sender_number="task-number",
        body="todo fuer Philip",
        received_at="2026-07-09T10:05:00+00:00",
        db_path=db_path,
    )

    agent = MessageAgent(db_path=db_path)
    result = agent.process_unprocessed_whatsapp_messages()

    assert result.processed_count == 1
    assert result.message_suggestions_created == 1
    assert result.task_suggestions_created == 1
    assert agent.get_pending_suggestions()
    assert agent.get_pending_task_suggestions()
    status = get_whatsapp_bridge_status(db_path)
    assert status["message_count"] == 1


def test_whatsapp_agent_notes_roundtrip_locally(tmp_path) -> None:
    notes_path = tmp_path / "whatsapp" / "agent_notes.json"

    missing = load_whatsapp_agent_notes(notes_path)
    saved = save_whatsapp_agent_notes("Nur Einzelchats auswerten.", notes_path)
    loaded = load_whatsapp_agent_notes(notes_path)

    assert missing["agent_notes_configured"] is False
    assert saved["agent_notes"] == "Nur Einzelchats auswerten."
    assert saved["external_call_used"] is False
    assert loaded["agent_notes_configured"] is True
    assert loaded["agent_notes"] == "Nur Einzelchats auswerten."


def test_blocked_whatsapp_sender_is_hidden_and_does_not_create_suggestions(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    BlockedSenderRepository(db_path).block_sender(
        source="whatsapp",
        sender="task-number",
        label="Kontakt",
    )

    result = insert_whatsapp_message(
        chat_id="task-chat",
        sender_name="Kontakt",
        sender_number="task-number",
        body="todo fuer Philip",
        received_at="2026-07-09T10:05:00+00:00",
        db_path=db_path,
    )

    assert result.stored is True
    assert read_recent_whatsapp_messages(db_path=db_path) == []
    spam_items = read_recent_whatsapp_messages(db_path=db_path, include_spam=True)
    assert spam_items[0]["is_spam"] == 1

    agent = MessageAgent(db_path=db_path)
    processed = agent.process_unprocessed_whatsapp_messages()

    assert processed.processed_count == 0
    assert processed.message_suggestions_created == 0
    assert processed.task_suggestions_created == 0


def test_resolved_whatsapp_conversation_is_hidden_reversibly(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    insert_whatsapp_message(
        chat_id="resolved-chat",
        sender_name="Kontakt",
        sender_number="resolved-number",
        body="Kannst du das bitte klaeren?",
        received_at="2026-07-15T10:00:00+00:00",
        db_path=db_path,
    )

    result = resolve_whatsapp_conversation(
        "resolved-chat",
        confidence=1.0,
        reason="explicit_completion_reply",
        provider="deterministic",
        db_path=db_path,
    )

    assert result.resolved is True
    assert result.hidden_count == 1
    assert read_recent_whatsapp_messages(db_path=db_path) == []
