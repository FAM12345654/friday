"""Side-effect-free guard for future local review batch apply actions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal


REVIEW_BATCH_APPROVE_MESSAGES_TOKEN = "BATCH FREIGEBEN"
REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN = "BATCH ABLEHNEN"
REVIEW_BATCH_CREATE_TASKS_TOKEN = "BATCH AUFGABEN ERSTELLEN"

ReviewBatchApplyAction = Literal[
    "approve_messages",
    "reject_suggestions",
    "create_tasks",
]

ReviewBatchApplyBlockReason = Literal[
    "preview_missing",
    "invalid_action_type",
    "missing_selection",
    "ids_not_visible",
    "ids_not_pending",
    "mixed_types_not_allowed",
    "invalid_token",
    "scanner_smoke_failed",
    "external_actions_enabled",
    "already_processed",
]

_ACTION_TOKENS: dict[str, str] = {
    "approve_messages": REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
    "reject_suggestions": REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN,
    "create_tasks": REVIEW_BATCH_CREATE_TASKS_TOKEN,
}

_LOCAL_ALLOWED_ACTIONS = frozenset(_ACTION_TOKENS)


@dataclass(frozen=True)
class ReviewBatchApplyGuardResult:
    """Structured guard result for future local review batch actions."""

    allowed: bool
    action_type: str
    selected_ids: tuple[int, ...]
    blocked_reasons: tuple[ReviewBatchApplyBlockReason, ...]
    required_token: str | None
    message: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool


def _normalize_ids(ids: Iterable[int]) -> tuple[int, ...]:
    normalized: list[int] = []
    seen: set[int] = set()
    for item in ids:
        if item not in seen:
            seen.add(item)
            normalized.append(item)
    return tuple(normalized)


def check_review_batch_apply_allowed(
    *,
    action_type: str,
    selected_ids: Iterable[int],
    visible_pending_ids: Iterable[int],
    preview_was_shown: bool,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    external_actions_enabled: bool,
    contains_mixed_suggestion_types: bool = False,
    contains_already_processed_suggestions: bool = False,
) -> ReviewBatchApplyGuardResult:
    """Check whether a future local review batch action would be allowed."""
    normalized_action = (action_type or "").strip()
    selected_id_tuple = _normalize_ids(selected_ids)
    visible_pending_id_tuple = _normalize_ids(visible_pending_ids)
    visible_pending_id_set = set(visible_pending_id_tuple)
    blocked_reasons: list[ReviewBatchApplyBlockReason] = []

    required_token = _ACTION_TOKENS.get(normalized_action)

    if not preview_was_shown:
        blocked_reasons.append("preview_missing")

    if normalized_action not in _LOCAL_ALLOWED_ACTIONS:
        blocked_reasons.append("invalid_action_type")

    if not selected_id_tuple:
        blocked_reasons.append("missing_selection")

    if selected_id_tuple and any(item not in visible_pending_id_set for item in selected_id_tuple):
        blocked_reasons.append("ids_not_visible")
        blocked_reasons.append("ids_not_pending")

    if contains_mixed_suggestion_types and normalized_action in {
        "approve_messages",
        "create_tasks",
    }:
        blocked_reasons.append("mixed_types_not_allowed")

    if contains_already_processed_suggestions:
        blocked_reasons.append("already_processed")

    if (approval_token or "").strip() != required_token:
        blocked_reasons.append("invalid_token")

    if not scanner_smoke_passed:
        blocked_reasons.append("scanner_smoke_failed")

    if external_actions_enabled:
        blocked_reasons.append("external_actions_enabled")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return ReviewBatchApplyGuardResult(
        allowed=allowed,
        action_type=normalized_action,
        selected_ids=selected_id_tuple,
        blocked_reasons=unique_blocked_reasons,
        required_token=required_token,
        message=None if allowed else "Batch-Aktion wurde nicht freigegeben.",
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )
