"""Tests for the read-only review activity summary model."""

from __future__ import annotations

from friday.app.review_activity_summary import build_review_activity_summary


def test_review_activity_summary_counts_message_statuses() -> None:
    summary = build_review_activity_summary(
        message_suggestions=[
            {"id": 1, "status": "pending"},
            {"id": 2, "status": "edited"},
            {"id": 3, "status": "approved"},
            {"id": 4, "status": "rejected"},
        ],
        task_suggestions=[],
    )

    assert summary.message_counts.total == 4
    assert summary.message_counts.open == 2
    assert summary.message_counts.approved == 1
    assert summary.message_counts.rejected == 1
    assert summary.message_counts.converted == 0
    assert summary.message_counts.with_created_task_id == 0


def test_review_activity_summary_counts_task_statuses_and_created_tasks() -> None:
    summary = build_review_activity_summary(
        message_suggestions=[],
        task_suggestions=[
            {"id": 10, "status": "pending", "created_task_id": None},
            {"id": 11, "status": "edited", "created_task_id": None},
            {"id": 12, "status": "rejected", "created_task_id": None},
            {"id": 13, "status": "converted", "created_task_id": 42},
            {"id": 14, "status": "converted", "created_task_id": "43"},
        ],
    )

    assert summary.task_counts.total == 5
    assert summary.task_counts.open == 2
    assert summary.task_counts.approved == 0
    assert summary.task_counts.rejected == 1
    assert summary.task_counts.converted == 2
    assert summary.task_counts.with_created_task_id == 2


def test_review_activity_summary_recent_items_are_sorted_by_updated_at() -> None:
    summary = build_review_activity_summary(
        message_suggestions=[
            {"id": 1, "status": "approved", "updated_at": "2026-07-06T08:00:00"},
            {"id": 2, "status": "rejected", "updated_at": "2026-07-06T10:00:00"},
        ],
        task_suggestions=[
            {
                "id": 3,
                "status": "converted",
                "created_task_id": 99,
                "updated_at": "2026-07-06T09:00:00",
            },
        ],
    )

    assert [item.suggestion_id for item in summary.recent_items] == [2, 3, 1]
    assert summary.recent_items[1].suggestion_type == "task"
    assert summary.recent_items[1].created_task_id == 99


def test_review_activity_summary_respects_recent_limit() -> None:
    summary = build_review_activity_summary(
        message_suggestions=[
            {"id": 1, "status": "approved", "updated_at": "2026-07-06T08:00:00"},
            {"id": 2, "status": "approved", "updated_at": "2026-07-06T09:00:00"},
        ],
        task_suggestions=[
            {"id": 3, "status": "converted", "updated_at": "2026-07-06T10:00:00"},
        ],
        recent_limit=2,
    )

    assert [item.suggestion_id for item in summary.recent_items] == [3, 2]


def test_review_activity_summary_has_safe_read_only_flags() -> None:
    summary = build_review_activity_summary(
        message_suggestions=None,
        task_suggestions=None,
    )

    assert summary.message_counts.total == 0
    assert summary.task_counts.total == 0
    assert summary.preview_only is True
    assert summary.persisted is False
    assert summary.external_action_used is False
