from friday.agents.message_agent import MessageAgent
from friday.agents.task_agent import TaskAgent
from friday.app.review_batch_apply_guard import (
    REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
    REVIEW_BATCH_CREATE_TASKS_TOKEN,
    REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN,
    check_review_batch_apply_allowed,
)
from friday.app.review_batch_apply_model import (
    ReviewBatchApplyItem,
    ReviewBatchApplyResult,
    apply_review_batch_selection,
)
from friday.storage.database import setup_local_database


def _build_agents(tmp_path):
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    message_agent = MessageAgent(db_path=db_file)
    task_agent = TaskAgent(db_path=db_file)
    return message_agent, task_agent


def _set_messages(message_agent: MessageAgent, messages: list[dict]) -> None:
    message_agent.get_messages = lambda: messages  # type: ignore[method-assign]
    for message in messages:
        sender = message.get("sender")
        if sender:
            message_agent.contact_repository.create_contact(  # type: ignore[union-attr]
                name=sender,
                contact_type="kunde",
                notes="Testkunde fuer Review Batch Apply.",
                betreuer="philip",
            )


def _allowed_guard(action_type: str, selected_ids: list[int], token: str):
    return check_review_batch_apply_allowed(
        action_type=action_type,
        selected_ids=selected_ids,
        visible_pending_ids=selected_ids,
        preview_was_shown=True,
        approval_token=token,
        scanner_smoke_passed=True,
        external_actions_enabled=False,
    )


def test_review_batch_apply_blocks_when_guard_blocks(tmp_path) -> None:
    message_agent, _task_agent = _build_agents(tmp_path)
    _set_messages(
        message_agent,
        [{"id": 1, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"}],
    )
    suggestion = message_agent.generate_local_suggestions()[0]
    guard = check_review_batch_apply_allowed(
        action_type="approve_messages",
        selected_ids=[1],
        visible_pending_ids=[1],
        preview_was_shown=True,
        approval_token="JA",
        scanner_smoke_passed=True,
        external_actions_enabled=False,
    )

    result = apply_review_batch_selection(
        guard_result=guard,
        visible_items=(
            ReviewBatchApplyItem(
                virtual_id=1,
                suggestion_id=suggestion["id"],
                suggestion_type="message",
            ),
        ),
        message_agent=message_agent,
    )

    assert result.applied is False
    assert "invalid_token" in result.blocked_reasons
    unchanged = message_agent.suggestion_repository.get_suggestion_by_id(suggestion["id"])  # type: ignore[union-attr]
    assert unchanged["status"] == "pending"


def test_review_batch_apply_approves_message_suggestions_locally(tmp_path) -> None:
    message_agent, _task_agent = _build_agents(tmp_path)
    _set_messages(
        message_agent,
        [
            {"id": 1, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 2, "sender": "Team", "text": "Kannst du übermorgen kurz sprechen?"},
        ],
    )
    suggestions = message_agent.generate_local_suggestions()
    guard = _allowed_guard(
        "approve_messages",
        [1, 2],
        REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
    )

    result = apply_review_batch_selection(
        guard_result=guard,
        visible_items=(
            ReviewBatchApplyItem(1, suggestions[0]["id"], "message"),
            ReviewBatchApplyItem(2, suggestions[1]["id"], "message"),
        ),
        message_agent=message_agent,
    )

    assert result.applied is True
    assert result.affected_ids == (suggestions[0]["id"], suggestions[1]["id"])
    assert result.created_task_ids == ()
    assert result.external_action_used is False
    updated = [
        message_agent.suggestion_repository.get_suggestion_by_id(item["id"])  # type: ignore[union-attr]
        for item in suggestions
    ]
    assert [item["status"] for item in updated] == ["approved", "approved"]


def test_review_batch_apply_rejects_message_and_task_suggestions_locally(tmp_path) -> None:
    message_agent, _task_agent = _build_agents(tmp_path)
    _set_messages(
        message_agent,
        [
            {"id": 1, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 2, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    guard = check_review_batch_apply_allowed(
        action_type="reject_suggestions",
        selected_ids=[1, 2],
        visible_pending_ids=[1, 2],
        preview_was_shown=True,
        approval_token=REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN,
        scanner_smoke_passed=True,
        external_actions_enabled=False,
        contains_mixed_suggestion_types=True,
    )

    result = apply_review_batch_selection(
        guard_result=guard,
        visible_items=(
            ReviewBatchApplyItem(1, message_suggestion["id"], "message"),
            ReviewBatchApplyItem(2, task_suggestion["id"], "task"),
        ),
        message_agent=message_agent,
    )

    assert result.applied is True
    updated_message = message_agent.suggestion_repository.get_suggestion_by_id(message_suggestion["id"])  # type: ignore[union-attr]
    updated_task = message_agent.task_suggestion_repository.get_task_suggestion_by_id(task_suggestion["id"])  # type: ignore[union-attr]
    assert updated_message["status"] == "rejected"
    assert updated_task["status"] == "rejected"


def test_review_batch_apply_creates_tasks_from_task_suggestions_locally(tmp_path) -> None:
    message_agent, task_agent = _build_agents(tmp_path)
    _set_messages(
        message_agent,
        [
            {"id": 1, "sender": "Chef", "text": "Bitte bitte die Rechnung prüfen."},
            {"id": 2, "sender": "Team", "text": "Kannst du bitte den Report fertig machen?"},
        ],
    )
    suggestions = message_agent.generate_local_task_suggestions()
    guard = _allowed_guard(
        "create_tasks",
        [1, 2],
        REVIEW_BATCH_CREATE_TASKS_TOKEN,
    )

    result = apply_review_batch_selection(
        guard_result=guard,
        visible_items=(
            ReviewBatchApplyItem(1, suggestions[0]["id"], "task"),
            ReviewBatchApplyItem(2, suggestions[1]["id"], "task"),
        ),
        message_agent=message_agent,
        task_agent=task_agent,
    )

    assert result.applied is True
    assert len(result.created_task_ids) == 2
    for suggestion in suggestions:
        converted = message_agent.task_suggestion_repository.get_task_suggestion_by_id(suggestion["id"])  # type: ignore[union-attr]
        assert converted["status"] == "converted"
        assert converted["created_task_id"] is not None
    created_titles = {task["title"] for task in task_agent.get_open_tasks()}
    assert {item["title"] for item in suggestions}.issubset(created_titles)


def test_review_batch_apply_requires_task_agent_for_create_tasks(tmp_path) -> None:
    message_agent, _task_agent = _build_agents(tmp_path)
    _set_messages(
        message_agent,
        [{"id": 1, "sender": "Chef", "text": "Bitte bitte die Rechnung prüfen."}],
    )
    suggestion = message_agent.generate_local_task_suggestions()[0]
    guard = _allowed_guard(
        "create_tasks",
        [1],
        REVIEW_BATCH_CREATE_TASKS_TOKEN,
    )

    result = apply_review_batch_selection(
        guard_result=guard,
        visible_items=(ReviewBatchApplyItem(1, suggestion["id"], "task"),),
        message_agent=message_agent,
        task_agent=None,
    )

    assert result.applied is False
    assert result.blocked_reasons == ("task_agent_missing",)


def test_review_batch_apply_blocks_stale_converted_task_suggestion(tmp_path) -> None:
    message_agent, task_agent = _build_agents(tmp_path)
    _set_messages(
        message_agent,
        [{"id": 1, "sender": "Chef", "text": "Bitte bitte die Rechnung prüfen."}],
    )
    suggestion = message_agent.generate_local_task_suggestions()[0]
    guard = _allowed_guard(
        "create_tasks",
        [1],
        REVIEW_BATCH_CREATE_TASKS_TOKEN,
    )
    visible_items = (ReviewBatchApplyItem(1, suggestion["id"], "task"),)
    before_count = len(task_agent.get_open_tasks())
    first = apply_review_batch_selection(
        guard_result=guard,
        visible_items=visible_items,
        message_agent=message_agent,
        task_agent=task_agent,
    )

    second = apply_review_batch_selection(
        guard_result=guard,
        visible_items=visible_items,
        message_agent=message_agent,
        task_agent=task_agent,
    )

    assert first.applied is True
    assert second.applied is False
    assert "not_pending" in second.blocked_reasons
    assert "already_converted" in second.blocked_reasons
    assert len(task_agent.get_open_tasks()) == before_count + len(first.created_task_ids)


def test_review_batch_apply_blocks_missing_visible_item(tmp_path) -> None:
    message_agent, _task_agent = _build_agents(tmp_path)
    guard = _allowed_guard(
        "approve_messages",
        [1],
        REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
    )

    result = apply_review_batch_selection(
        guard_result=guard,
        visible_items=(),
        message_agent=message_agent,
    )

    assert result.applied is False
    assert result.blocked_reasons == ("missing_visible_item",)


def test_review_batch_apply_has_safe_result_flags(tmp_path) -> None:
    message_agent, _task_agent = _build_agents(tmp_path)
    _set_messages(
        message_agent,
        [{"id": 1, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"}],
    )
    suggestion = message_agent.generate_local_suggestions()[0]
    guard = _allowed_guard(
        "approve_messages",
        [1],
        REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
    )

    result = apply_review_batch_selection(
        guard_result=guard,
        visible_items=(ReviewBatchApplyItem(1, suggestion["id"], "message"),),
        message_agent=message_agent,
    )

    assert isinstance(result, ReviewBatchApplyResult)
    assert result.preview_only is False
    assert result.persisted is True
    assert result.external_action_used is False
