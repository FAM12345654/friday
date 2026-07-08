"""Contact context prompt UI renderer helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from friday.app.contact_context_prompt_preview import (
    ContactPromptPreview,
    build_contact_prompt_preview,
)

CONTACT_PROMPT_OPTION_LABELS: tuple[tuple[str, str], ...] = (
    ("1", "Kunde"),
    ("2", "Kollege"),
    ("3", "Mitarbeiter"),
    ("4", "Familie"),
    ("5", "Freund"),
    ("6", "Dienstleister"),
    ("7", "Sonstiges"),
    ("8", "Überspringen"),
)

CONTACT_PROMPT_SKIP_INPUTS: tuple[str, ...] = (
    "",
    "8",
    "z",
    "zurück",
    "skip",
    "überspringen",
)

CONTACT_PROMPT_INVALID_MESSAGE = "Ungültige Auswahl. Bitte erneut versuchen."


@dataclass(frozen=True)
class ContactPromptUIRender:
    prompt_preview: ContactPromptPreview
    title: str
    question: str | None
    option_labels: Tuple[tuple[str, str], ...]
    skip_inputs: Tuple[str, ...]
    invalid_message: str
    should_render: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def build_contact_prompt_text(display_name: str) -> str:
    clean_name = (display_name or "").strip() or "diese Person"
    return (
        f"Kontakt-Kontext für {clean_name}\n\n"
        f"Wer ist {clean_name} für dich?\n"
        "1. Kunde\n"
        "2. Kollege\n"
        "3. Mitarbeiter\n"
        "4. Familie\n"
        "5. Freund\n"
        "6. Dienstleister\n"
        "7. Sonstiges\n"
        "8. Überspringen\n\n"
        "Auswahl (1-8):"
    )


def render_contact_prompt_ui(
    display_name: str,
    contact_type: str,
    source_context: str,
    recently_skipped: bool = False,
    sensitive_or_disallowed: bool = False,
) -> ContactPromptUIRender:
    prompt_preview = build_contact_prompt_preview(
        display_name=display_name,
        contact_type=contact_type,
        source_context=source_context,
        recently_skipped=recently_skipped,
        sensitive_or_disallowed=sensitive_or_disallowed,
    )

    clean_name = (display_name or "").strip() or "diese Person"
    question = (
        build_contact_prompt_text(clean_name) if prompt_preview.should_ask else None
    )

    return ContactPromptUIRender(
        prompt_preview=prompt_preview,
        title=f"Kontakt-Kontext für {clean_name}",
        question=question,
        option_labels=CONTACT_PROMPT_OPTION_LABELS,
        skip_inputs=CONTACT_PROMPT_SKIP_INPUTS,
        invalid_message=CONTACT_PROMPT_INVALID_MESSAGE,
        should_render=prompt_preview.should_ask,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
