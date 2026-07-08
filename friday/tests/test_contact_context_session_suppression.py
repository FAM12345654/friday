"""Tests for in-memory contact prompt session suppression helpers."""

from friday.app.contact_context_session_suppression import (
    ContactPromptSuppressionEntry,
    clear_contact_prompt_suppression,
    is_contact_prompt_suppressed,
    mark_contact_prompt_skipped,
)


def test_mark_and_check_skipped_prompt() -> None:
    entries: tuple[ContactPromptSuppressionEntry, ...] = ()
    suppressed = mark_contact_prompt_skipped(
        "  MAX   Mustermann ",
        "nachrichten_review",
        entries,
    )

    assert len(suppressed) == 1
    entry = suppressed[0]
    assert entry.normalized_name == "max mustermann"
    assert entry.source_context == "nachrichten_review"
    assert entry.status == "skipped"
    assert entry.reason == "user_skipped"
    assert entry.preview_only is True
    assert entry.persisted is False
    assert entry.external_lookup_used is False

    assert is_contact_prompt_suppressed(
        "max mustermann",
        "nachrichten_review",
        suppressed,
    )


def test_skipped_prompt_is_context_specific() -> None:
    entries: tuple[ContactPromptSuppressionEntry, ...] = ()
    entries = mark_contact_prompt_skipped(
        "Max Mustermann",
        "nachrichten_review",
        entries,
    )

    assert not is_contact_prompt_suppressed(
        "Max Mustermann",
        "person_bearbeiten",
        entries,
    )


def test_mark_skipped_prompt_does_not_suppress_other_person() -> None:
    entries: tuple[ContactPromptSuppressionEntry, ...] = ()
    entries = mark_contact_prompt_skipped(
        "Max Mustermann",
        "nachrichten_review",
        entries,
    )

    assert not is_contact_prompt_suppressed(
        "Eva Musterfrau",
        "nachrichten_review",
        entries,
    )


def test_mark_skipped_prompt_replaces_existing_entry_for_same_key() -> None:
    existing = ContactPromptSuppressionEntry(
        normalized_name="max mustermann",
        source_context="nachrichten_review",
        status="suppressed",
        reason="review_cached",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
    entries = (existing,)

    replaced = mark_contact_prompt_skipped(
        "Max Mustermann",
        "nachrichten_review",
        entries,
    )

    assert len(replaced) == 1
    assert replaced[0].status == "skipped"
    assert replaced[0].reason == "user_skipped"


def test_clear_contact_prompt_suppression_removes_entry() -> None:
    entries: tuple[ContactPromptSuppressionEntry, ...] = ()
    suppressed = mark_contact_prompt_skipped(
        "Max Mustermann",
        "nachrichten_review",
        entries,
    )

    cleared = clear_contact_prompt_suppression(
        "Max Mustermann",
        "nachrichten_review",
        suppressed,
    )

    assert not is_contact_prompt_suppressed(
        "Max Mustermann",
        "nachrichten_review",
        cleared,
    )
    assert len(cleared) == 0


def test_clear_missing_entry_keeps_state() -> None:
    entries: tuple[ContactPromptSuppressionEntry, ...] = ()
    cleared = clear_contact_prompt_suppression(
        "Max Mustermann",
        "nachrichten_review",
        entries,
    )

    assert cleared == ()
