"""Contact context prompt input parser helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday.app.contact_context_preview import ContactType
from friday.app.contact_context_prompt_ui_renderer import (
    CONTACT_PROMPT_INVALID_MESSAGE,
    CONTACT_PROMPT_SKIP_INPUTS,
)


ContactPromptInputAction = Literal["select_contact_type", "skip", "invalid"]

CONTACT_PROMPT_INPUT_TO_TYPE: dict[str, ContactType] = {
    "1": "kunde",
    "2": "kollege",
    "3": "mitarbeiter",
    "4": "familie",
    "5": "freund",
    "6": "dienstleister",
    "7": "sonstiges",
}


@dataclass(frozen=True)
class ContactPromptInputParseResult:
    raw_input: str
    normalized_input: str
    action: ContactPromptInputAction
    contact_type: ContactType | None
    error_message: str | None
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def normalize_contact_prompt_input(raw_input: str | None) -> str:
    return (raw_input or "").strip().lower()


def parse_contact_prompt_input(raw_input: str | None) -> ContactPromptInputParseResult:
    normalized = normalize_contact_prompt_input(raw_input)
    raw_value = raw_input or ""

    if normalized in CONTACT_PROMPT_SKIP_INPUTS:
        return ContactPromptInputParseResult(
            raw_input=raw_value,
            normalized_input=normalized,
            action="skip",
            contact_type=None,
            error_message=None,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    selected_type = CONTACT_PROMPT_INPUT_TO_TYPE.get(normalized)
    if selected_type is not None:
        return ContactPromptInputParseResult(
            raw_input=raw_value,
            normalized_input=normalized,
            action="select_contact_type",
            contact_type=selected_type,
            error_message=None,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    return ContactPromptInputParseResult(
        raw_input=raw_value,
        normalized_input=normalized,
        action="invalid",
        contact_type=None,
        error_message=CONTACT_PROMPT_INVALID_MESSAGE,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
