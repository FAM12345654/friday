"""Review batch selection parser helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


ReviewBatchSelectionStatus = Literal[
    "selected",
    "all",
    "none",
    "back",
    "empty",
    "invalid",
]

REVIEW_BATCH_SELECTION_INVALID_MESSAGE = "Ungültige Auswahl. Bitte erneut versuchen."


@dataclass(frozen=True)
class ReviewBatchSelectionParseResult:
    raw_input: str
    normalized_input: str
    status: ReviewBatchSelectionStatus
    selected_ids: tuple[int, ...]
    invalid_tokens: tuple[str, ...]
    message: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool


def normalize_review_batch_selection_input(raw_input: str | None) -> str:
    """Normalize raw review batch selection input."""
    return (raw_input or "").strip().lower()


def _normalize_visible_ids(visible_ids: Iterable[int]) -> tuple[int, ...]:
    seen: set[int] = set()
    normalized: list[int] = []
    for item in visible_ids:
        if item not in seen:
            seen.add(item)
            normalized.append(item)
    return tuple(normalized)


def _build_result(
    *,
    raw_input: str,
    normalized_input: str,
    status: ReviewBatchSelectionStatus,
    selected_ids: tuple[int, ...] = (),
    invalid_tokens: tuple[str, ...] = (),
    message: str | None = None,
) -> ReviewBatchSelectionParseResult:
    return ReviewBatchSelectionParseResult(
        raw_input=raw_input,
        normalized_input=normalized_input,
        status=status,
        selected_ids=selected_ids,
        invalid_tokens=invalid_tokens,
        message=message,
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )


def parse_review_batch_selection(
    raw_input: str | None,
    visible_ids: Iterable[int],
) -> ReviewBatchSelectionParseResult:
    """Parse a local review batch selection without executing actions."""
    raw_value = raw_input or ""
    normalized = normalize_review_batch_selection_input(raw_input)
    visible_id_tuple = _normalize_visible_ids(visible_ids)
    visible_id_set = set(visible_id_tuple)

    if normalized == "":
        return _build_result(
            raw_input=raw_value,
            normalized_input=normalized,
            status="empty",
        )

    if normalized == "z":
        return _build_result(
            raw_input=raw_value,
            normalized_input=normalized,
            status="back",
        )

    if normalized == "none":
        return _build_result(
            raw_input=raw_value,
            normalized_input=normalized,
            status="none",
        )

    if normalized == "all":
        return _build_result(
            raw_input=raw_value,
            normalized_input=normalized,
            status="all",
            selected_ids=visible_id_tuple,
        )

    tokens = tuple(part.strip() for part in normalized.split(","))
    if any(token == "" for token in tokens):
        return _build_result(
            raw_input=raw_value,
            normalized_input=normalized,
            status="invalid",
            invalid_tokens=tuple(token for token in tokens if token == ""),
            message=REVIEW_BATCH_SELECTION_INVALID_MESSAGE,
        )

    selected: list[int] = []
    invalid_tokens: list[str] = []
    seen_selected: set[int] = set()

    for token in tokens:
        if not token.isdecimal():
            invalid_tokens.append(token)
            continue

        parsed_id = int(token)
        if parsed_id not in visible_id_set:
            invalid_tokens.append(token)
            continue

        if parsed_id not in seen_selected:
            seen_selected.add(parsed_id)
            selected.append(parsed_id)

    if invalid_tokens:
        return _build_result(
            raw_input=raw_value,
            normalized_input=normalized,
            status="invalid",
            invalid_tokens=tuple(invalid_tokens),
            message=REVIEW_BATCH_SELECTION_INVALID_MESSAGE,
        )

    return _build_result(
        raw_input=raw_value,
        normalized_input=normalized,
        status="selected",
        selected_ids=tuple(selected),
    )
