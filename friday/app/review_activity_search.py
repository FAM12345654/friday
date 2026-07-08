"""Read-only search for local review activity detail items."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from friday.app.review_activity_detail_view import ReviewActivityDetailItem


INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE = "Ungueltiger Review-Suchbegriff."
DEFAULT_REVIEW_ACTIVITY_SEARCH_MIN_QUERY_LENGTH = 2
DEFAULT_REVIEW_ACTIVITY_SEARCH_RESULT_LIMIT = 25


@dataclass(frozen=True)
class ReviewActivitySearchResult:
    """Read-only result for searching local review activity details."""

    requested_query: str
    normalized_query: str
    is_valid: bool
    items: tuple[ReviewActivityDetailItem, ...]
    total_matches: int
    result_limit: int
    was_limited: bool
    error_message: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool


def normalize_review_activity_search_query(value: object) -> str:
    """Normalize a user-visible review activity search query."""
    return " ".join(str(value or "").strip().lower().split())


def _item_search_text(item: ReviewActivityDetailItem) -> str:
    parts = [
        item.suggestion_type,
        str(item.suggestion_id or ""),
        item.status,
        item.primary_label,
        item.excerpt,
        str(item.created_task_id or ""),
    ]
    return " ".join(part.strip().lower() for part in parts if part)


def build_review_activity_search(
    items: Iterable[ReviewActivityDetailItem] | None,
    query: object,
    *,
    min_query_length: int = DEFAULT_REVIEW_ACTIVITY_SEARCH_MIN_QUERY_LENGTH,
    result_limit: int = DEFAULT_REVIEW_ACTIVITY_SEARCH_RESULT_LIMIT,
) -> ReviewActivitySearchResult:
    """Search local review activity detail items without side effects."""
    requested_query = str(query or "")
    normalized_query = normalize_review_activity_search_query(query)
    normalized_items = tuple(items or ())
    safe_min_query_length = max(1, int(min_query_length or 1))
    safe_result_limit = max(1, int(result_limit or 1))

    if len(normalized_query) < safe_min_query_length:
        return ReviewActivitySearchResult(
            requested_query=requested_query,
            normalized_query=normalized_query,
            is_valid=False,
            items=(),
            total_matches=0,
            result_limit=safe_result_limit,
            was_limited=False,
            error_message=INVALID_REVIEW_ACTIVITY_SEARCH_QUERY_MESSAGE,
            preview_only=True,
            persisted=False,
            external_action_used=False,
        )

    matched_items = tuple(
        item for item in normalized_items if normalized_query in _item_search_text(item)
    )
    limited_items = matched_items[:safe_result_limit]

    return ReviewActivitySearchResult(
        requested_query=requested_query,
        normalized_query=normalized_query,
        is_valid=True,
        items=limited_items,
        total_matches=len(matched_items),
        result_limit=safe_result_limit,
        was_limited=len(matched_items) > safe_result_limit,
        error_message=None,
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )
