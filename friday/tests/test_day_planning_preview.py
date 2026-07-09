"""Tests for the local day planning preview model."""

from __future__ import annotations

from friday.app.day_planning_preview import build_day_plan_preview
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


def test_day_plan_preview_handles_empty_tasks() -> None:
    preview = build_day_plan_preview([], today="2026-07-08")

    assert preview.today == "2026-07-08"
    assert preview.items == ()
    assert preview.source_task_count == 0
    assert preview.recommended_count == 0
    assert preview.excluded_count == 0
    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_actions_enabled is False


def test_day_plan_preview_excludes_done_and_archived_tasks() -> None:
    preview = build_day_plan_preview(
        [
            _task(1, "Offen", status="open"),
            _task(2, "Erledigt", status="done"),
            _task(3, "Archiviert", status="archived"),
        ],
        today="2026-07-08",
    )

    assert [item.title for item in preview.items] == ["Offen"]
    assert preview.source_task_count == 3
    assert preview.recommended_count == 1
    assert preview.excluded_count == 2


def test_day_plan_preview_sorts_overdue_and_today_before_future_and_missing_due_date() -> None:
    preview = build_day_plan_preview(
        [
            _task(1, "Ohne Datum", due_date=None, priority="urgent"),
            _task(2, "Morgen", due_date="2026-07-09", priority="urgent"),
            _task(3, "Heute", due_date="2026-07-08", priority="low"),
            _task(4, "Gestern", due_date="2026-07-07", priority="low"),
        ],
        today="2026-07-08",
    )

    assert [item.title for item in preview.items] == [
        "Gestern",
        "Heute",
        "Morgen",
        "Ohne Datum",
    ]
    assert preview.items[0].sort_bucket == "ueberfaellig"
    assert preview.items[1].sort_bucket == "heute"


def test_day_plan_preview_sorts_priority_within_same_due_date() -> None:
    preview = build_day_plan_preview(
        [
            _task(1, "Normal", due_date="2026-07-08", priority="normal"),
            _task(2, "Urgent", due_date="2026-07-08", priority="urgent"),
            _task(3, "Low", due_date="2026-07-08", priority="low"),
            _task(4, "High", due_date="2026-07-08", priority="high"),
        ],
        today="2026-07-08",
    )

    assert [item.title for item in preview.items] == ["Urgent", "High", "Normal", "Low"]


def test_day_plan_preview_uses_title_as_stable_tie_breaker() -> None:
    preview = build_day_plan_preview(
        [
            _task(1, "Zeta", due_date="2026-07-08", priority="normal"),
            _task(2, "Alpha", due_date="2026-07-08", priority="normal"),
        ],
        today="2026-07-08",
    )

    assert [item.title for item in preview.items] == ["Alpha", "Zeta"]


def test_day_plan_preview_normalizes_unknown_priority_without_crashing() -> None:
    preview = build_day_plan_preview(
        [_task(1, "Unklare Prioritaet", due_date="2026-07-08", priority="sehr wichtig")],
        today="2026-07-08",
    )

    assert preview.items[0].priority == "normal"
    assert preview.items[0].recommendation_reason == "heute faellig"


def test_day_plan_preview_limit_keeps_read_only_metadata_stable() -> None:
    preview = build_day_plan_preview(
        [
            _task(1, "Eins", due_date="2026-07-08", priority="normal"),
            _task(2, "Zwei", due_date="2026-07-08", priority="low"),
        ],
        today="2026-07-08",
        limit=1,
    )

    assert [item.title for item in preview.items] == ["Eins"]
    assert preview.source_task_count == 2
    assert preview.recommended_count == 1
    assert preview.excluded_count == 0
    assert preview.persisted is False


def test_day_plan_preview_keeps_safety_flags_local_only() -> None:
    assert USE_SQLITE_STORAGE is True
    assert ENABLE_REAL_EMAIL is False
    assert ENABLE_REAL_WHATSAPP is False
    assert ENABLE_REAL_SMS is False
    assert ENABLE_REAL_CALENDAR is True
    assert ENABLE_REAL_WEATHER is False
    assert ENABLE_REAL_MUSIC is False
    assert REQUIRE_USER_APPROVAL is True
