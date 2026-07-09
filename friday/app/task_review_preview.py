"""Read-only task review preview helpers.

This module builds a local, side-effect-free overview from existing task
dictionaries. It does not read from or write to storage and does not print or
ask for input.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any


OPEN_STATUSES = {"open", "todo", "pending"}
HIGH_PRIORITIES = {"high", "urgent"}


@dataclass(frozen=True)
class TaskReviewItem:
    """Small immutable task snapshot for review previews."""

    task_id: int | None
    title: str
    status: str
    due_date: str | None
    priority: str
    category: str


@dataclass(frozen=True)
class TaskReviewSummary:
    """Aggregated counts for a local task review preview."""

    total_count: int
    open_count: int
    done_count: int
    archived_count: int
    due_today_count: int
    overdue_count: int
    without_due_date_count: int
    high_priority_open_count: int
    urgent_open_count: int
    read_only: bool = True
    external_actions_enabled: bool = False


@dataclass(frozen=True)
class TaskReviewPreview:
    """Read-only preview result for local task review."""

    today: str
    summary: TaskReviewSummary
    due_today: tuple[TaskReviewItem, ...]
    overdue: tuple[TaskReviewItem, ...]
    high_priority_open: tuple[TaskReviewItem, ...]
    without_due_date: tuple[TaskReviewItem, ...]
    notes: tuple[str, ...]
    read_only: bool = True
    writes_enabled: bool = False
    external_actions_enabled: bool = False


def build_task_review_preview(tasks: list[dict[str, Any]], today: str) -> TaskReviewPreview:
    """Build a read-only task review preview from task dictionaries."""

    today_date = _parse_date(today)
    items = tuple(_to_review_item(task) for task in tasks)

    open_items = tuple(item for item in items if _is_open(item.status))
    done_count = sum(1 for item in items if item.status == "done")
    archived_count = sum(1 for item in items if item.status == "archived")

    due_today = tuple(
        item
        for item in open_items
        if today_date is not None and _parse_date(item.due_date) == today_date
    )
    overdue = tuple(
        item
        for item in open_items
        if today_date is not None
        and _parse_date(item.due_date) is not None
        and _parse_date(item.due_date) < today_date
    )
    without_due_date = tuple(
        item for item in open_items if _parse_date(item.due_date) is None
    )
    high_priority_open = tuple(
        item for item in open_items if item.priority in HIGH_PRIORITIES
    )
    urgent_open_count = sum(1 for item in open_items if item.priority == "urgent")

    notes = _build_notes(
        total_count=len(items),
        open_count=len(open_items),
        due_today_count=len(due_today),
        overdue_count=len(overdue),
    )

    summary = TaskReviewSummary(
        total_count=len(items),
        open_count=len(open_items),
        done_count=done_count,
        archived_count=archived_count,
        due_today_count=len(due_today),
        overdue_count=len(overdue),
        without_due_date_count=len(without_due_date),
        high_priority_open_count=len(high_priority_open),
        urgent_open_count=urgent_open_count,
    )

    return TaskReviewPreview(
        today=today,
        summary=summary,
        due_today=due_today,
        overdue=overdue,
        high_priority_open=high_priority_open,
        without_due_date=without_due_date,
        notes=notes,
    )


def _to_review_item(task: dict[str, Any]) -> TaskReviewItem:
    return TaskReviewItem(
        task_id=_to_optional_int(task.get("id")),
        title=str(task.get("title") or ""),
        status=str(task.get("status") or "open").strip().lower(),
        due_date=_to_optional_string(task.get("due_date")),
        priority=str(task.get("priority") or "normal").strip().lower(),
        category=str(task.get("category") or "").strip(),
    )


def _to_optional_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _to_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _is_open(status: str) -> bool:
    return status in OPEN_STATUSES


def _build_notes(
    total_count: int,
    open_count: int,
    due_today_count: int,
    overdue_count: int,
) -> tuple[str, ...]:
    notes = [
        "Read-only preview: Es werden keine Aufgaben geaendert.",
        "Alle Werte stammen aus lokal uebergebenen Task-Daten.",
    ]
    if total_count == 0:
        notes.append("Es sind keine Aufgaben fuer die Vorschau vorhanden.")
    elif open_count == 0:
        notes.append("Es sind keine offenen Aufgaben vorhanden.")
    if due_today_count:
        notes.append("Es gibt Aufgaben, die heute faellig sind.")
    if overdue_count:
        notes.append("Es gibt ueberfaellige offene Aufgaben.")
    return tuple(notes)
