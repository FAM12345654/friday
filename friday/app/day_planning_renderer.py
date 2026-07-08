"""Renderer for local day planning preview text."""

from __future__ import annotations

from friday.app.day_planning_preview import DayPlanPreview


def render_day_plan_preview(preview: DayPlanPreview) -> str:
    """Render a local day planning preview as German text."""
    lines = [
        f"Lokale Tagesplanung fuer {preview.today}",
        "",
    ]

    if not preview.items:
        lines.extend(
            [
                "Keine offenen Aufgaben fuer die Tagesplanung gefunden.",
                "",
                _safety_hint(),
            ]
        )
        return "\n".join(lines)

    lines.append("Empfohlene Aufgaben:")
    for index, item in enumerate(preview.items, start=1):
        lines.extend(
            [
                f"{index}. {item.title}",
                f"   Faellig: {_format_due_date(item.due_date)}",
                f"   Prioritaet: {item.priority}",
                f"   Grund: {item.recommendation_reason}",
            ]
        )
    lines.extend(
        [
            "",
            f"Empfohlen: {preview.recommended_count} von {preview.source_task_count} lokalen Aufgaben.",
            _safety_hint(),
        ]
    )
    return "\n".join(lines)


def _format_due_date(due_date: str | None) -> str:
    """Return a user-facing due-date value."""
    return due_date or "kein Faelligkeitsdatum"


def _safety_hint() -> str:
    """Return the standard local-only hint."""
    return "Hinweis: Diese Ansicht ist nur eine lokale Vorschau. Es wurde nichts geaendert."
