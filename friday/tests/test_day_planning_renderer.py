"""Tests for the local day planning preview renderer."""

from __future__ import annotations

from dataclasses import replace

from friday.app.day_planning_preview import build_day_plan_preview
from friday.app.day_planning_renderer import render_day_plan_preview
from friday.config import (
    ENABLE_REAL_CALENDAR,
    ENABLE_REAL_EMAIL,
    ENABLE_REAL_MUSIC,
    ENABLE_REAL_SMS,
    ENABLE_REAL_WEATHER,
    ENABLE_REAL_WHATSAPP,
    REQUIRE_USER_APPROVAL,
    USE_SQLITE_STORAGE,
)


def _task(
    task_id: int,
    title: str,
    due_date: str | None = None,
    priority: str | None = "normal",
    status: str = "open",
) -> dict:
    return {
        "id": task_id,
        "title": title,
        "due_date": due_date,
        "priority": priority,
        "status": status,
    }


def test_render_day_plan_preview_empty_state() -> None:
    preview = build_day_plan_preview([], today="2026-07-08")

    output = render_day_plan_preview(preview)

    assert "Lokale Tagesplanung fuer 2026-07-08" in output
    assert "Keine offenen Aufgaben fuer die Tagesplanung gefunden." in output
    assert "nur eine lokale Vorschau" in output
    assert "Es wurde nichts geaendert." in output


def test_render_day_plan_preview_with_tasks() -> None:
    preview = build_day_plan_preview(
        [
            _task(1, "Rechnung pruefen", due_date="2026-07-08", priority="high"),
            _task(2, "Einkauf planen", due_date="2026-07-09", priority="low"),
        ],
        today="2026-07-08",
    )

    output = render_day_plan_preview(preview)

    assert "Empfohlene Aufgaben:" in output
    assert "1. Rechnung pruefen" in output
    assert "Faellig: 2026-07-08" in output
    assert "Prioritaet: high" in output
    assert "Grund: heute faellig" in output
    assert "2. Einkauf planen" in output
    assert "Empfohlen: 2 von 2 lokalen Aufgaben." in output


def test_render_day_plan_preview_formats_missing_due_date() -> None:
    preview = build_day_plan_preview(
        [_task(1, "Ohne Datum", due_date=None, priority="urgent")],
        today="2026-07-08",
    )

    output = render_day_plan_preview(preview)

    assert "Faellig: kein Faelligkeitsdatum" in output
    assert "Prioritaet: urgent" in output


def test_render_day_plan_preview_does_not_mutate_preview() -> None:
    preview = build_day_plan_preview(
        [_task(1, "Stabil", due_date="2026-07-08", priority="normal")],
        today="2026-07-08",
    )
    before = replace(preview)

    render_day_plan_preview(preview)

    assert preview == before


def test_day_planning_renderer_keeps_safety_flags_local_only() -> None:
    assert USE_SQLITE_STORAGE is True
    assert ENABLE_REAL_EMAIL is False
    assert ENABLE_REAL_WHATSAPP is False
    assert ENABLE_REAL_SMS is False
    assert ENABLE_REAL_CALENDAR is True
    assert ENABLE_REAL_WEATHER is False
    assert ENABLE_REAL_MUSIC is False
    assert REQUIRE_USER_APPROVAL is True
