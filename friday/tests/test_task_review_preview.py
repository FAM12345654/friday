"""Tests for the local read-only task review preview model."""

from __future__ import annotations

from copy import deepcopy

from friday.app.task_review_preview import build_task_review_preview


def test_task_review_preview_counts_core_statuses() -> None:
    preview = build_task_review_preview(
        [
            {"id": 1, "title": "Offen", "status": "open", "due_date": "2026-07-08"},
            {"id": 2, "title": "Erledigt", "status": "done", "due_date": "2026-07-08"},
            {"id": 3, "title": "Archiviert", "status": "archived"},
        ],
        today="2026-07-08",
    )

    assert preview.summary.total_count == 3
    assert preview.summary.open_count == 1
    assert preview.summary.done_count == 1
    assert preview.summary.archived_count == 1
    assert preview.summary.due_today_count == 1


def test_task_review_preview_detects_due_today_and_overdue_open_tasks() -> None:
    preview = build_task_review_preview(
        [
            {"id": 1, "title": "Heute", "status": "open", "due_date": "2026-07-08"},
            {"id": 2, "title": "Alt", "status": "open", "due_date": "2026-07-07"},
            {"id": 3, "title": "Spaeter", "status": "open", "due_date": "2026-07-09"},
        ],
        today="2026-07-08",
    )

    assert [item.title for item in preview.due_today] == ["Heute"]
    assert [item.title for item in preview.overdue] == ["Alt"]
    assert preview.summary.due_today_count == 1
    assert preview.summary.overdue_count == 1


def test_task_review_preview_handles_missing_and_invalid_due_dates() -> None:
    preview = build_task_review_preview(
        [
            {"id": 1, "title": "Ohne Datum", "status": "open"},
            {"id": 2, "title": "Kaputtes Datum", "status": "open", "due_date": "morgen"},
            {"id": 3, "title": "Erledigt ohne Datum", "status": "done"},
        ],
        today="2026-07-08",
    )

    assert [item.title for item in preview.without_due_date] == [
        "Ohne Datum",
        "Kaputtes Datum",
    ]
    assert preview.summary.without_due_date_count == 2


def test_task_review_preview_counts_high_and_urgent_open_tasks() -> None:
    preview = build_task_review_preview(
        [
            {"id": 1, "title": "High", "status": "open", "priority": "high"},
            {"id": 2, "title": "Urgent", "status": "open", "priority": "urgent"},
            {"id": 3, "title": "Done High", "status": "done", "priority": "high"},
        ],
        today="2026-07-08",
    )

    assert [item.title for item in preview.high_priority_open] == ["High", "Urgent"]
    assert preview.summary.high_priority_open_count == 2
    assert preview.summary.urgent_open_count == 1


def test_task_review_preview_is_read_only_and_has_no_external_actions() -> None:
    preview = build_task_review_preview([], today="2026-07-08")

    assert preview.read_only is True
    assert preview.writes_enabled is False
    assert preview.external_actions_enabled is False
    assert preview.summary.read_only is True
    assert preview.summary.external_actions_enabled is False


def test_task_review_preview_does_not_mutate_input_tasks() -> None:
    tasks = [
        {"id": "1", "title": "Original", "status": "OPEN", "priority": "HIGH"},
        {"id": "x", "title": "Invalid ID", "status": ""},
    ]
    before = deepcopy(tasks)

    build_task_review_preview(tasks, today="2026-07-08")

    assert tasks == before
