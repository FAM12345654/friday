"""Read-only local day planning preview helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable


_DONE_STATUSES = {"done", "archived"}
_PRIORITY_RANKS = {
    "urgent": 4,
    "high": 3,
    "normal": 2,
    "medium": 2,
    "low": 1,
}


@dataclass(frozen=True)
class DayPlanItem:
    """One task recommended for a local day plan preview."""

    task_id: int | None
    title: str
    due_date: str | None
    priority: str
    status: str
    recommendation_reason: str
    sort_bucket: str


@dataclass(frozen=True)
class DayPlanPreview:
    """Read-only result for a local day plan preview."""

    today: str
    items: tuple[DayPlanItem, ...]
    source_task_count: int
    recommended_count: int
    excluded_count: int
    preview_only: bool = True
    persisted: bool = False
    external_actions_enabled: bool = False


def build_day_plan_preview(
    tasks: Iterable[dict[str, Any]],
    today: str,
    limit: int | None = None,
) -> DayPlanPreview:
    """Build a deterministic read-only day planning preview from task dictionaries."""
    task_list = list(tasks)
    parsed_today = _parse_date(today)
    recommended = [
        _build_item(task=task, today=parsed_today)
        for task in task_list
        if _is_recommendable_task(task)
    ]
    recommended.sort(key=lambda item: _sort_key(item, parsed_today))
    if limit is not None:
        recommended = recommended[: max(limit, 0)]

    return DayPlanPreview(
        today=today,
        items=tuple(recommended),
        source_task_count=len(task_list),
        recommended_count=len(recommended),
        excluded_count=len(task_list) - len([task for task in task_list if _is_recommendable_task(task)]),
    )


def _is_recommendable_task(task: dict[str, Any]) -> bool:
    """Return True when a task is open enough to appear in a day plan."""
    title = str(task.get("title") or "").strip()
    if not title:
        return False
    status = str(task.get("status") or "open").strip().lower()
    return status not in _DONE_STATUSES


def _build_item(task: dict[str, Any], today: date | None) -> DayPlanItem:
    """Convert a task dictionary into a day plan item."""
    due_date = _clean_optional_text(task.get("due_date"))
    status = str(task.get("status") or "open").strip().lower() or "open"
    priority = _normalize_priority(task.get("priority"))
    return DayPlanItem(
        task_id=_safe_int(task.get("id")),
        title=str(task.get("title") or "").strip(),
        due_date=due_date,
        priority=priority,
        status=status,
        recommendation_reason=_recommendation_reason(due_date=due_date, today=today, priority=priority),
        sort_bucket=_sort_bucket(due_date=due_date, today=today),
    )


def _sort_key(item: DayPlanItem, today: date | None) -> tuple[int, str, int, str]:
    """Sort overdue/due tasks first, then priority, due date, title."""
    due = _parse_date(item.due_date)
    due_bucket = _due_bucket(due=due, today=today)
    due_value = item.due_date or "9999-12-31"
    return (
        due_bucket,
        due_value,
        -_PRIORITY_RANKS.get(item.priority, _PRIORITY_RANKS["normal"]),
        item.title.lower(),
    )


def _recommendation_reason(due_date: str | None, today: date | None, priority: str) -> str:
    """Return a short reason for why the task appears in the preview."""
    due = _parse_date(due_date)
    if due is not None and today is not None:
        if due < today:
            return "ueberfaellig"
        if due == today:
            return "heute faellig"
    if priority in {"urgent", "high"}:
        return "hohe prioritaet"
    if due_date:
        return "geplant"
    return "ohne faelligkeitsdatum"


def _sort_bucket(due_date: str | None, today: date | None) -> str:
    """Return a readable bucket matching the due-date sort grouping."""
    due = _parse_date(due_date)
    if due is None or today is None:
        return "ohne_faelligkeitsdatum"
    if due < today:
        return "ueberfaellig"
    if due == today:
        return "heute"
    return "spaeter"


def _due_bucket(due: date | None, today: date | None) -> int:
    """Return a numeric due-date group for sorting."""
    if due is None or today is None:
        return 3
    if due <= today:
        return 0
    return 1


def _parse_date(value: str | None) -> date | None:
    """Parse an ISO date string safely."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        return None


def _normalize_priority(value: Any) -> str:
    """Normalize task priority for preview sorting."""
    priority = str(value or "normal").strip().lower() or "normal"
    if priority not in _PRIORITY_RANKS:
        return "normal"
    return priority


def _clean_optional_text(value: Any) -> str | None:
    """Return stripped text or None."""
    cleaned = str(value or "").strip()
    return cleaned or None


def _safe_int(value: Any) -> int | None:
    """Convert task ids safely for display-only preview items."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
