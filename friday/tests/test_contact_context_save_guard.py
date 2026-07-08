"""Tests for contact-context save guard helpers."""

from __future__ import annotations

from friday.app.contact_context_save_guard import (
    CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE,
    check_contact_context_fields_for_save,
)


def test_contact_context_save_guard_allows_harmless_context() -> None:
    result = check_contact_context_fields_for_save(
        relationship_context="Projekt Alpha",
    )

    assert result.allowed is True
    assert result.checked_fields == ("relationship_context",)
    assert result.blocked_fields == ()
    assert result.message is None


def test_contact_context_save_guard_blocks_sensitive_context() -> None:
    result = check_contact_context_fields_for_save(
        relationship_context="hat medizinische Diagnose",
    )

    assert result.allowed is False
    assert "relationship_context" in result.blocked_fields
    assert "health" in result.blocked_categories
    assert result.message == CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE


def test_contact_context_save_guard_checks_notes_if_available() -> None:
    result = check_contact_context_fields_for_save(notes="Parteimitglied")

    assert result.allowed is False
    assert "notes" in result.blocked_fields
    assert "politics" in result.blocked_categories


def test_contact_context_save_guard_allows_empty_fields() -> None:
    result = check_contact_context_fields_for_save()

    assert result.allowed is True
    assert result.checked_fields == ()
    assert result.blocked_fields == ()


def test_contact_context_save_guard_has_safe_flags() -> None:
    result = check_contact_context_fields_for_save(
        relationship_context="Projekt Alpha",
    )

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False
