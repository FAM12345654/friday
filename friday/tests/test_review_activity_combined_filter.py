"""Tests for the read-only review activity combined filter model."""

from __future__ import annotations

from friday.app.review_activity_combined_filter import (
    build_review_activity_combined_filter,
)
from friday.app.review_activity_detail_view import ReviewActivityDetailItem
from friday.app.review_activity_search import (
    INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE,
)
from friday.app.review_activity_status_filter import (
    INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE,
)
from friday.app.review_activity_type_filter import (
    INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE,
)


def _item(
    suggestion_id: int,
    suggestion_type: str,
    status: str,
    primary_label: str,
    excerpt: str,
    created_task_id: int | None = None,
) -> ReviewActivityDetailItem:
    return ReviewActivityDetailItem(
        suggestion_type=suggestion_type,
        suggestion_id=suggestion_id,
        status=status,
        primary_label=primary_label,
        excerpt=excerpt,
        updated_at=f"2026-07-06T0{suggestion_id}:00:00",
        created_task_id=created_task_id,
    )


def test_review_activity_combined_filter_status_and_type() -> None:
    items = (
        _item(1, "message", "pending", "Chef", "Termin"),
        _item(2, "task", "pending", "Rechnung", "Lokal pruefen"),
        _item(3, "task", "approved", "Einkauf", "Liste"),
    )

    result = build_review_activity_combined_filter(
        items,
        status_filter="pending",
        type_filter="task",
    )

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [2]
    assert result.query_applied is False
    assert result.total_matches == 1


def test_review_activity_combined_filter_open_status_and_type() -> None:
    items = (
        _item(1, "task", "pending", "Chef", "Termin"),
        _item(2, "task", "edited", "Rechnung", "Lokal pruefen"),
        _item(3, "task", "approved", "Einkauf", "Liste"),
        _item(4, "message", "pending", "Kontakt", "Notiz"),
    )

    result = build_review_activity_combined_filter(
        items,
        status_filter="open",
        type_filter="task",
    )

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1, 2]


def test_review_activity_combined_filter_status_and_search() -> None:
    items = (
        _item(1, "message", "pending", "Chef", "Termin bestaetigen"),
        _item(2, "task", "approved", "Chef", "Rechnung pruefen"),
        _item(3, "message", "pending", "Einkauf", "Liste"),
    )

    result = build_review_activity_combined_filter(
        items,
        status_filter="pending",
        query="chef",
    )

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1]
    assert result.query_applied is True
    assert result.total_matches == 1


def test_review_activity_combined_filter_type_and_search() -> None:
    items = (
        _item(1, "message", "pending", "Chef", "Termin bestaetigen"),
        _item(2, "task", "converted", "Chef", "Rechnung pruefen"),
        _item(3, "task", "converted", "Einkauf", "Liste"),
    )

    result = build_review_activity_combined_filter(
        items,
        type_filter="task",
        query="chef",
    )

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [2]


def test_review_activity_combined_filter_status_type_and_search_preserves_order() -> None:
    items = (
        _item(3, "task", "converted", "Rechnung", "Bitte lokal pruefen"),
        _item(1, "task", "converted", "Rechnung", "Noch einmal pruefen"),
        _item(2, "message", "converted", "Rechnung", "Nachricht"),
        _item(4, "task", "pending", "Rechnung", "Spaeter pruefen"),
    )

    result = build_review_activity_combined_filter(
        items,
        status_filter="converted",
        type_filter="task",
        query="rechnung",
    )

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [3, 1]


def test_review_activity_combined_filter_empty_query_is_skipped() -> None:
    items = (
        _item(1, "message", "pending", "Chef", "Termin"),
        _item(2, "message", "approved", "Einkauf", "Liste"),
    )

    result = build_review_activity_combined_filter(
        items,
        type_filter="message",
        query="   ",
    )

    assert result.is_valid is True
    assert result.query_applied is False
    assert [item.suggestion_id for item in result.items] == [1, 2]


def test_review_activity_combined_filter_invalid_status_is_safe() -> None:
    result = build_review_activity_combined_filter(
        (_item(1, "message", "pending", "Chef", "Termin"),),
        status_filter="komisch",
        type_filter="message",
        query="chef",
    )

    assert result.is_valid is False
    assert result.items == ()
    assert result.error_message == INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False


def test_review_activity_combined_filter_invalid_type_is_safe() -> None:
    result = build_review_activity_combined_filter(
        (_item(1, "message", "pending", "Chef", "Termin"),),
        status_filter="pending",
        type_filter="contact",
        query="chef",
    )

    assert result.is_valid is False
    assert result.items == ()
    assert result.error_message == INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False


def test_review_activity_combined_filter_short_non_empty_query_is_safe() -> None:
    result = build_review_activity_combined_filter(
        (_item(1, "message", "pending", "Chef", "Termin"),),
        query="c",
    )

    assert result.is_valid is False
    assert result.items == ()
    assert result.query_applied is True
    assert result.error_message == INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE


def test_review_activity_combined_filter_limits_search_results() -> None:
    items = tuple(
        _item(suggestion_id, "message", "pending", "Chef", "Termin")
        for suggestion_id in range(1, 5)
    )

    result = build_review_activity_combined_filter(
        items,
        query="chef",
        result_limit=2,
    )

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1, 2]
    assert result.total_matches == 4
    assert result.result_limit == 2
    assert result.was_limited is True


def test_review_activity_combined_filter_defaults_are_safe_read_only() -> None:
    result = build_review_activity_combined_filter(None)

    assert result.is_valid is True
    assert result.items == ()
    assert result.total_matches == 0
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
