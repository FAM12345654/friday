from friday.app.contact_context_prompt_ui_renderer import (
    CONTACT_PROMPT_INVALID_MESSAGE,
    CONTACT_PROMPT_OPTION_LABELS,
    CONTACT_PROMPT_SKIP_INPUTS,
    build_contact_prompt_text,
    render_contact_prompt_ui,
)


def test_render_contact_prompt_ui_for_allowed_unknown_contact() -> None:
    render = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert render.should_render is True
    assert render.question is not None
    assert "Kontakt-Kontext für Max Mustermann" in render.question
    assert "Wer ist Max Mustermann für dich?" in render.question
    assert "1. Kunde" in render.question
    assert "8. Überspringen" in render.question
    assert render.prompt_preview.should_ask is True


def test_render_contact_prompt_ui_blocks_known_contact() -> None:
    render = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="kunde",
        source_context="nachrichten_review",
    )

    assert render.should_render is False
    assert render.question is None
    assert render.prompt_preview.candidate.reason == "known_contact"


def test_render_contact_prompt_ui_blocks_app_start() -> None:
    render = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="app_start",
    )

    assert render.should_render is False
    assert render.question is None
    assert render.prompt_preview.candidate.reason == "no_active_context"


def test_render_contact_prompt_ui_exposes_option_labels() -> None:
    render = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert ("1", "Kunde") in render.option_labels
    assert ("8", "Überspringen") in render.option_labels
    assert ("7", "Sonstiges") in render.option_labels
    assert render.option_labels == CONTACT_PROMPT_OPTION_LABELS


def test_render_contact_prompt_ui_exposes_skip_inputs() -> None:
    render = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert "" in render.skip_inputs
    assert "8" in render.skip_inputs
    assert "z" in render.skip_inputs
    assert "skip" in render.skip_inputs
    assert "überspringen" in render.skip_inputs


def test_render_contact_prompt_ui_exposes_standard_invalid_message() -> None:
    render = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert render.invalid_message == CONTACT_PROMPT_INVALID_MESSAGE
    assert render.invalid_message == "Ungültige Auswahl. Bitte erneut versuchen."


def test_render_contact_prompt_ui_has_safe_flags() -> None:
    render = render_contact_prompt_ui(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert render.preview_only is True
    assert render.persisted is False
    assert render.external_lookup_used is False
    assert render.prompt_preview.preview_only is True
    assert render.prompt_preview.persisted is False
    assert render.prompt_preview.external_lookup_used is False


def test_build_contact_prompt_text_uses_fallback_name() -> None:
    text = build_contact_prompt_text("")

    assert "Kontakt-Kontext für diese Person" in text
    assert "Wer ist diese Person für dich?" in text
