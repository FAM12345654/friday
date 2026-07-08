"""Read-only model for local review activity detail views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


ReviewActivityDetailType = Literal["message", "task"]

DEFAULT_EXCERPT_LIMIT = 80


@dataclass(frozen=True)
class ReviewActivityDetailItem:
    """One read-only local review activity detail item."""

    suggestion_type: ReviewActivityDetailType
    suggestion_id: int | None
    status: str
    primary_label: str
    excerpt: str
    updated_at: str
    created_task_id: int | None


@dataclass(frozen=True)
class ReviewActivityDetailView:
    """Read-only detail view of local review activity."""

    message_items: tuple[ReviewActivityDetailItem, ...]
    task_items: tuple[ReviewActivityDetailItem, ...]
    all_items: tuple[ReviewActivityDetailItem, ...]
    preview_only: bool
    persisted: bool
    external_action_used: bool


def _as_int_or_none(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdecimal():
        return int(value.strip())
    return None


def _clean_text(value: object, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text if text else fallback


def _normalize_status(value: object) -> str:
    return _clean_text(value).lower()


def _updated_at(value: dict[str, Any]) -> str:
    return _clean_text(value.get("updated_at") or value.get("created_at"))


def _first_text(value: dict[str, Any], keys: tuple[str, ...], fallback: str = "") -> str:
    for key in keys:
        text = _clean_text(value.get(key))
        if text:
            return text
    return fallback


def _excerpt(value: object, limit: int) -> str:
    text = " ".join(_clean_text(value).split())
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 3)].rstrip()}..."


def _message_item(
    suggestion: dict[str, Any],
    *,
    excerpt_limit: int,
) -> ReviewActivityDetailItem:
    sender = _first_text(
        suggestion,
        ("sender", "from", "recipient"),
        fallback="Unbekannt",
    )
    text = _first_text(
        suggestion,
        ("text", "message_text", "suggested_text", "draft_text", "body"),
    )
    return ReviewActivityDetailItem(
        suggestion_type="message",
        suggestion_id=_as_int_or_none(suggestion.get("id")),
        status=_normalize_status(suggestion.get("status")),
        primary_label=sender,
        excerpt=_excerpt(text, excerpt_limit),
        updated_at=_updated_at(suggestion),
        created_task_id=None,
    )


def _task_item(
    suggestion: dict[str, Any],
    *,
    excerpt_limit: int,
) -> ReviewActivityDetailItem:
    title = _first_text(
        suggestion,
        ("title", "task_title", "suggested_title"),
        fallback="Ohne Titel",
    )
    notes = _first_text(
        suggestion,
        ("notes", "description", "text"),
        fallback=title,
    )
    return ReviewActivityDetailItem(
        suggestion_type="task",
        suggestion_id=_as_int_or_none(suggestion.get("id")),
        status=_normalize_status(suggestion.get("status")),
        primary_label=title,
        excerpt=_excerpt(notes, excerpt_limit),
        updated_at=_updated_at(suggestion),
        created_task_id=_as_int_or_none(suggestion.get("created_task_id")),
    )


def _sort_items(
    items: tuple[ReviewActivityDetailItem, ...],
) -> tuple[ReviewActivityDetailItem, ...]:
    return tuple(
        sorted(
            items,
            key=lambda item: (
                item.updated_at,
                item.suggestion_id if item.suggestion_id is not None else -1,
            ),
            reverse=True,
        )
    )


def build_review_activity_detail_view(
    message_suggestions: list[dict[str, Any]] | None,
    task_suggestions: list[dict[str, Any]] | None,
    *,
    excerpt_limit: int = DEFAULT_EXCERPT_LIMIT,
) -> ReviewActivityDetailView:
    """Build a read-only detail view from local review suggestion rows."""
    normalized_messages = list(message_suggestions or [])
    normalized_tasks = list(task_suggestions or [])

    message_items = _sort_items(
        tuple(
            _message_item(suggestion, excerpt_limit=excerpt_limit)
            for suggestion in normalized_messages
        )
    )
    task_items = _sort_items(
        tuple(
            _task_item(suggestion, excerpt_limit=excerpt_limit)
            for suggestion in normalized_tasks
        )
    )
    all_items = _sort_items(message_items + task_items)

    return ReviewActivityDetailView(
        message_items=message_items,
        task_items=task_items,
        all_items=all_items,
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )
