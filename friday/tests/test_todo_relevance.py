"""Tests for deterministic local task relevance rules."""

from __future__ import annotations

from friday.app.todo_relevance import is_relevant_for_user


def test_relevance_matches_whole_word_triggers() -> None:
    assert is_relevant_for_user(text="Bitte PH informieren.")
    assert is_relevant_for_user(text="Das ist fuer Philip.")
    assert is_relevant_for_user(text="Phips soll das pruefen.")
    assert is_relevant_for_user(text="Bitte an Zeitler geben.")


def test_relevance_does_not_match_inside_other_words() -> None:
    assert not is_relevant_for_user(text="Graph bitte pruefen.")
    assert not is_relevant_for_user(text="Alphabetisch sortieren.")


def test_relevance_matches_customer_betreuer_philip() -> None:
    assert is_relevant_for_user(
        text="Bitte Angebot vorbereiten.",
        sender_contact={"contact_type": "kunde", "betreuer": "philip"},
    )


def test_relevance_rejects_other_betreuer_without_trigger() -> None:
    assert not is_relevant_for_user(
        text="Bitte Angebot vorbereiten.",
        sender_contact={"contact_type": "kunde", "betreuer": "alex"},
    )
