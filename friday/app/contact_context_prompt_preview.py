"""Contact context prompt preview composition helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from friday.app.contact_context_preview import (
    ContactContextPreview,
    build_contact_context_preview,
)
from friday.app.contact_context_prompt_candidate import (
    ContactPromptCandidate,
    should_create_contact_prompt_candidate,
)


DEFAULT_CONTACT_TYPE_OPTIONS: tuple[str, ...] = (
    "kunde",
    "kollege",
    "mitarbeiter",
    "familie",
    "freund",
    "dienstleister",
    "sonstiges",
    "überspringen",
)


@dataclass(frozen=True)
class ContactPromptPreview:
    candidate: ContactPromptCandidate
    context_preview: ContactContextPreview
    prompt_options: tuple[str, ...]
    should_ask: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def build_contact_prompt_preview(
    display_name: str,
    contact_type: str,
    source_context: str,
    recently_skipped: bool = False,
    sensitive_or_disallowed: bool = False,
    nickname: str | None = None,
    relationship_context: str | None = None,
) -> ContactPromptPreview:
    candidate = should_create_contact_prompt_candidate(
        display_name=display_name,
        contact_type=contact_type,
        source_context=source_context,
        recently_skipped=recently_skipped,
        sensitive_or_disallowed=sensitive_or_disallowed,
    )
    context_preview = build_contact_context_preview(
        display_name=display_name,
        contact_type=contact_type,
        nickname=nickname,
        relationship_context=relationship_context,
        source_context=source_context,
    )
    should_ask = candidate.status == "allowed"

    return ContactPromptPreview(
        candidate=candidate,
        context_preview=context_preview,
        prompt_options=DEFAULT_CONTACT_TYPE_OPTIONS,
        should_ask=should_ask,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
