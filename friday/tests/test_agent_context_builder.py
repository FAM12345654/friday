"""Tests for local agent context assembly from user-editable notes."""

from __future__ import annotations

from types import SimpleNamespace

from friday.app.account_policy_store import AccountPolicy
from friday.app.agent_context_builder import build_agent_context


def _policy() -> AccountPolicy:
    return AccountPolicy(
        id=1,
        provider="outlook_ics",
        label="team-hampejs PH",
        role="source",
        access="read",
        include_filters={"title_contains": ["PH"]},
        exclude_filters={},
        notes="PH bedeutet Dienst und soll als belegt gelten.",
        enabled=True,
        created_at="2026-07-09T00:00:00+00:00",
        transform={"fixed_daily_window": {"start": "08:00", "end": "18:00"}},
    )


def test_build_agent_context_combines_local_notes_without_external_action() -> None:
    context = build_agent_context(
        contact={"name": "Max", "contact_type": "arbeit", "notes": "Mag kurze Nachrichten."},
        channel="email",
        policies=[_policy()],
        email_account=SimpleNamespace(agent_notes="E-Mails bitte formell."),
        whatsapp_notes={"agent_notes": "WhatsApp bitte locker."},
    )

    assert context.startswith("Lokaler Agent-Kontext")
    assert "PH bedeutet Dienst" in context
    assert "E-Mail-Konto-Notiz" in context
    assert "E-Mails bitte formell." in context
    assert "Kontakt-Notiz fuer Max" in context
    assert "Mag kurze Nachrichten." in context
    assert "WhatsApp-Agent-Notiz" not in context


def test_build_agent_context_filters_by_whatsapp_channel() -> None:
    context = build_agent_context(
        contact=None,
        channel="whatsapp",
        policies=[],
        email_account=SimpleNamespace(agent_notes="Nicht fuer WhatsApp."),
        whatsapp_notes={"agent_notes": "Du darfst Emojis vermeiden."},
    )

    assert "WhatsApp-Agent-Notiz" in context
    assert "Du darfst Emojis vermeiden." in context
    assert "Nicht fuer WhatsApp." not in context


def test_build_agent_context_includes_customer_betreuer() -> None:
    context = build_agent_context(
        contact={"name": "Kunde Alpha", "contact_type": "kunde", "betreuer": "alex"},
        channel="email",
        policies=[],
        email_account=SimpleNamespace(agent_notes=""),
        whatsapp_notes={"agent_notes": ""},
    )

    assert "Kunde Kunde Alpha, Betreuer: Alex" in context
    assert "Kontaktart: kunde" in context


def test_build_agent_context_returns_empty_string_when_no_notes_exist() -> None:
    assert (
        build_agent_context(
            contact={},
            channel="email",
            policies=[],
            email_account=SimpleNamespace(agent_notes=""),
            whatsapp_notes={"agent_notes": ""},
        )
        == ""
    )
