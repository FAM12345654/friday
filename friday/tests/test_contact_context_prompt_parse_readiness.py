"""Compatibility checks between contact context prompt renderer and parser."""

from friday.app.contact_context_prompt_input_parser import parse_contact_prompt_input
from friday.app.contact_context_prompt_ui_renderer import (
    CONTACT_PROMPT_INVALID_MESSAGE,
    CONTACT_PROMPT_OPTION_LABELS,
    CONTACT_PROMPT_SKIP_INPUTS,
    render_contact_prompt_ui,
)


def test_renderer_options_are_covered_by_parser() -> None:
    for option_value, _ in CONTACT_PROMPT_OPTION_LABELS:
        parsed = parse_contact_prompt_input(option_value)

        if option_value == "8":
            assert parsed.action == "skip"
            assert parsed.contact_type is None
        else:
            assert parsed.action == "select_contact_type"
            assert parsed.contact_type is not None


def test_renderer_skip_inputs_are_covered_by_parser() -> None:
    for skip_input in CONTACT_PROMPT_SKIP_INPUTS:
        parsed = parse_contact_prompt_input(skip_input)
        assert parsed.action == "skip"
        assert parsed.contact_type is None
        assert parsed.error_message is None


def test_renderer_invalid_message_matches_parser_invalid_message() -> None:
    parsed = parse_contact_prompt_input("invalid")
    assert parsed.action == "invalid"
    assert parsed.error_message == CONTACT_PROMPT_INVALID_MESSAGE


def test_renderer_and_parser_keep_safe_flags() -> None:
    rendered = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )
    parsed = parse_contact_prompt_input("1")

    assert rendered.preview_only is True
    assert rendered.persisted is False
    assert rendered.external_lookup_used is False

    assert parsed.preview_only is True
    assert parsed.persisted is False
    assert parsed.external_lookup_used is False


def test_delete_confirmation_is_not_prompt_action() -> None:
    parsed = parse_contact_prompt_input("JA")
    assert parsed.action == "invalid"
    assert parsed.contact_type is None
