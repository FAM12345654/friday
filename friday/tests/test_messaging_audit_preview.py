"""Tests for side-effect-free messaging audit previews."""

from __future__ import annotations

import pytest

from friday.app.messaging_audit_preview import build_messaging_audit_preview


def test_build_messaging_audit_preview_contains_core_fields() -> None:
    preview = build_messaging_audit_preview(
        task_id=7,
        task_title="Rechnung pruefen",
        contact_id=3,
        contact_name="Lena",
        channel="email",
        target="lena@example.test",
        draft_text="Bitte uebernehmen.",
        approval_token="EMAIL SENDEN",
        mode="mock",
        status="approval_accepted",
        created_at="2026-07-09T10:00:00+00:00",
    )

    assert preview.task_id == 7
    assert preview.task_title == "Rechnung pruefen"
    assert preview.contact_name == "Lena"
    assert preview.channel == "email"
    assert preview.target == "lena@example.test"
    assert preview.approval_token == "EMAIL SENDEN"
    assert preview.mode == "mock"
    assert preview.status == "approval_accepted"


def test_messaging_audit_preview_is_not_persisted_and_does_not_send() -> None:
    preview = build_messaging_audit_preview(
        task_id=None,
        task_title="Aufgabe",
        contact_id=None,
        contact_name="Kontakt",
        channel="whatsapp",
        target="+491234",
        draft_text="Hallo",
        approval_token="WHATSAPP SENDEN",
    )

    assert preview.persisted is False
    assert preview.external_send_enabled is False
    assert "Nothing was sent" in preview.notes


def test_messaging_audit_preview_rejects_invalid_channel() -> None:
    with pytest.raises(ValueError, match="Unsupported messaging channel"):
        build_messaging_audit_preview(
            task_id=None,
            task_title="Aufgabe",
            contact_id=None,
            contact_name="Kontakt",
            channel="sms",  # type: ignore[arg-type]
            target="123",
            draft_text="Hallo",
            approval_token=None,
        )


def test_messaging_audit_preview_rejects_empty_draft() -> None:
    with pytest.raises(ValueError, match="draft_text"):
        build_messaging_audit_preview(
            task_id=None,
            task_title="Aufgabe",
            contact_id=None,
            contact_name="Kontakt",
            channel="email",
            target="test@example.test",
            draft_text="   ",
            approval_token=None,
        )


def test_messaging_audit_preview_blocks_external_id_outside_live_mode() -> None:
    with pytest.raises(ValueError, match="external_message_id"):
        build_messaging_audit_preview(
            task_id=None,
            task_title="Aufgabe",
            contact_id=None,
            contact_name="Kontakt",
            channel="email",
            target="test@example.test",
            draft_text="Hallo",
            approval_token="EMAIL SENDEN",
            mode="mock",
            status="simulated",
            external_message_id="provider-123",
        )
