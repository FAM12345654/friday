"""Tests for deterministic local task relevance rules."""

from __future__ import annotations

from friday.app.todo_relevance import determine_mail_relevance, is_relevant_for_user


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


def test_office_mail_relevance_hides_irrelevant_shared_mailbox_message() -> None:
    result = determine_mail_relevance(
        account="office@familienhelden.at",
        subject="Allgemeine Info",
        snippet="Bitte an Alex weitergeben.",
        sender="info@example.test",
        recipients=[{"name": "Alex", "address": "alex@familienhelden.at"}],
    )

    assert result == {"relevant": False, "reason": "office_not_relevant"}


def test_office_mail_relevance_matches_philip_recipient() -> None:
    result = determine_mail_relevance(
        account="office@familienhelden.at",
        subject="Neue Anfrage",
        snippet="Bitte prüfen.",
        sender="info@example.test",
        recipients=[{"name": "Philip Zeitler", "address": "philip@familienhelden.at"}],
    )

    assert result == {"relevant": True, "reason": "philip_trigger"}


def test_office_mail_relevance_matches_all_partners() -> None:
    result = determine_mail_relevance(
        account="office@familienhelden.at",
        subject="Info an Philip, Alex und Flo",
        snippet="Team-Abstimmung",
        sender="info@example.test",
    )

    assert result == {"relevant": True, "reason": "team_all_partners"}


def test_personal_mailbox_remains_fully_visible() -> None:
    result = determine_mail_relevance(
        account="philip@familienhelden.at",
        subject="Newsletter",
        snippet="Allgemeines Update",
        sender="newsletter@example.test",
    )

    assert result == {"relevant": True, "reason": "personal_mailbox"}


def test_office_mail_relevance_matches_customer_betreuer() -> None:
    result = determine_mail_relevance(
        account="office@familienhelden.at",
        subject="Bitte Angebot vorbereiten",
        snippet="Danke.",
        sender="kunde@example.test",
        sender_contact={"contact_type": "kunde", "betreuer": "philip"},
    )

    assert result == {"relevant": True, "reason": "customer_betreuer_philip"}


def test_office_mail_relevance_does_not_match_trigger_inside_other_words() -> None:
    result = determine_mail_relevance(
        account="office@familienhelden.at",
        subject="Ausflug nach Philippsburg",
        snippet="Bitte an Alex.",
        sender="info@example.test",
    )

    assert result == {"relevant": False, "reason": "office_not_relevant"}
