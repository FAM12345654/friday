"""Tests for conservative local WhatsApp completion detection."""

from __future__ import annotations

from friday.app.whatsapp_inbox_store import insert_whatsapp_message, read_recent_whatsapp_messages
from friday.app.whatsapp_resolution import classify_and_resolve_whatsapp_reply
from friday.storage.database import setup_local_database


def _seed(tmp_path):
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    insert_whatsapp_message(
        chat_id="chat-1",
        sender_name="Kontakt",
        sender_number="number-1",
        body="Kannst du das bitte erledigen?",
        received_at="2026-07-15T10:00:00+00:00",
        db_path=db_path,
    )
    return db_path


def test_explicit_completion_hides_conversation(tmp_path) -> None:
    db_path = _seed(tmp_path)
    result = classify_and_resolve_whatsapp_reply(
        chat_id="chat-1",
        reply_text="Das ist erledigt.",
        db_path=db_path,
    )
    assert result.resolved is True
    assert result.confidence == 1.0
    assert read_recent_whatsapp_messages(db_path=db_path) == []


def test_negated_completion_keeps_conversation(tmp_path) -> None:
    db_path = _seed(tmp_path)
    result = classify_and_resolve_whatsapp_reply(
        chat_id="chat-1",
        reply_text="Das ist noch nicht erledigt.",
        db_path=db_path,
    )
    assert result.resolved is False
    assert len(read_recent_whatsapp_messages(db_path=db_path)) == 1
