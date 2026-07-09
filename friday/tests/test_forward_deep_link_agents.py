"""Tests for preview-only forwarding deep-link agents."""

from __future__ import annotations

from friday.agents.email_forward_agent import build_email_forward_preview
from friday.agents.whatsapp_forward_agent import (
    build_whatsapp_forward_preview,
    normalize_whatsapp_target,
)


def test_email_forward_preview_builds_encoded_mailto_link() -> None:
    result = build_email_forward_preview(
        draft_text="Hallo Max,\nbitte Aufgabe prüfen: äöüß",
        email_address="max@example.test",
        subject="Aufgabe prüfen",
    )

    assert result.sent is False
    assert result.preview_only is True
    assert result.deep_link is not None
    assert result.deep_link.startswith("mailto:max@example.test?")
    assert "Aufgabe%20pr%C3%BCfen" in result.deep_link
    assert "%C3%A4%C3%B6%C3%BC%C3%9F" in result.deep_link


def test_whatsapp_forward_preview_builds_encoded_wa_me_link() -> None:
    result = build_whatsapp_forward_preview(
        draft_text="Bitte prüfen:\nRechnung äöüß",
        whatsapp_target="+49 151 12345678",
    )

    assert result.normalized_target == "4915112345678"
    assert result.deep_link is not None
    assert result.deep_link.startswith("https://wa.me/4915112345678?")
    assert "%C3%A4%C3%B6%C3%BC%C3%9F" in result.deep_link
    assert result.sent is False


def test_whatsapp_forward_preview_rejects_non_international_local_number() -> None:
    result = build_whatsapp_forward_preview(
        draft_text="Hallo",
        whatsapp_target="0151 123456",
    )

    assert normalize_whatsapp_target("0151 123456") is None
    assert result.deep_link is None
    assert "internationalen Format" in result.message
