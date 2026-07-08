"""Build local notification previews for due tasks."""

from __future__ import annotations

from dataclasses import dataclass

from friday.app.date_utils import resolve_today


@dataclass(frozen=True)
class NotificationPreview:
    """Preview text for a local startup notification."""

    title: str
    text: str
    due_today_count: int
    overdue_count: int
    should_show: bool
    preview_only: bool = True
    persisted: bool = False
    external_lookup_used: bool = False


def build_due_task_notification_preview(
    tasks: list[dict],
    today: str | None = None,
) -> NotificationPreview:
    """Return a local notification preview for due and overdue open tasks."""
    effective_today = today or resolve_today()
    due_today_count = 0
    overdue_count = 0

    for task in tasks:
        status = str(task.get("status") or "open").lower()
        if status in {"done", "archived"}:
            continue
        due_date = task.get("due_date")
        if not due_date:
            continue
        if str(due_date) < effective_today:
            overdue_count += 1
        elif str(due_date) == effective_today:
            due_today_count += 1

    if due_today_count == 0 and overdue_count == 0:
        return NotificationPreview(
            title="Friday Aufgaben",
            text="Keine heute fälligen oder überfälligen Aufgaben.",
            due_today_count=0,
            overdue_count=0,
            should_show=False,
        )

    parts = []
    if due_today_count:
        parts.append(f"{due_today_count} Aufgaben heute fällig")
    if overdue_count:
        parts.append(f"{overdue_count} Aufgaben überfällig")

    return NotificationPreview(
        title="Friday Aufgaben",
        text=", ".join(parts) + ".",
        due_today_count=due_today_count,
        overdue_count=overdue_count,
        should_show=True,
    )
