"""Tests for the read-only review activity search model."""

from __future__ import annotations

from friday.app.review_activity_detail_view import ReviewActivityDetailItem
from friday.app.review_activity_search import (
    INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE,
    build_review_activity_search,
    normalize_review_activity_search_query,
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


def test_normalize_review_activity_search_query_collapses_spaces() -> None:
    assert normalize_review_activity_search_query("  Chef   Termin  ") == "chef termin"


def test_review_activity_search_finds_primary_label() -> None:
    items = (
        _item(1, "message", "approved", "Chef", "Termin bestaetigen"),
        _item(2, "task", "converted", "Rechnung pruefen", "Lokale Aufgabe"),
    )

    result = build_review_activity_search(items, "chef")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [1]


def test_review_activity_search_finds_excerpt() -> None:
    items = (
        _item(1, "message", "approved", "Chef", "Termin bestaetigen"),
        _item(2, "task", "converted", "Rechnung pruefen", "Bitte lokal pruefen"),
    )

    result = build_review_activity_search(items, "lokal")

    assert result.is_valid is True
    assert [item.suggestion_id for item in result.items] == [2]


def test_review_activity_search_finds_status_and_type() -> None:
    items = (
        _item(1, "message", "approved", "Chef", "Termin bestaetigen"),
        _item(2, "task", "converted", "Rechnung pruefen", "Bitte lokal pruefen"),
    )

    status_result = build_review_activity_search(items, "converted")
    type_result = build_review_activity_search(items, "message")

    assert [item.suggestion_id for item in status_result.items] == [2]
    assert [item.suggestion_id for item in type_result.items] == [1]


def test_review_activity_search_finds_local_ids() -> None:
    items = (
        _item(12, "message", "approved", "Chef", "Termin bestaetigen"),
        _item(13, "task", "converted", "Rechnung pruefen", "Bitte lokal pruefen", 99),
    )

    suggestion_result = build_review_activity_search(items, "12")
    created_task_result = build_review_activity_search(items, "99")

    assert [item.suggestion_id for item in suggestion_result.items] == [12]
    assert [item.suggestion_id for item in created_task_result.items] == [13]


def test_review_activity_search_empty_query_is_safe() -> None:
    result = build_review_activity_search((_item(1, "message", "pending", "Chef", ""),), "   ")

    assert result.is_valid is False
    assert result.items == ()
    assert result.total_matches == 0
    assert result.was_limited is False
    assert result.error_message == INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE


def test_review_activity_search_short_query_is_safe() -> None:
    result = build_review_activity_search((_item(1, "message", "pending", "Chef", ""),), "c")

    assert result.is_valid is False
    assert result.items == ()
    assert result.error_message == INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE


def test_review_activity_search_without_matches_is_valid_empty() -> None:
    result = build_review_activity_search((_item(1, "message", "pending", "Chef", ""),), "zz")

    assert result.is_valid is True
    assert result.items == ()
    assert result.total_matches == 0
    assert result.error_message is None


def test_review_activity_search_limits_results() -> None:
    items = tuple(
        _item(suggestion_id, "message", "pending", "Chef", "Termin")
        for suggestion_id in range(1, 5)
    )

    result = build_review_activity_search(items, "chef", result_limit=2)

    assert [item.suggestion_id for item in result.items] == [1, 2]
    assert result.total_matches == 4
    assert result.result_limit == 2
    assert result.was_limited is True


def test_review_activity_search_treats_regex_like_query_as_literal() -> None:
    items = (
        _item(1, "message", "pending", "Chef", "Termin"),
        _item(2, "task", "converted", "Rechnung", "Bitte lokal pruefen"),
    )

    result = build_review_activity_search(items, ".*")

    assert result.is_valid is True
    assert result.items == ()


def test_review_activity_search_has_safe_read_only_flags() -> None:
    result = build_review_activity_search(None, "chef")

    assert result.items == ()
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
