"""Tests for local email draft-only model."""

from __future__ import annotations

from friday.app.email_draft_model import (
    build_email_draft,
    normalize_email_draft_text,
)
from friday.app.email_draft_renderer import render_email_draft_preview


def test_build_email_draft_creates_preview_only_draft() -> None:
    draft = build_email_draft(
        recipient_label="Max Mustermann",
        subject="Rueckmeldung",
        body="Hallo Max, danke fuer deine Nachricht.",
        source_context="message_review",
    )

    assert draft.recipient_label == "Max Mustermann"
    assert draft.subject == "Rueckmeldung"
    assert draft.status == "drafted"
    assert draft.blocked_reasons == ()
    assert draft.preview_only is True
    assert draft.provider_used is False
    assert draft.external_send_enabled is False
    assert draft.persisted is False
    assert draft.external_lookup_used is False


def test_build_email_draft_uses_safe_defaults_for_recipient_and_subject() -> None:
    draft = build_email_draft(
        recipient_label="  ",
        subject="",
        body="Kurzer lokaler Entwurf.",
        source_context="  ",
    )

    assert draft.recipient_label == "Unbekannter Kontakt"
    assert draft.subject == "Ohne Betreff"
    assert draft.source_context == "local_preview"
    assert draft.status == "drafted"


def test_build_email_draft_blocks_empty_body() -> None:
    draft = build_email_draft(
        recipient_label="Max",
        subject="Hallo",
        body="   ",
    )

    assert draft.status == "blocked"
    assert "E-Mail-Entwurf braucht einen lokalen Nachrichtentext." in draft.blocked_reasons


def test_build_email_draft_blocks_sensitive_content() -> None:
    draft = build_email_draft(
        recipient_label="Max",
        subject="Diagnose",
        body="Bitte die Therapie besprechen.",
    )

    assert draft.status == "blocked"
    assert any("sensible Kategorie" in reason for reason in draft.blocked_reasons)
    assert any("health" in reason for reason in draft.blocked_reasons)


def test_build_email_draft_blocks_unknown_delivery_status() -> None:
    draft = build_email_draft(
        recipient_label="Max",
        subject="Hallo",
        body="Nur lokaler Text.",
        status="delivery_done",
    )

    assert draft.status == "blocked"
    assert "Unbekannter E-Mail-Draft-Status." in draft.blocked_reasons
    assert draft.external_send_enabled is False


def test_build_email_draft_blocks_unknown_status() -> None:
    draft = build_email_draft(
        recipient_label="Max",
        subject="Hallo",
        body="Nur lokaler Text.",
        status="waiting",
    )

    assert draft.status == "blocked"
    assert "Unbekannter E-Mail-Draft-Status." in draft.blocked_reasons


def test_render_email_draft_preview_shows_local_no_send_notice() -> None:
    draft = build_email_draft(
        recipient_label="Max",
        subject="Rueckmeldung",
        body="Hallo Max.",
    )

    preview = render_email_draft_preview(draft)

    assert "E-Mail-Entwurf (lokal, nicht gesendet)" in preview
    assert "An: Max" in preview
    assert "Betreff: Rueckmeldung" in preview
    assert "Hallo Max." in preview
    assert "Es wurde nichts gesendet." in preview
    assert "Kein E-Mail-Provider ist verbunden." in preview
    assert "Dies ist nur eine lokale Vorschau." in preview


def test_render_email_draft_preview_includes_blocked_reasons() -> None:
    draft = build_email_draft(
        recipient_label="Max",
        subject="Hallo",
        body="",
    )

    preview = render_email_draft_preview(draft)

    assert "Status: blocked" in preview
    assert "Blockiert:" in preview
    assert "E-Mail-Entwurf braucht einen lokalen Nachrichtentext." in preview


def test_normalize_email_draft_text_collapses_whitespace() -> None:
    assert normalize_email_draft_text("  Hallo   Max  ") == "Hallo Max"


def test_build_email_draft_blocks_credential_markers() -> None:
    draft = build_email_draft(
        recipient_label="Max",
        subject="Zugang",
        body="Bitte api_key nicht teilen.",
    )

    assert draft.status == "blocked"
    assert any("Zugangsdaten" in reason for reason in draft.blocked_reasons)


def test_email_draft_model_contains_no_delivery_status_literals() -> None:
    from pathlib import Path

    content = Path("friday/app/email_draft_model.py").read_text(encoding="utf-8")

    assert '"sent"' not in content
    assert '"queued"' not in content
    assert '"scheduled_send"' not in content
