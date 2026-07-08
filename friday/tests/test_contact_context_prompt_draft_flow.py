"""Tests for the local contact context prompt draft flow model."""

from __future__ import annotations

import pytest

from friday.app.contact_context_prompt_draft_flow import (
    ContactPromptDraftFlowStatus,
    apply_contact_prompt_draft_input,
    prepare_contact_prompt_draft_flow,
)
from friday.app.contact_context_prompt_input_parser import CONTACT_PROMPT_INVALID_MESSAGE


def test_prepare_contact_prompt_draft_flow_renders_allowed_prompt() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert prepared.status == "rendered"
    assert prepared.prompt_rendered is True
    assert prepared.rendered.should_render is True
    assert prepared.parsed is None
    assert prepared.selected_contact_type is None
    assert prepared.preview_only is True
    assert prepared.persisted is False
    assert prepared.external_lookup_used is False


def test_prepare_contact_prompt_draft_flow_blocks_known_contact() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="kunde",
        source_context="nachrichten_review",
    )

    assert prepared.status == "blocked"
    assert prepared.prompt_rendered is False
    assert prepared.rendered.prompt_preview.candidate.reason == "known_contact"


def test_apply_contact_prompt_draft_input_selects_contact_type() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )
    applied = apply_contact_prompt_draft_input(prepared, "1")

    assert applied.status == "selected"
    assert applied.selected_contact_type == "kunde"
    assert applied.skipped is False
    assert applied.error_message is None
    assert applied.parsed is not None
    assert applied.parsed.contact_type == "kunde"


@pytest.mark.parametrize(
    "selection",
    ["1", "2", "3", "4", "5", "6", "7"],
)
def test_apply_contact_prompt_draft_input_selects_contact_type_for_all_numeric_options(
    selection: str,
) -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )
    applied = apply_contact_prompt_draft_input(prepared, selection)

    assert applied.status == "selected"
    assert applied.selected_contact_type is not None
    assert applied.skipped is False
    assert applied.error_message is None
    assert applied.parsed is not None
    assert applied.parsed.contact_type in {
        "kunde",
        "kollege",
        "mitarbeiter",
        "familie",
        "freund",
        "dienstleister",
        "sonstiges",
    }


def test_apply_contact_prompt_draft_input_skips() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )
    applied = apply_contact_prompt_draft_input(prepared, "8")

    assert applied.status == "skipped"
    assert applied.selected_contact_type is None
    assert applied.skipped is True
    assert applied.error_message is None


def test_apply_contact_prompt_draft_input_handles_invalid() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )
    applied = apply_contact_prompt_draft_input(prepared, "9")

    assert applied.status == "invalid"
    assert applied.error_message == CONTACT_PROMPT_INVALID_MESSAGE
    assert applied.selected_contact_type is None
    assert applied.skipped is False


def test_apply_contact_prompt_draft_input_does_not_process_blocked_flow() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="kunde",
        source_context="nachrichten_review",
    )
    applied = apply_contact_prompt_draft_input(prepared, "1")

    assert applied == prepared
    assert applied.parsed is None
    assert applied.selected_contact_type is None


def test_contact_prompt_draft_flow_has_safe_flags() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert prepared.preview_only is True
    assert prepared.persisted is False
    assert prepared.external_lookup_used is False
    assert prepared.rendered.preview_only is True
    assert prepared.rendered.persisted is False
    assert prepared.rendered.external_lookup_used is False
    assert prepared.rendered.prompt_preview.preview_only is True
    assert prepared.rendered.prompt_preview.persisted is False
    assert prepared.rendered.prompt_preview.external_lookup_used is False


def test_contact_prompt_draft_flow_treats_delete_confirmation_as_invalid() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )
    applied = apply_contact_prompt_draft_input(prepared, "JA")

    assert applied.status == "invalid"
    assert applied.selected_contact_type is None
    assert applied.error_message == CONTACT_PROMPT_INVALID_MESSAGE
    assert applied.parsed is not None
    assert applied.parsed.contact_type is None


def test_apply_contact_prompt_draft_input_keeps_status_model_values() -> None:
    prepared = prepare_contact_prompt_draft_flow(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    statuses: tuple[ContactPromptDraftFlowStatus, ...] = (
        "rendered",
        "selected",
        "skipped",
        "invalid",
        "blocked",
    )

    assert prepared.status in statuses
    assert apply_contact_prompt_draft_input(prepared, "1").status == "selected"
    assert apply_contact_prompt_draft_input(prepared, "8").status == "skipped"
    assert apply_contact_prompt_draft_input(prepared, "9").status == "invalid"
