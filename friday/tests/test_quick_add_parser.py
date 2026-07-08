"""Tests for the local task quick-add parser."""

from __future__ import annotations

from friday.app.quick_add_parser import parse_quick_add_task


def test_parse_quick_add_plain_title() -> None:
    result = parse_quick_add_task("Bericht schreiben", today="2026-07-05")

    assert result.valid is True
    assert result.title == "Bericht schreiben"
    assert result.priority == "normal"
    assert result.due_date is None


def test_parse_quick_add_priority_and_iso_date() -> None:
    result = parse_quick_add_task("Zahnarzt anrufen !hoch @2026-07-15", today="2026-07-05")

    assert result.valid is True
    assert result.title == "Zahnarzt anrufen"
    assert result.priority == "high"
    assert result.due_date == "2026-07-15"


def test_parse_quick_add_tomorrow_relative_to_injected_today() -> None:
    result = parse_quick_add_task("Bericht fertig @morgen !mittel", today="2026-07-05")

    assert result.valid is True
    assert result.title == "Bericht fertig"
    assert result.priority == "normal"
    assert result.due_date == "2026-07-06"


def test_parse_quick_add_today_relative_to_injected_today() -> None:
    result = parse_quick_add_task("Heute erledigen @heute !niedrig", today="2026-07-05")

    assert result.valid is True
    assert result.title == "Heute erledigen"
    assert result.priority == "low"
    assert result.due_date == "2026-07-05"


def test_parse_quick_add_rejects_empty_input() -> None:
    result = parse_quick_add_task("   ", today="2026-07-05")

    assert result.valid is False
    assert result.error == "Eine Aufgabe braucht mindestens einen Titel."


def test_parse_quick_add_rejects_unknown_priority_marker() -> None:
    result = parse_quick_add_task("Aufgabe !super", today="2026-07-05")

    assert result.valid is False
    assert result.error == "Unbekannte Priorität: !super"


def test_parse_quick_add_rejects_duplicate_date_marker() -> None:
    result = parse_quick_add_task("Aufgabe @heute @morgen", today="2026-07-05")

    assert result.valid is False
    assert result.error == "Fälligkeitsdatum wurde mehrfach angegeben."


def test_parse_quick_add_rejects_invalid_date_marker() -> None:
    result = parse_quick_add_task("Aufgabe @bald", today="2026-07-05")

    assert result.valid is False
    assert result.error == "Ungültiges Fälligkeitsdatum: @bald"


def test_parse_quick_add_keeps_special_characters_in_title() -> None:
    result = parse_quick_add_task("Müller & Söhne zurückrufen !hoch", today="2026-07-05")

    assert result.valid is True
    assert result.title == "Müller & Söhne zurückrufen"


def test_parse_quick_add_optional_recurrence_marker() -> None:
    result = parse_quick_add_task("Wasser trinken #taeglich", today="2026-07-05")

    assert result.valid is True
    assert result.recurrence == "taeglich"
