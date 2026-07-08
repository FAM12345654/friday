"""Local review batch apply model guarded by an explicit safety result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from friday.app.review_batch_apply_guard import ReviewBatchApplyGuardResult


ReviewBatchApplySuggestionType = Literal["message", "task"]


@dataclass(frozen=True)
class ReviewBatchApplyItem:
    """One visible batch item mapped to a real local suggestion."""

    virtual_id: int
    suggestion_id: int
    suggestion_type: ReviewBatchApplySuggestionType


@dataclass(frozen=True)
class ReviewBatchApplyResult:
    """Structured result for a guarded local review batch apply."""

    applied: bool
    action_type: str
    affected_ids: tuple[int, ...]
    created_task_ids: tuple[int, ...]
    blocked_reasons: tuple[str, ...]
    message: str
    preview_only: bool
    persisted: bool
    external_action_used: bool


class _MessageAgentProtocol(Protocol):
    suggestion_repository: object | None
    task_suggestion_repository: object | None

    def approve_suggestion(self, suggestion_id: int) -> dict | None:
        ...

    def reject_suggestion(self, suggestion_id: int) -> dict | None:
        ...

    def reject_task_suggestion(self, suggestion_id: int) -> dict | None:
        ...

    def mark_task_suggestion_converted(
        self,
        suggestion_id: int,
        created_task_id: int,
    ) -> dict | None:
        ...


class _TaskAgentProtocol(Protocol):
    def create_task(
        self,
        title: str,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        priority: str | None = None,
    ) -> dict:
        ...


def _blocked_result(
    *,
    action_type: str,
    blocked_reasons: tuple[str, ...],
    message: str = "Batch-Aktion wurde nicht ausgefuehrt.",
) -> ReviewBatchApplyResult:
    return ReviewBatchApplyResult(
        applied=False,
        action_type=action_type,
        affected_ids=(),
        created_task_ids=(),
        blocked_reasons=blocked_reasons,
        message=message,
        preview_only=True,
        persisted=False,
        external_action_used=False,
    )


def _items_for_guard_selection(
    guard_result: ReviewBatchApplyGuardResult,
    items: tuple[ReviewBatchApplyItem, ...],
) -> tuple[ReviewBatchApplyItem, ...] | None:
    item_by_virtual_id = {item.virtual_id: item for item in items}
    selected_items: list[ReviewBatchApplyItem] = []
    for virtual_id in guard_result.selected_ids:
        item = item_by_virtual_id.get(virtual_id)
        if item is None:
            return None
        selected_items.append(item)
    return tuple(selected_items)


def _message_suggestion_by_id(
    message_agent: _MessageAgentProtocol,
    suggestion_id: int,
) -> dict | None:
    repository = message_agent.suggestion_repository
    if repository is None:
        return None
    return repository.get_suggestion_by_id(suggestion_id)  # type: ignore[attr-defined]


def _task_suggestion_by_id(
    message_agent: _MessageAgentProtocol,
    suggestion_id: int,
) -> dict | None:
    repository = message_agent.task_suggestion_repository
    if repository is None:
        return None
    return repository.get_task_suggestion_by_id(suggestion_id)  # type: ignore[attr-defined]


def _is_pending_like(suggestion: dict | None) -> bool:
    if suggestion is None:
        return False
    return str(suggestion.get("status") or "").lower() in {"pending", "edited"}


def _preflight_selected_items(
    *,
    action_type: str,
    selected_items: tuple[ReviewBatchApplyItem, ...],
    message_agent: _MessageAgentProtocol,
) -> tuple[str, ...]:
    blocked_reasons: list[str] = []

    for item in selected_items:
        if action_type == "approve_messages" and item.suggestion_type != "message":
            blocked_reasons.append("wrong_suggestion_type")
            continue
        if action_type == "create_tasks" and item.suggestion_type != "task":
            blocked_reasons.append("wrong_suggestion_type")
            continue

        if item.suggestion_type == "message":
            suggestion = _message_suggestion_by_id(message_agent, item.suggestion_id)
            if not _is_pending_like(suggestion):
                blocked_reasons.append("not_pending")
        else:
            suggestion = _task_suggestion_by_id(message_agent, item.suggestion_id)
            if not _is_pending_like(suggestion):
                blocked_reasons.append("not_pending")
            if suggestion is not None and suggestion.get("created_task_id") is not None:
                blocked_reasons.append("already_converted")

    return tuple(dict.fromkeys(blocked_reasons))


def apply_review_batch_selection(
    *,
    guard_result: ReviewBatchApplyGuardResult,
    visible_items: tuple[ReviewBatchApplyItem, ...],
    message_agent: _MessageAgentProtocol,
    task_agent: _TaskAgentProtocol | None = None,
) -> ReviewBatchApplyResult:
    """Apply one guarded local review batch action."""
    action_type = guard_result.action_type
    if not guard_result.allowed:
        return _blocked_result(
            action_type=action_type,
            blocked_reasons=tuple(guard_result.blocked_reasons),
            message=guard_result.message or "Batch-Aktion wurde nicht freigegeben.",
        )

    selected_items = _items_for_guard_selection(guard_result, visible_items)
    if selected_items is None:
        return _blocked_result(
            action_type=action_type,
            blocked_reasons=("missing_visible_item",),
        )

    if action_type not in {"approve_messages", "reject_suggestions", "create_tasks"}:
        return _blocked_result(
            action_type=action_type,
            blocked_reasons=("unsupported_action",),
        )

    if action_type == "create_tasks" and task_agent is None:
        return _blocked_result(
            action_type=action_type,
            blocked_reasons=("task_agent_missing",),
        )

    preflight_blocked_reasons = _preflight_selected_items(
        action_type=action_type,
        selected_items=selected_items,
        message_agent=message_agent,
    )
    if preflight_blocked_reasons:
        return _blocked_result(
            action_type=action_type,
            blocked_reasons=preflight_blocked_reasons,
        )

    affected_ids: list[int] = []
    created_task_ids: list[int] = []

    for item in selected_items:
        if action_type == "approve_messages":
            updated = message_agent.approve_suggestion(item.suggestion_id)
            if updated is not None:
                affected_ids.append(item.suggestion_id)
            continue

        if action_type == "reject_suggestions":
            if item.suggestion_type == "message":
                updated = message_agent.reject_suggestion(item.suggestion_id)
            else:
                updated = message_agent.reject_task_suggestion(item.suggestion_id)
            if updated is not None:
                affected_ids.append(item.suggestion_id)
            continue

        if action_type == "create_tasks" and task_agent is not None:
            suggestion = _task_suggestion_by_id(message_agent, item.suggestion_id)
            if suggestion is None:
                continue
            task = task_agent.create_task(
                title=str(suggestion.get("title") or ""),
                category=suggestion.get("category"),
                due_date=suggestion.get("due_date"),
                notes=suggestion.get("notes"),
                priority=suggestion.get("priority"),
            )
            created_task_id = int(task["id"])
            message_agent.mark_task_suggestion_converted(
                item.suggestion_id,
                created_task_id,
            )
            affected_ids.append(item.suggestion_id)
            created_task_ids.append(created_task_id)

    return ReviewBatchApplyResult(
        applied=bool(affected_ids),
        action_type=action_type,
        affected_ids=tuple(affected_ids),
        created_task_ids=tuple(created_task_ids),
        blocked_reasons=(),
        message="Batch-Aktion wurde lokal ausgefuehrt.",
        preview_only=False,
        persisted=True,
        external_action_used=False,
    )
