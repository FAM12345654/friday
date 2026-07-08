"""Contact context prompt draft flow helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday.app.contact_context_preview import ContactType
from friday.app.contact_context_prompt_input_parser import (
    ContactPromptInputParseResult,
    parse_contact_prompt_input,
)
from friday.app.contact_context_prompt_ui_renderer import (
    CONTACT_PROMPT_INVALID_MESSAGE,
    ContactPromptUIRender,
    render_contact_prompt_ui,
)

ContactPromptDraftFlowStatus = Literal[
    "blocked",
    "rendered",
    "selected",
    "skipped",
    "invalid",
]


@dataclass(frozen=True)
class ContactPromptDraftFlowResult:
    """Pure draft-flow result for contact-context prompt handling."""

    display_name: str
    source_context: str
    status: ContactPromptDraftFlowStatus
    rendered: ContactPromptUIRender
    parsed: ContactPromptInputParseResult | None
    selected_contact_type: ContactType | None
    skipped: bool
    error_message: str | None
    prompt_rendered: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def prepare_contact_prompt_draft_flow(
    display_name: str,
    contact_type: str,
    source_context: str,
    recently_skipped: bool = False,
    sensitive_or_disallowed: bool = False,
) -> ContactPromptDraftFlowResult:
    """Prepare a local-only draft flow without reading external input."""
    rendered = render_contact_prompt_ui(
        display_name=display_name,
        contact_type=contact_type,
        source_context=source_context,
        recently_skipped=recently_skipped,
        sensitive_or_disallowed=sensitive_or_disallowed,
    )

    status: ContactPromptDraftFlowStatus = (
        "rendered" if rendered.should_render else "blocked"
    )

    return ContactPromptDraftFlowResult(
        display_name=(display_name or "").strip(),
        source_context=(source_context or "").strip().lower() or "unklar",
        status=status,
        rendered=rendered,
        parsed=None,
        selected_contact_type=None,
        skipped=False,
        error_message=None,
        prompt_rendered=rendered.should_render,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def apply_contact_prompt_draft_input(
    prepared: ContactPromptDraftFlowResult,
    raw_input: str | None,
) -> ContactPromptDraftFlowResult:
    """Apply user input to a prepared draft flow result."""
    if prepared.status == "blocked":
        return prepared

    parsed = parse_contact_prompt_input(raw_input)

    if parsed.action == "select_contact_type":
        status: ContactPromptDraftFlowStatus = "selected"
        selected_contact_type = parsed.contact_type
        skipped = False
        error_message = None
    elif parsed.action == "skip":
        status = "skipped"
        selected_contact_type = None
        skipped = True
        error_message = None
    else:
        status = "invalid"
        selected_contact_type = None
        skipped = False
        error_message = parsed.error_message or CONTACT_PROMPT_INVALID_MESSAGE

    return ContactPromptDraftFlowResult(
        display_name=prepared.display_name,
        source_context=prepared.source_context,
        status=status,
        rendered=prepared.rendered,
        parsed=parsed,
        selected_contact_type=selected_contact_type,
        skipped=skipped,
        error_message=error_message,
        prompt_rendered=prepared.prompt_rendered,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
