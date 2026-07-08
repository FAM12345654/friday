"""Contact context prompt candidate model helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday.app.contact_context_preview import normalize_contact_name

PromptStatus = Literal["allowed", "not_allowed", "ask_later", "skipped"]
ContactPromptReason = Literal[
    "unknown_contact_in_review",
    "explicit_person_edit",
    "task_from_unknown_sender",
    "explicit_user_request",
    "known_contact",
    "no_active_context",
    "recently_skipped",
    "sensitive_or_disallowed",
]


@dataclass(frozen=True)
class ContactPromptCandidate:
    display_name: str
    normalized_name: str
    source_context: str
    status: PromptStatus
    reason: ContactPromptReason
    question: str | None
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


ALLOWED_SOURCE_CONTEXTS: set[str] = {
    "nachrichten_review",
    "person_bearbeiten",
    "aufgabe_aus_nachricht",
    "nutzeranfrage",
}

DISALLOWED_SOURCE_CONTEXTS: set[str] = {
    "app_start",
    "automatisch_jede_nachricht",
    "unklar",
}


def build_contact_prompt_question(display_name: str) -> str:
    clean_name = (display_name or "").strip() or "diese Person"
    return f"Wer ist {clean_name} für dich?"


def should_create_contact_prompt_candidate(
    display_name: str,
    contact_type: str,
    source_context: str,
    recently_skipped: bool = False,
    sensitive_or_disallowed: bool = False,
) -> ContactPromptCandidate:
    clean_name = (display_name or "").strip()
    normalized_name = normalize_contact_name(clean_name)
    clean_contact_type = (contact_type or "").strip().lower()
    clean_source = (source_context or "").strip().lower()

    normalized_source = clean_source or "unklar"

    if sensitive_or_disallowed:
        return ContactPromptCandidate(
            display_name=clean_name,
            normalized_name=normalized_name,
            source_context=normalized_source,
            status="not_allowed",
            reason="sensitive_or_disallowed",
            question=None,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    if recently_skipped:
        return ContactPromptCandidate(
            display_name=clean_name,
            normalized_name=normalized_name,
            source_context=normalized_source,
            status="skipped",
            reason="recently_skipped",
            question=None,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    if clean_contact_type and clean_contact_type != "unbekannt":
        return ContactPromptCandidate(
            display_name=clean_name,
            normalized_name=normalized_name,
            source_context=normalized_source,
            status="not_allowed",
            reason="known_contact",
            question=None,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    if (
        normalized_source in DISALLOWED_SOURCE_CONTEXTS
        or normalized_source not in ALLOWED_SOURCE_CONTEXTS
    ):
        return ContactPromptCandidate(
            display_name=clean_name,
            normalized_name=normalized_name,
            source_context=normalized_source,
            status="not_allowed",
            reason="no_active_context",
            question=None,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    reason_by_source: dict[str, ContactPromptReason] = {
        "nachrichten_review": "unknown_contact_in_review",
        "person_bearbeiten": "explicit_person_edit",
        "aufgabe_aus_nachricht": "task_from_unknown_sender",
        "nutzeranfrage": "explicit_user_request",
    }

    return ContactPromptCandidate(
        display_name=clean_name,
        normalized_name=normalized_name,
        source_context=normalized_source,
        status="allowed",
        reason=reason_by_source[normalized_source],
        question=build_contact_prompt_question(clean_name),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
