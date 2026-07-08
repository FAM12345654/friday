from friday.app.contact_context_prompt_preview import build_contact_prompt_preview


def test_contact_prompt_preview_allows_unknown_contact_in_review() -> None:
    preview = build_contact_prompt_preview(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert preview.should_ask is True
    assert preview.candidate.status == "allowed"
    assert preview.candidate.reason == "unknown_contact_in_review"
    assert preview.context_preview.contact_type == "unbekannt"
    assert "kunde" in preview.prompt_options
    assert "überspringen" in preview.prompt_options


def test_contact_prompt_preview_blocks_known_contact() -> None:
    preview = build_contact_prompt_preview(
        display_name="Max Mustermann",
        contact_type="kunde",
        source_context="nachrichten_review",
    )

    assert preview.should_ask is False
    assert preview.candidate.reason == "known_contact"
    assert preview.context_preview.contact_type == "kunde"


def test_contact_prompt_preview_respects_recently_skipped() -> None:
    preview = build_contact_prompt_preview(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
        recently_skipped=True,
    )

    assert preview.should_ask is False
    assert preview.candidate.status == "skipped"
    assert preview.candidate.reason == "recently_skipped"


def test_contact_prompt_preview_blocks_sensitive_or_disallowed() -> None:
    preview = build_contact_prompt_preview(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
        sensitive_or_disallowed=True,
    )

    assert preview.should_ask is False
    assert preview.candidate.reason == "sensitive_or_disallowed"


def test_contact_prompt_preview_keeps_optional_context() -> None:
    preview = build_contact_prompt_preview(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="person_bearbeiten",
        nickname="Max",
        relationship_context="Projekt Alpha",
    )

    assert preview.context_preview.nickname == "Max"
    assert preview.context_preview.relationship_context == "Projekt Alpha"


def test_contact_prompt_preview_has_safe_flags() -> None:
    preview = build_contact_prompt_preview(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="aufgabe_aus_nachricht",
    )

    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False
    assert preview.context_preview.persisted is False
    assert preview.candidate.external_lookup_used is False


def test_contact_prompt_preview_blocks_disallowed_source() -> None:
    preview = build_contact_prompt_preview(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="app_start",
    )

    assert preview.should_ask is False
    assert preview.candidate.reason == "no_active_context"
