"""Read-only status filter for local review activity detail items."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from friday.app.review_activity_detail_view import ReviewActivityDetailItem


VALID_REVIEW_ACTIVITY_STATUS_FILTERS = frozenset(
    {
        "all",
        "open",
        "pending",
        "edited",
        "approved",
        "rejected",
        "converted",
    }
)

OPEN_REVIEW_ACTIVITY_STATUSES = frozenset({"pending", "edited"})
INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE = "Ungültiger Review-Statusfilter."


@dataclass(frozen=True)
class ReviewActivityStatusFilterResult:
    """Read-only result for filtering local review activity details."""

    requested_filter: str
    normalized_filter: str
    is_valid: bool
    items: tuple[ReviewActivityDetailItem, ...]
    error_message: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool


def normalize_review_activity_status_filter(value: object) -> str:
    """Normalize a user-visible review status filter value."""
    return str(value or "").strip().lower()


def build_review_activity_status_filter(
    items: Iterable[ReviewActivityDetailItem] | None,
    status_filter: object,
) -> ReviewActivityStatusFilterResult:
    """Filter local review activity detail items by status without side effects."""
    requested_filter = str(status_filter or "")
    normalized_filter = normalize_review_activity_status_filter(status_filter)
    normalized_items = tuple(items or ())

    if normalized_filter not in VALID_REVIEW_ACTIVITY_STATUS_FILTERS:
        return ReviewActivityStatusFilterResult(
            requested_filter=requested_filter,
            normalized_filter=normalized_filter,
            is_valid=False,
            items=(),
            error_message=INVALID_REVIEW_ACTIVITY_STATUS_FILTER_MESSAGE,
            preview_only=True,
            persisted=False,
            external_action_used=False,
        )

    if normalized_filter == "all":
        filtered_items = normalized_items
    elif normalized_filter == "open":
        filtered_items = tuple(
            item for item in normalized_items if item.status in OPEN_REVIEW_ACTIVITY_STATUSES
        )
    else:
        filtered_items = tuple(
            item for item in normalized_items if item.status == normalized_filter
        )

    return ReviewActivityStatusFilterResult(
        requested_filter=requested_filter,
        normalized_filter=normalized_filter,
        is_valid=True,
        items=filtered_items,
        error_message=None,
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )
