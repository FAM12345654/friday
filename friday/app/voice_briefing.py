"""Compose the spoken morning briefing text.

Pure text building over the MorningBriefingAgent preview plus overdue tasks
— no I/O here. German is the primary voice; English is available for the
bilingual voice module. The output is written for TTS: short sentences, no
markdown, numbers spelled in digits (both Orpheus and Kokoro read them fine).
"""

from __future__ import annotations

from datetime import date
from typing import Any, Iterable, Mapping

MAX_SPOKEN_ITEMS = 5

_WEEKDAYS_DE = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
_WEEKDAYS_EN = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
# Month names stay explicit: strftime('%B') depends on the process locale.
_MONTHS_DE = (
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
)
_MONTHS_EN = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def _spoken_date(day_iso: str, language: str) -> str:
    try:
        day = date.fromisoformat(day_iso)
    except ValueError:
        return day_iso
    if language == "en":
        return f"{_WEEKDAYS_EN[day.weekday()]}, {_MONTHS_EN[day.month - 1]} {day.day}"
    return f"{_WEEKDAYS_DE[day.weekday()]}, der {day.day}. {_MONTHS_DE[day.month - 1]}"


def _titles(items: Iterable[Mapping[str, Any]], key: str = "title") -> list[str]:
    titles = []
    for item in items:
        title = " ".join(str(item.get(key) or "").split())
        if title:
            titles.append(title)
    return titles


def _join(titles: list[str], language: str) -> str:
    shown = titles[:MAX_SPOKEN_ITEMS]
    if len(shown) == 1:
        return shown[0]
    connector = " und " if language == "de" else " and "
    return ", ".join(shown[:-1]) + connector + shown[-1]


def build_briefing_text(
    *,
    day_iso: str,
    tasks_today: Iterable[Mapping[str, Any]],
    overdue_tasks: Iterable[Mapping[str, Any]] = (),
    calendar_items: Iterable[Mapping[str, Any]] = (),
    language: str = "de",
) -> str:
    """Build the spoken briefing for one day."""
    lang = "en" if str(language).lower().startswith("en") else "de"
    task_titles = _titles(tasks_today)
    overdue_titles = _titles(overdue_tasks)
    event_titles = _titles(calendar_items)

    parts: list[str] = []
    spoken_day = _spoken_date(day_iso, lang)

    if lang == "en":
        parts.append(f"Good morning! Today is {spoken_day}.")
        if task_titles:
            noun = "task" if len(task_titles) == 1 else "tasks"
            parts.append(f"You have {len(task_titles)} {noun} today: {_join(task_titles, lang)}.")
        else:
            parts.append("You have no tasks scheduled for today.")
        if overdue_titles:
            noun = "task is" if len(overdue_titles) == 1 else "tasks are"
            parts.append(f"{len(overdue_titles)} {noun} overdue: {_join(overdue_titles, lang)}.")
        if event_titles:
            noun = "appointment" if len(event_titles) == 1 else "appointments"
            parts.append(f"Your calendar has {len(event_titles)} {noun}: {_join(event_titles, lang)}.")
        parts.append("Have a great day!")
    else:
        parts.append(f"Guten Morgen! Heute ist {spoken_day}.")
        if task_titles:
            noun = "Aufgabe" if len(task_titles) == 1 else "Aufgaben"
            parts.append(f"Du hast heute {len(task_titles)} {noun}: {_join(task_titles, lang)}.")
        else:
            parts.append("Für heute stehen keine Aufgaben an.")
        if overdue_titles:
            if len(overdue_titles) == 1:
                parts.append(f"Eine Aufgabe ist überfällig: {_join(overdue_titles, lang)}.")
            else:
                parts.append(
                    f"{len(overdue_titles)} Aufgaben sind überfällig: {_join(overdue_titles, lang)}."
                )
        if event_titles:
            noun = "Termin" if len(event_titles) == 1 else "Termine"
            parts.append(f"Im Kalender {'steht' if len(event_titles) == 1 else 'stehen'} {len(event_titles)} {noun}: {_join(event_titles, lang)}.")
        parts.append("Einen guten Start in den Tag!")

    return " ".join(parts)


def select_overdue_tasks(
    tasks: Iterable[Mapping[str, Any]],
    today_iso: str,
) -> list[Mapping[str, Any]]:
    """Open, unsnoozed tasks whose due date lies before today."""
    overdue: list[Mapping[str, Any]] = []
    for task in tasks:
        status = str(task.get("status") or "").lower()
        if status in {"done", "archived"}:
            continue
        snoozed_until = str(task.get("snoozed_until") or "").strip()
        if snoozed_until and snoozed_until > today_iso:
            continue
        due = str(task.get("due_date") or "").strip()
        if due and due < today_iso:
            overdue.append(task)
    return overdue
