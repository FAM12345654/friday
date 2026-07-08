"""Read-only model for local review activity summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


ReviewActivitySuggestionType = Literal["message", "task"]

OPEN_REVIEW_STATUSES = frozenset({"pending", "edited"})


@dataclass(frozen=True)
class ReviewActivityCounts:
    """Status counts for one local review suggestion type."""

    total: int
    open: int
    approved: int
    rejected: int
    converted: int
    with_created_task_id: int


@dataclass(frozen=True)
class ReviewActivityRecentItem:
    """One recently changed local review suggestion."""

    suggestion_type: ReviewActivitySuggestionType
    suggestion_id: int | None
    status: str
    updated_at: str
    created_task_id: int | None


@dataclass(frozen=True)
class ReviewActivitySummary:
    """Read-only summary of local review activity."""

    message_counts: ReviewActivityCounts
    task_counts: ReviewActivityCounts
    recent_items: tuple[ReviewActivityRecentItem, ...]
    preview_only: bool
    persisted: bool
    external_action_used: bool


def _normalize_status(value: object) -> str:
    return str(value or "").strip().lower()


def _as_int_or_none(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdecimal():
        return int(value.strip())
    return None


def _updated_at(value: dict[str, Any]) -> str:
    return str(value.get("updated_at") or value.get("created_at") or "").strip()


def _build_counts(
    suggestions: list[dict[str, Any]],
    *,
    include_converted: bool,
) -> ReviewActivityCounts:
    statuses = [_normalize_status(item.get("status")) for item in suggestions]
    return ReviewActivityCounts(
        total=len(suggestions),
        open=sum(1 for status in statuses if status in OPEN_REVIEW_STATUSES),
        approved=statuses.count("approved"),
        rejected=statuses.count("rejected"),
        converted=statuses.count("converted") if include_converted else 0,
        with_created_task_id=sum(
            1 for item in suggestions if _as_int_or_none(item.get("created_task_id")) is not None
        )
        if include_converted
        else 0,
    )


def _recent_item(
    suggestion: dict[str, Any],
    suggestion_type: ReviewActivitySuggestionType,
) -> ReviewActivityRecentItem:
    return ReviewActivityRecentItem(
        suggestion_type=suggestion_type,
        suggestion_id=_as_int_or_none(suggestion.get("id")),
        status=_normalize_status(suggestion.get("status")),
        updated_at=_updated_at(suggestion),
        created_task_id=_as_int_or_none(suggestion.get("created_task_id"))
        if suggestion_type == "task"
        else None,
    )


def _build_recent_items(
    message_suggestions: list[dict[str, Any]],
    task_suggestions: list[dict[str, Any]],
    recent_limit: int,
) -> tuple[ReviewActivityRecentItem, ...]:
    candidates = [
        _recent_item(suggestion, "message")
        for suggestion in message_suggestions
        if _updated_at(suggestion)
    ]
    candidates.extend(
        _recent_item(suggestion, "task")
        for suggestion in task_suggestions
        if _updated_at(suggestion)
    )
    candidates.sort(key=lambda item: item.updated_at, reverse=True)
    return tuple(candidates[: max(0, recent_limit)])


def build_review_activity_summary(
    message_suggestions: list[dict[str, Any]] | None,
    task_suggestions: list[dict[str, Any]] | None,
    *,
    recent_limit: int = 5,
) -> ReviewActivitySummary:
    """Build a read-only summary from local review suggestion rows."""
    normalized_messages = list(message_suggestions or [])
    normalized_tasks = list(task_suggestions or [])
    return ReviewActivitySummary(
        message_counts=_build_counts(
            normalized_messages,
            include_converted=False,
        ),
        task_counts=_build_counts(
            normalized_tasks,
            include_converted=True,
        ),
        recent_items=_build_recent_items(
            normalized_messages,
            normalized_tasks,
            recent_limit,
        ),
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )
