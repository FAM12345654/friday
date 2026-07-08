from friday.app.contact_context_prompt_candidate import (
    ContactPromptCandidate,
    should_create_contact_prompt_candidate,
)


def test_prompt_candidate_allows_unknown_contact_in_review() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
    )

    assert isinstance(candidate, ContactPromptCandidate)
    assert candidate.status == "allowed"
    assert candidate.reason == "unknown_contact_in_review"
    assert candidate.question == "Wer ist Max Mustermann für dich?"
    assert candidate.preview_only is True
    assert candidate.persisted is False
    assert candidate.external_lookup_used is False


def test_prompt_candidate_blocks_known_contact() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="Max Mustermann",
        contact_type="kunde",
        source_context="nachrichten_review",
    )

    assert candidate.status == "not_allowed"
    assert candidate.reason == "known_contact"
    assert candidate.question is None


def test_prompt_candidate_blocks_app_start_without_context() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="app_start",
    )

    assert candidate.status == "not_allowed"
    assert candidate.reason == "no_active_context"


def test_prompt_candidate_respects_recently_skipped() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
        recently_skipped=True,
    )

    assert candidate.status == "skipped"
    assert candidate.reason == "recently_skipped"
    assert candidate.question is None


def test_prompt_candidate_blocks_sensitive_or_disallowed() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="nachrichten_review",
        sensitive_or_disallowed=True,
    )

    assert candidate.status == "not_allowed"
    assert candidate.reason == "sensitive_or_disallowed"
    assert candidate.question is None


def test_prompt_candidate_allows_explicit_person_edit() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="person_bearbeiten",
    )

    assert candidate.status == "allowed"
    assert candidate.reason == "explicit_person_edit"


def test_prompt_candidate_normalizes_name_and_source() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="  MAX   Mustermann ",
        contact_type="unbekannt",
        source_context="  NUTZERANFRAGE  ",
    )

    assert candidate.normalized_name == "max mustermann"
    assert candidate.source_context == "nutzeranfrage"


def test_prompt_candidate_has_no_persistence_or_external_lookup() -> None:
    candidate = should_create_contact_prompt_candidate(
        display_name="Max Mustermann",
        contact_type="unbekannt",
        source_context="aufgabe_aus_nachricht",
    )

    assert candidate.preview_only is True
    assert candidate.persisted is False
    assert candidate.external_lookup_used is False
