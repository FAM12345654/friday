"""Tests for local startup notification previews."""

from __future__ import annotations

from friday.app.notification_preview import build_due_task_notification_preview


def test_notification_preview_ignores_empty_task_list() -> None:
    preview = build_due_task_notification_preview([], today="2026-07-08")

    assert preview.should_show is False
    assert preview.due_today_count == 0
    assert preview.overdue_count == 0


def test_notification_preview_counts_due_today() -> None:
    preview = build_due_task_notification_preview(
        [{"title": "Heute", "due_date": "2026-07-08", "status": "open"}],
        today="2026-07-08",
    )

    assert preview.should_show is True
    assert preview.due_today_count == 1
    assert preview.overdue_count == 0
    assert "1 Aufgaben heute fällig" in preview.text


def test_notification_preview_counts_overdue() -> None:
    preview = build_due_task_notification_preview(
        [{"title": "Alt", "due_date": "2026-07-07", "status": "open"}],
        today="2026-07-08",
    )

    assert preview.should_show is True
    assert preview.due_today_count == 0
    assert preview.overdue_count == 1
    assert "1 Aufgaben überfällig" in preview.text


def test_notification_preview_counts_mixed_tasks() -> None:
    preview = build_due_task_notification_preview(
        [
            {"title": "Alt", "due_date": "2026-07-07", "status": "open"},
            {"title": "Heute", "due_date": "2026-07-08", "status": "open"},
            {"title": "Fertig", "due_date": "2026-07-08", "status": "done"},
        ],
        today="2026-07-08",
    )

    assert preview.should_show is True
    assert preview.due_today_count == 1
    assert preview.overdue_count == 1
