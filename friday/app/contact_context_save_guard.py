"""Contact context save guard helpers.

This module validates local contact-context free text before save operations.
It performs no persistence and no external actions.
"""

from __future__ import annotations

from dataclasses import dataclass

from friday.app.sensitive_contact_context_guard import (
    SensitiveContactCategory,
    SensitiveContactContextGuardResult,
    check_sensitive_contact_context,
)


CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE = (
    "Kontakt-Kontext wurde nicht gespeichert, weil ein sensibler Freitext erkannt wurde."
)


@dataclass(frozen=True)
class ContactContextSaveGuardResult:
    """Structured result for contact-context save validation."""

    allowed: bool
    checked_fields: tuple[str, ...]
    blocked_fields: tuple[str, ...]
    blocked_categories: tuple[SensitiveContactCategory, ...]
    message: str | None
    field_results: tuple[SensitiveContactContextGuardResult, ...]
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def check_contact_context_fields_for_save(
    relationship_context: str | None = None,
    notes: str | None = None,
) -> ContactContextSaveGuardResult:
    """Validate local contact-context free-text fields before persistence."""
    field_inputs: tuple[tuple[str, str | None], ...] = (
        ("relationship_context", relationship_context),
        ("notes", notes),
    )

    checked_fields: list[str] = []
    blocked_fields: list[str] = []
    blocked_categories: list[SensitiveContactCategory] = []
    field_results: list[SensitiveContactContextGuardResult] = []

    for field_name, value in field_inputs:
        if value is None or not value.strip():
            continue

        checked_fields.append(field_name)
        result = check_sensitive_contact_context(value)
        field_results.append(result)

        if not result.allowed:
            blocked_fields.append(field_name)
            blocked_categories.extend(result.blocked_categories)

    unique_blocked_categories = tuple(dict.fromkeys(blocked_categories))
    allowed = not blocked_fields

    return ContactContextSaveGuardResult(
        allowed=allowed,
        checked_fields=tuple(checked_fields),
        blocked_fields=tuple(blocked_fields),
        blocked_categories=unique_blocked_categories,
        message=None if allowed else CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE,
        field_results=tuple(field_results),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
