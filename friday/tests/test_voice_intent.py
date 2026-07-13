"""Tests for the voice command intent parser."""

from __future__ import annotations

from friday.app.voice_intent import match_task_by_title, parse_voice_command

TODAY = "2026-07-13"


def test_briefing_german_variants() -> None:
    for text in ("Was steht heute an?", "Guten Morgen Friday", "Briefing bitte", "meine Aufgaben"):
        assert parse_voice_command(text, TODAY).intent == "briefing", text


def test_briefing_english() -> None:
    result = parse_voice_command("Hey Friday, what's on today?", TODAY)
    assert result.intent == "briefing"
    assert result.language == "en"


def test_calendar_intent() -> None:
    assert parse_voice_command("Welche Termine habe ich?", TODAY).intent == "calendar_today"
    assert parse_voice_command("show my appointments today", TODAY).intent == "calendar_today"


def test_create_task_german_strips_prefix() -> None:
    result = parse_voice_command("Hey Friday, erstelle Aufgabe: Milch kaufen", TODAY)
    assert result.intent == "create_task"
    assert result.argument == "Milch kaufen"
    assert result.language == "de"


def test_create_task_remind_me() -> None:
    result = parse_voice_command("Erinnere mich an den Zahnarzttermin", TODAY)
    assert result.intent == "create_task"
    assert "Zahnarzttermin" in result.argument

    english = parse_voice_command("remind me to call Anna", TODAY)
    assert english.intent == "create_task"
    assert english.argument == "call Anna"


def test_complete_task() -> None:
    result = parse_voice_command("Erledige die Aufgabe Milch kaufen", TODAY)
    assert result.intent == "complete_task"
    assert result.argument == "Milch kaufen"

    done = parse_voice_command("Milch kaufen ist erledigt", TODAY)
    assert done.intent == "complete_task"
    assert done.argument == "Milch kaufen"

    english = parse_voice_command("mark laundry as done", TODAY)
    assert english.intent == "complete_task"
    assert english.argument == "laundry"


def test_snooze_task_with_and_without_time_word() -> None:
    default = parse_voice_command("Verschiebe Steuererklärung", TODAY)
    assert default.intent == "snooze_task"
    assert default.argument == "Steuererklärung"
    assert default.snooze_until == "2026-07-14"

    next_week = parse_voice_command("Verschiebe Steuererklärung auf nächste Woche", TODAY)
    assert next_week.snooze_until == "2026-07-20"

    english = parse_voice_command("snooze taxes until next week", TODAY)
    assert english.intent == "snooze_task"
    assert english.argument == "taxes"
    assert english.snooze_until == "2026-07-20"


def test_search_intent() -> None:
    result = parse_voice_command("Suche nach Rechnung von Anna", TODAY)
    assert result.intent == "search"
    assert result.argument == "Rechnung von Anna"

    english = parse_voice_command("search for the invoice", TODAY)
    assert english.intent == "search"
    assert english.argument == "the invoice"


def test_unknown_and_empty() -> None:
    assert parse_voice_command("", TODAY).intent == "unknown"
    result = parse_voice_command("Blubb blubb blubb", TODAY)
    assert result.intent == "unknown"
    assert result.argument == "Blubb blubb blubb"


def test_to_dict_shape() -> None:
    payload = parse_voice_command("Briefing", TODAY).to_dict()
    assert payload["intent"] == "briefing"
    assert set(payload) == {"intent", "argument", "language", "snooze_until"}


# ---------------------------------------------------------------------------
# Fuzzy task matching
# ---------------------------------------------------------------------------

TASKS = [
    {"id": 1, "title": "Milch kaufen"},
    {"id": 2, "title": "Steuererklärung abgeben"},
    {"id": 3, "title": "Anna anrufen"},
]


def test_match_exact_and_substring() -> None:
    assert match_task_by_title(TASKS, "Milch kaufen")["id"] == 1
    assert match_task_by_title(TASKS, "milch")["id"] == 1
    assert match_task_by_title(TASKS, "die Steuererklärung")["id"] == 2


def test_match_fuzzy_transcription_noise() -> None:
    # Whisper might transcribe slightly differently.
    assert match_task_by_title(TASKS, "anna anrufen bitte")["id"] == 3


def test_match_returns_none_when_nothing_close() -> None:
    assert match_task_by_title(TASKS, "Rasen mähen") is None
    assert match_task_by_title(TASKS, "") is None
    assert match_task_by_title([], "Milch kaufen") is None
