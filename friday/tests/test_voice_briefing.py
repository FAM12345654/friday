"""Tests for the spoken morning briefing text builder."""

from __future__ import annotations

from friday.app.voice_briefing import build_briefing_text, select_overdue_tasks

TODAY = "2026-07-13"


def test_german_briefing_with_everything() -> None:
    text = build_briefing_text(
        day_iso=TODAY,
        tasks_today=[{"title": "Milch kaufen"}, {"title": "Anna anrufen"}],
        overdue_tasks=[{"title": "Steuererklärung"}],
        calendar_items=[{"title": "Zahnarzt"}],
        language="de",
    )
    assert text.startswith("Guten Morgen! Heute ist Montag")
    assert "2 Aufgaben: Milch kaufen und Anna anrufen." in text
    assert "Eine Aufgabe ist überfällig: Steuererklärung." in text
    assert "1 Termin: Zahnarzt." in text
    assert text.endswith("Einen guten Start in den Tag!")


def test_german_briefing_speaks_weather_after_greeting() -> None:
    text = build_briefing_text(
        day_iso=TODAY,
        tasks_today=[{"title": "Milch kaufen"}],
        language="de",
        weather_text="Regen, bei Temperaturen zwischen 17 und 25 Grad Celsius.",
    )
    greeting_index = text.index("Guten Morgen")
    weather_index = text.index("Das Wetter: Regen")
    task_index = text.index("Milch kaufen")
    assert greeting_index < weather_index < task_index


def test_english_briefing_speaks_weather_after_greeting() -> None:
    text = build_briefing_text(
        day_iso=TODAY,
        tasks_today=[{"title": "Buy milk"}],
        language="en",
        weather_text="rain, with temperatures between 17 and 25 degrees Celsius.",
    )
    assert "The weather: rain" in text
    assert text.index("The weather:") < text.index("Buy milk")


def test_briefing_without_weather_has_no_weather_sentence() -> None:
    text = build_briefing_text(day_iso=TODAY, tasks_today=[], language="de")
    assert "Das Wetter" not in text


def test_german_briefing_empty_day() -> None:
    text = build_briefing_text(day_iso=TODAY, tasks_today=[], language="de")
    assert "keine Aufgaben" in text
    assert "überfällig" not in text
    assert "Termin" not in text


def test_english_briefing() -> None:
    text = build_briefing_text(
        day_iso=TODAY,
        tasks_today=[{"title": "Buy milk"}],
        calendar_items=[{"title": "Dentist"}, {"title": "Standup"}],
        language="en",
    )
    assert text.startswith("Good morning! Today is Monday")
    assert "1 task today: Buy milk." in text
    assert "2 appointments: Dentist and Standup." in text


def test_spoken_list_caps_at_five_items() -> None:
    tasks = [{"title": f"Aufgabe {i}"} for i in range(1, 9)]
    text = build_briefing_text(day_iso=TODAY, tasks_today=tasks, language="de")
    assert "8 Aufgaben" in text
    assert "Aufgabe 5" in text
    assert "Aufgabe 6" not in text


def test_no_markdown_or_newlines_for_tts() -> None:
    text = build_briefing_text(
        day_iso=TODAY,
        tasks_today=[{"title": "Milch  kaufen"}],
        language="de",
    )
    assert "\n" not in text
    assert "*" not in text
    assert "  " not in text


def test_select_overdue_respects_status_and_snooze() -> None:
    tasks = [
        {"title": "Überfällig", "due_date": "2026-07-10", "status": "open"},
        {"title": "Erledigt", "due_date": "2026-07-10", "status": "done"},
        {"title": "Snoozed", "due_date": "2026-07-10", "status": "open", "snoozed_until": "2026-07-20"},
        {"title": "Heute", "due_date": TODAY, "status": "open"},
        {"title": "Ohne Datum", "due_date": None, "status": "open"},
    ]
    overdue = select_overdue_tasks(tasks, TODAY)
    assert [task["title"] for task in overdue] == ["Überfällig"]
