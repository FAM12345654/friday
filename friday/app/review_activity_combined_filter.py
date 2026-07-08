"""Read-only combined filter for local review activity detail items."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from friday.app.review_activity_detail_view import ReviewActivityDetailItem
from friday.app.review_activity_search import (
    DEFAULT_REVIEW_ACTIVITY_SEARCH_MIN_QUERY_LENGTH,
    DEFAULT_REVIEW_ACTIVITY_SEARCH_RESULT_LIMIT,
    build_review_activity_search,
    normalize_review_activity_search_query,
)
from friday.app.review_activity_status_filter import (
    build_review_activity_status_filter,
    normalize_review_activity_status_filter,
)
from friday.app.review_activity_type_filter import (
    build_review_activity_type_filter,
    normalize_review_activity_type_filter,
)


@dataclass(frozen=True)
class ReviewActivityCombinedFilterResult:
    """Read-only result for combining local review activity filters."""

    requested_status_filter: str
    normalized_status_filter: str
    requested_type_filter: str
    normalized_type_filter: str
    requested_query: str
    normalized_query: str
    query_applied: bool
    is_valid: bool
    items: tuple[ReviewActivityDetailItem, ...]
    total_matches: int
    result_limit: int
    was_limited: bool
    error_message: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool


def _safe_result_limit(value: int) -> int:
    return max(1, int(value or 1))


def build_review_activity_combined_filter(
    items: Iterable[ReviewActivityDetailItem] | None,
    *,
    status_filter: object = "all",
    type_filter: object = "all",
    query: object = "",
    min_query_length: int = DEFAULT_REVIEW_ACTIVITY_SEARCH_MIN_QUERY_LENGTH,
    result_limit: int = DEFAULT_REVIEW_ACTIVITY_SEARCH_RESULT_LIMIT,
) -> ReviewActivityCombinedFilterResult:
    """Filter local review activity detail items by status, type, and optional search."""
    requested_status_filter = str(status_filter or "")
    normalized_status_filter = normalize_review_activity_status_filter(status_filter)
    requested_type_filter = str(type_filter or "")
    normalized_type_filter = normalize_review_activity_type_filter(type_filter)
    requested_query = str(query or "")
    normalized_query = normalize_review_activity_search_query(query)
    safe_result_limit = _safe_result_limit(result_limit)
    normalized_items = tuple(items or ())

    status_result = build_review_activity_status_filter(
        normalized_items,
        status_filter,
    )
    if not status_result.is_valid:
        return ReviewActivityCombinedFilterResult(
            requested_status_filter=requested_status_filter,
            normalized_status_filter=normalized_status_filter,
            requested_type_filter=requested_type_filter,
            normalized_type_filter=normalized_type_filter,
            requested_query=requested_query,
            normalized_query=normalized_query,
            query_applied=False,
            is_valid=False,
            items=(),
            total_matches=0,
            result_limit=safe_result_limit,
            was_limited=False,
            error_message=status_result.error_message,
            preview_only=True,
            persisted=False,
            external_action_used=False,
        )

    type_result = build_review_activity_type_filter(
        status_result.items,
        type_filter,
    )
    if not type_result.is_valid:
        return ReviewActivityCombinedFilterResult(
            requested_status_filter=requested_status_filter,
            normalized_status_filter=normalized_status_filter,
            requested_type_filter=requested_type_filter,
            normalized_type_filter=normalized_type_filter,
            requested_query=requested_query,
            normalized_query=normalized_query,
            query_applied=False,
            is_valid=False,
            items=(),
            total_matches=0,
            result_limit=safe_result_limit,
            was_limited=False,
            error_message=type_result.error_message,
            preview_only=True,
            persisted=False,
            external_action_used=False,
        )

    if not normalized_query:
        return ReviewActivityCombinedFilterResult(
            requested_status_filter=requested_status_filter,
            normalized_status_filter=normalized_status_filter,
            requested_type_filter=requested_type_filter,
            normalized_type_filter=normalized_type_filter,
            requested_query=requested_query,
            normalized_query=normalized_query,
            query_applied=False,
            is_valid=True,
            items=type_result.items,
            total_matches=len(type_result.items),
            result_limit=safe_result_limit,
            was_limited=False,
            error_message=None,
            preview_only=True,
            persisted=False,
            external_action_used=False,
        )

    search_result = build_review_activity_search(
        type_result.items,
        query,
        min_query_length=min_query_length,
        result_limit=safe_result_limit,
    )
    return ReviewActivityCombinedFilterResult(
        requested_status_filter=requested_status_filter,
        normalized_status_filter=normalized_status_filter,
        requested_type_filter=requested_type_filter,
        normalized_type_filter=normalized_type_filter,
        requested_query=requested_query,
        normalized_query=normalized_query,
        query_applied=True,
        is_valid=search_result.is_valid,
        items=search_result.items,
        total_matches=search_result.total_matches,
        result_limit=search_result.result_limit,
        was_limited=search_result.was_limited,
        error_message=search_result.error_message,
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )
