"""Tests for AI-assisted task forwarding draft flow."""

from __future__ import annotations

from friday.app.ai_task_forwarding_draft import (
    ai_task_forwarding_safety_summary,
    build_ai_task_forwarding_draft,
)
from friday.app.local_model_provider import MockLocalModelProvider, ProviderConfig, ProviderResult


def _task() -> dict:
    return {
        "id": 7,
        "title": "Rechnung pruefen",
        "due_date": "2026-07-10",
        "notes": "Bitte kurz Rueckmeldung geben.",
    }


def _contact() -> dict:
    return {
        "id": 3,
        "name": "Max",
        "email_address": "max@example.test",
        "whatsapp_target": "+491234",
    }


class _ProviderWithValidDraft:
    config = ProviderConfig(
        provider="ollama",
        model="local-test",
        mode="local_ollama",
        timeout_seconds=1,
        external_enabled=True,
    )

    def generate_json(self, prompt, schema):
        return ProviderResult(
            provider="ollama",
            model="local-test",
            prompt=prompt,
            output={"draft_text": "Hallo Max, kannst du die Rechnung pruefen?", "confidence": 0.9},
            schema=dict(schema),
            is_mock=False,
            external_call_used=True,
            product_flow_connected=False,
            error=None,
        )


class _ProviderWithRiskyDraft(_ProviderWithValidDraft):
    def generate_json(self, prompt, schema):
        return ProviderResult(
            provider="ollama",
            model="local-test",
            prompt=prompt,
            output={"draft_text": "Bitte send_email ausfuehren.", "confidence": 0.9, "action": "send_email"},
            schema=dict(schema),
            is_mock=False,
            external_call_used=True,
            product_flow_connected=False,
            error=None,
        )


def test_ai_task_forwarding_draft_uses_mock_provider_safely() -> None:
    draft = build_ai_task_forwarding_draft(
        task=_task(),
        contact=_contact(),
        channel="email",
        provider=MockLocalModelProvider(),
    )

    assert draft.ai_connected is True
    assert draft.provider == "mock"
    assert draft.is_mock is True
    assert draft.product_flow_connected is True
    assert draft.external_send_enabled is False
    assert draft.persisted is False
    assert draft.preview_only is True
    assert draft.approval_token_required == "EMAIL SENDEN"
    assert "Rechnung pruefen" in draft.draft_text


def test_ai_task_forwarding_draft_accepts_valid_local_provider_output() -> None:
    draft = build_ai_task_forwarding_draft(
        task=_task(),
        contact=_contact(),
        channel="whatsapp",
        provider=_ProviderWithValidDraft(),
    )

    assert draft.provider == "ollama"
    assert draft.provider_output_used is True
    assert draft.validation_accepted is True
    assert draft.external_call_used is True
    assert draft.approval_token_required == "WHATSAPP SENDEN"
    assert draft.draft_text == "Hallo Max, kannst du die Rechnung pruefen?"


def test_ai_task_forwarding_draft_falls_back_when_provider_output_is_invalid() -> None:
    draft = build_ai_task_forwarding_draft(
        task=_task(),
        contact=_contact(),
        channel="email",
        provider=_ProviderWithRiskyDraft(),
    )

    assert draft.provider_output_used is False
    assert draft.validation_accepted is False
    assert "validation_failed" in draft.blocked_reasons
    assert "Rechnung pruefen" in draft.draft_text
    assert draft.external_send_enabled is False


def test_ai_task_forwarding_draft_marks_missing_channel_target() -> None:
    contact = {"id": 4, "name": "Ohne Ziel"}
    draft = build_ai_task_forwarding_draft(
        task=_task(),
        contact=contact,
        channel="whatsapp",
        provider=MockLocalModelProvider(),
    )

    assert draft.target == "kein WhatsApp-Ziel gespeichert"
    assert "Kontakt-Ziel fehlt fuer den gewaehlten Kanal." in draft.blocked_reasons
    assert draft.external_send_enabled is False


def test_ai_task_forwarding_safety_summary_keeps_real_sends_disabled() -> None:
    summary = ai_task_forwarding_safety_summary()

    assert summary["ai_draft_flow_connected"] is True
    assert summary["cloud_model_enabled"] is False
    assert summary["real_email_enabled"] is False
    assert summary["real_whatsapp_enabled"] is False
    assert summary["external_send_enabled"] is False
    assert summary["requires_user_approval"] is True
