"""Tests for the local sensitive contact-context guard."""

from __future__ import annotations

from friday.app.sensitive_contact_context_guard import (
    check_sensitive_contact_context,
    normalize_sensitive_guard_text,
)


def test_sensitive_guard_allows_empty_text() -> None:
    assert check_sensitive_contact_context(None).allowed is True
    assert check_sensitive_contact_context("").allowed is True
    assert check_sensitive_contact_context("   ").allowed is True


def test_sensitive_guard_allows_harmless_work_context() -> None:
    allowed_texts = [
        "Projekt Alpha",
        "arbeitet mit mir an Website",
        "Kunde fuer Angebot",
        "Kollege aus Buchhaltung",
        "Dienstleister fuer Heizung",
        "Freund aus Verein",
        "Mitarbeiter im Lager",
    ]

    for text in allowed_texts:
        result = check_sensitive_contact_context(text)
        assert result.allowed is True
        assert result.blocked_categories == ()


def test_sensitive_guard_blocks_health_context() -> None:
    result = check_sensitive_contact_context("Hat eine Diagnose Depression erwähnt.")

    assert result.allowed is False
    assert "health" in result.blocked_categories


def test_sensitive_guard_blocks_religion_context() -> None:
    result = check_sensitive_contact_context("Kontakt aus der Kirche, Religion bekannt.")

    assert result.allowed is False
    assert "religion" in result.blocked_categories


def test_sensitive_guard_blocks_political_context() -> None:
    result = check_sensitive_contact_context("Ist Parteimitglied in einer politischen Partei.")

    assert result.allowed is False
    assert "politics" in result.blocked_categories


def test_sensitive_guard_blocks_union_context() -> None:
    result = check_sensitive_contact_context("Ist Gewerkschaftsmitglied.")

    assert result.allowed is False
    assert "trade_union" in result.blocked_categories


def test_sensitive_guard_blocks_criminal_record_context() -> None:
    result = check_sensitive_contact_context("Private Notiz: Vorstrafe bekannt.")

    assert result.allowed is False
    assert "criminal_record" in result.blocked_categories


def test_sensitive_guard_blocks_financial_private_context() -> None:
    result = check_sensitive_contact_context("Privatinsolvenz und Schulden wurden erwähnt.")

    assert result.allowed is False
    assert "financial_private" in result.blocked_categories


def test_sensitive_guard_blocks_multiple_categories() -> None:
    result = check_sensitive_contact_context(
        "Parteimitglied, Religion bekannt und Diagnose erwähnt."
    )

    assert result.allowed is False
    assert "politics" in result.blocked_categories
    assert "religion" in result.blocked_categories
    assert "health" in result.blocked_categories


def test_sensitive_guard_has_safe_flags() -> None:
    result = check_sensitive_contact_context("Projekt Alpha")

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_sensitive_guard_normalizes_text() -> None:
    assert normalize_sensitive_guard_text("  Projekt   Alpha  ") == "projekt alpha"
    result = check_sensitive_contact_context("  DIAGNOSE   ")

    assert result.text == "diagnose"
    assert result.allowed is False
    assert "health" in result.blocked_categories
