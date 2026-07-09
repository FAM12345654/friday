"""Tests for local routine detection candidates."""

from __future__ import annotations

from friday.app.routine_detector import detect_routine_candidates


def test_detects_frequent_unknown_sender_without_writing() -> None:
    candidates = detect_routine_candidates(
        messages=[
            {"sender": "kunde@example.test", "text": "Bitte PH Angebot pruefen."},
            {"sender": "kunde@example.test", "text": "Bitte Rueckmeldung."},
        ],
        contacts=[],
        calendar_items=[],
    )

    assert any(candidate.kind == "frequent_unknown_sender" for candidate in candidates)
    question = candidates[0]
    assert "wer ist das" in question.question_text.casefold()
    assert any(option["id"] == "kunde_philip" for option in question.options)


def test_known_sender_does_not_create_unknown_sender_candidate() -> None:
    candidates = detect_routine_candidates(
        messages=[
            {"sender": "Max <max@example.test>", "text": "Bitte PH Angebot pruefen."},
            {"sender": "Max <max@example.test>", "text": "Bitte Rueckmeldung."},
        ],
        contacts=[{"name": "Max", "email_address": "max@example.test", "contact_type": "kunde"}],
        calendar_items=[],
    )

    assert not any(candidate.kind == "frequent_unknown_sender" for candidate in candidates)


def test_detects_customer_without_betreuer() -> None:
    candidates = detect_routine_candidates(
        messages=[],
        contacts=[{"id": 7, "name": "Kunde Alpha", "contact_type": "kunde", "betreuer": ""}],
        calendar_items=[],
    )

    assert candidates[0].kind == "customer_missing_betreuer"
    assert candidates[0].subject_ref == "contact:7"


def test_detects_recurring_mail_topic() -> None:
    candidates = detect_routine_candidates(
        messages=[
            {"sender": "team@example.test", "subject": "Report Montag"},
            {"sender": "team@example.test", "subject": "Report Montag"},
        ],
        contacts=[{"name": "Team", "email_address": "team@example.test", "contact_type": "arbeit"}],
        calendar_items=[],
    )

    assert any(candidate.kind == "recurring_mail_topic" for candidate in candidates)


def test_detects_uncategorized_recurring_calendar_item() -> None:
    candidates = detect_routine_candidates(
        messages=[],
        contacts=[],
        calendar_items=[
            {"title": "PH Dienst", "start": "09:00", "date": "2026-07-06"},
            {"title": "PH Dienst", "start": "09:00", "date": "2026-07-13"},
        ],
    )

    assert any(candidate.kind == "calendar_uncategorized" for candidate in candidates)
