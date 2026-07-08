"""In-memory session suppression helpers for contact prompt flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday.app.contact_context_preview import normalize_contact_name

ContactPromptSuppressionStatus = Literal["skipped", "ask_later", "suppressed"]


@dataclass(frozen=True)
class ContactPromptSuppressionEntry:
    """A non-persistent suppression marker for one contact/context pair in session."""

    normalized_name: str
    source_context: str
    status: ContactPromptSuppressionStatus
    reason: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def normalize_suppression_key(
    display_name: str,
    source_context: str,
) -> tuple[str, str]:
    """Normalize a display name and context tuple key for suppression state."""

    normalized_name = normalize_contact_name(display_name) or "unbekannt"
    normalized_context = (source_context or "").strip().lower() or "unklar"
    return (normalized_name, normalized_context)


def _without_matching_entry(
    entries: tuple[ContactPromptSuppressionEntry, ...],
    normalized_name: str,
    source_context: str,
) -> tuple[ContactPromptSuppressionEntry, ...]:
    return tuple(
        entry
        for entry in entries
        if not (
            entry.normalized_name == normalized_name
            and entry.source_context == source_context
        )
    )


def mark_contact_prompt_skipped(
    display_name: str,
    source_context: str,
    entries: tuple[ContactPromptSuppressionEntry, ...],
) -> tuple[ContactPromptSuppressionEntry, ...]:
    """Mark a contact prompt as skipped in the current session state.

    The returned tuple is a new immutable state snapshot without mutating input.
    """

    normalized_name, normalized_context = normalize_suppression_key(
        display_name=display_name,
        source_context=source_context,
    )

    remaining = _without_matching_entry(
        entries=entries,
        normalized_name=normalized_name,
        source_context=normalized_context,
    )

    skipped = ContactPromptSuppressionEntry(
        normalized_name=normalized_name,
        source_context=normalized_context,
        status="skipped",
        reason="user_skipped",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )

    return tuple(remaining) + (skipped,)


def is_contact_prompt_suppressed(
    display_name: str,
    source_context: str,
    entries: tuple[ContactPromptSuppressionEntry, ...],
) -> bool:
    """Return whether a prompt should be suppressed in this session scope."""

    normalized_name, normalized_context = normalize_suppression_key(
        display_name=display_name,
        source_context=source_context,
    )

    for entry in entries:
        if (
            entry.normalized_name == normalized_name
            and entry.source_context == normalized_context
            and entry.status in {"skipped", "suppressed"}
        ):
            return True

    return False


def clear_contact_prompt_suppression(
    display_name: str,
    source_context: str,
    entries: tuple[ContactPromptSuppressionEntry, ...],
) -> tuple[ContactPromptSuppressionEntry, ...]:
    """Clear suppression entry for a single name/context key."""

    normalized_name, normalized_context = normalize_suppression_key(
        display_name=display_name,
        source_context=source_context,
    )

    return _without_matching_entry(
        entries=entries,
        normalized_name=normalized_name,
        source_context=normalized_context,
    )
