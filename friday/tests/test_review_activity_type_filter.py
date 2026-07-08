"""Tests for the read-only review activity type filter model."""

from __future__ import annotations

from friday.app.review_activity_detail_view import ReviewActivityDetailItem
from friday.app.review_activity_type_filter import (
    INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE,
    build_review_activity_type_filter,
    normalize_review_activity_type_filter,
)


def _item(
    suggestion_id: int,
    suggestion_type: str,
) -> ReviewActivityDetailItem:
    return ReviewActivityDetailItem(
        suggestion_type=suggestion_type,
        suggestion_id=suggestion_id,
        status="pending",
        primary_label=f"Eintrag {suggestion_id}",
        excerpt="Lokaler Review-Eintrag",
        updated_at=f"2026-07-06T0{suggestion_id}:00:00",
        created_task_id=None,
    )


def test_normalize_review_activity_type_filter_strips_and_lowercases() -> None:
    assert normalize_review_activity_type_filter(" Message ") == "message"


def test_review_activity_type_filter_all_returns_all_items() -> None:
    items = (_item(1, "message"), _item(2, "task"))

    result = build_review_activity_type_filter(items, "all")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1, 2]


def test_review_activity_type_filter_message_returns_message_items() -> None:
    items = (_item(1, "message"), _item(2, "task"), _item(3, "message"))

    result = build_review_activity_type_filter(items, "message")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1, 3]


def test_review_activity_type_filter_task_returns_task_items() -> None:
    items = (_item(1, "message"), _item(2, "task"))

    result = build_review_activity_type_filter(items, "task")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [2]


def test_review_activity_type_filter_invalid_filter_is_safe() -> None:
    result = build_review_activity_type_filter((_item(1, "message"),), "contact")

    assert result.is_valid is False
    assert result.items == ()
    assert result.error_message == INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE


def test_review_activity_type_filter_has_safe_read_only_flags() -> None:
    result = build_review_activity_type_filter(None, "all")

    assert result.items == ()
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
