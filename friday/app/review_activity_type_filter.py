"""Read-only type filter for local review activity detail items."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from friday.app.review_activity_detail_view import ReviewActivityDetailItem


VALID_REVIEW_ACTIVITY_TYPE_FILTERS = frozenset({"all", "message", "task"})
INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE = "Ungueltiger Review-Typfilter."


@dataclass(frozen=True)
class ReviewActivityTypeFilterResult:
    """Read-only result for filtering local review activity details by type."""

    requested_filter: str
    normalized_filter: str
    is_valid: bool
    items: tuple[ReviewActivityDetailItem, ...]
    error_message: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool


def normalize_review_activity_type_filter(value: object) -> str:
    """Normalize a user-visible review type filter value."""
    return str(value or "").strip().lower()


def build_review_activity_type_filter(
    items: Iterable[ReviewActivityDetailItem] | None,
    type_filter: object,
) -> ReviewActivityTypeFilterResult:
    """Filter local review activity detail items by type without side effects."""
    requested_filter = str(type_filter or "")
    normalized_filter = normalize_review_activity_type_filter(type_filter)
    normalized_items = tuple(items or ())

    if normalized_filter not in VALID_REVIEW_ACTIVITY_TYPE_FILTERS:
        return ReviewActivityTypeFilterResult(
            requested_filter=requested_filter,
            normalized_filter=normalized_filter,
            is_valid=False,
            items=(),
            error_message=INVALID_REVIEW_ACTIVITY_TYPE_FILTER_MESSAGE,
            preview_only=True,
            persisted=False,
            external_action_used=False,
        )

    if normalized_filter == "all":
        filtered_items = normalized_items
    else:
        filtered_items = tuple(
            item for item in normalized_items if item.suggestion_type == normalized_filter
        )

    return ReviewActivityTypeFilterResult(
        requested_filter=requested_filter,
        normalized_filter=normalized_filter,
        is_valid=True,
        items=filtered_items,
        error_message=None,
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )
