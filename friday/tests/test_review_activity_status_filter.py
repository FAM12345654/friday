"""Tests for the read-only review activity status filter model."""

from __future__ import annotations

from friday.app.review_activity_detail_view import ReviewActivityDetailItem
from friday.app.review_activity_status_filter import (
    INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE,
    build_review_activity_status_filter,
    normalize_review_activity_status_filter,
)


def _item(suggestion_id: int, status: str) -> ReviewActivityDetailItem:
    return ReviewActivityDetailItem(
        suggestion_type="message",
        suggestion_id=suggestion_id,
        status=status,
        primary_label=f"Eintrag {suggestion_id}",
        excerpt="Lokaler Review-Eintrag",
        updated_at=f"2026-07-06T0{suggestion_id}:00:00",
        created_task_id=None,
    )


def test_normalize_review_activity_status_filter_strips_and_lowercases() -> None:
    assert normalize_review_activity_status_filter(" Converted ") == "converted"


def test_review_activity_status_filter_all_returns_all_items() -> None:
    items = (_item(1, "pending"), _item(2, "approved"), _item(3, "converted"))

    result = build_review_activity_status_filter(items, "all")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1, 2, 3]


def test_review_activity_status_filter_pending_returns_pending_items() -> None:
    items = (_item(1, "pending"), _item(2, "approved"))

    result = build_review_activity_status_filter(items, "pending")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1]


def test_review_activity_status_filter_open_returns_pending_and_edited_items() -> None:
    items = (_item(1, "pending"), _item(2, "edited"), _item(3, "approved"))

    result = build_review_activity_status_filter(items, "open")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1, 2]


def test_review_activity_status_filter_converted_returns_converted_items() -> None:
    items = (_item(1, "pending"), _item(2, "converted"))

    result = build_review_activity_status_filter(items, "converted")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [2]


def test_review_activity_status_filter_invalid_filter_is_safe() -> None:
    result = build_review_activity_status_filter((_item(1, "pending"),), "komisch")

    assert result.is_valid is False
    assert result.items == ()
    assert result.error_message == INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE


def test_review_activity_status_filter_has_safe_read_only_flags() -> None:
    result = build_review_activity_status_filter(None, "all")

    assert result.items == ()
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
