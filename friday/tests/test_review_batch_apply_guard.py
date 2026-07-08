from friday.app.review_batch_apply_guard import (
    REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
    REVIEW_BATCH_CREATE_TASKS_TOKEN,
    REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN,
    ReviewBatchApplyGuardResult,
    check_review_batch_apply_allowed,
)


def _allowed_kwargs(**overrides):
    values = {
        "action_type": "approve_messages",
        "selected_ids": [1, 2],
        "visible_pending_ids": [1, 2, 3],
        "preview_was_shown": True,
        "approval_token": REVIEW_BATCH_APPROVE_MESSAGES_TOKEN,
        "scanner_smoke_passed": True,
        "external_actions_enabled": False,
    }
    values.update(overrides)
    return values


def test_review_batch_apply_guard_allows_message_approval_with_exact_token() -> None:
    result = check_review_batch_apply_allowed(**_allowed_kwargs())

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert result.required_token == REVIEW_BATCH_APPROVE_MESSAGES_TOKEN
    assert result.selected_ids == (1, 2)


def test_review_batch_apply_guard_allows_reject_with_exact_token() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(
            action_type="reject_suggestions",
            approval_token=REVIEW_BATCH_REJECT_SUGGESTIONS_TOKEN,
            contains_mixed_suggestion_types=True,
        )
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()


def test_review_batch_apply_guard_allows_task_creation_with_exact_token() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(
            action_type="create_tasks",
            approval_token=REVIEW_BATCH_CREATE_TASKS_TOKEN,
        )
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()


def test_review_batch_apply_guard_blocks_missing_preview() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(preview_was_shown=False)
    )

    assert result.allowed is False
    assert "preview_missing" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_missing_selection() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(selected_ids=[])
    )

    assert result.allowed is False
    assert "missing_selection" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_ids_not_visible_or_pending() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(selected_ids=[1, 4])
    )

    assert result.allowed is False
    assert "ids_not_visible" in result.blocked_reasons
    assert "ids_not_pending" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_mixed_types_for_message_approval() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(contains_mixed_suggestion_types=True)
    )

    assert result.allowed is False
    assert "mixed_types_not_allowed" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_mixed_types_for_task_creation() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(
            action_type="create_tasks",
            approval_token=REVIEW_BATCH_CREATE_TASKS_TOKEN,
            contains_mixed_suggestion_types=True,
        )
    )

    assert result.allowed is False
    assert "mixed_types_not_allowed" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_already_processed_suggestions() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(contains_already_processed_suggestions=True)
    )

    assert result.allowed is False
    assert "already_processed" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_wrong_token() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(approval_token="BATCH ABLEHNEN")
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_common_approval_words() -> None:
    for token in ("", "ja", "JA", "ok", "SPEICHERN", "KONTAKT LÖSCHEN", "a", "r", "s"):
        result = check_review_batch_apply_allowed(
            **_allowed_kwargs(approval_token=token)
        )
        assert result.allowed is False
        assert "invalid_token" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_smoke_failure() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(scanner_smoke_passed=False)
    )

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_external_actions_enabled() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(external_actions_enabled=True)
    )

    assert result.allowed is False
    assert "external_actions_enabled" in result.blocked_reasons


def test_review_batch_apply_guard_blocks_forbidden_action_types() -> None:
    for action_type in ("send_messages", "create_calendar_events", "unknown"):
        result = check_review_batch_apply_allowed(
            **_allowed_kwargs(action_type=action_type)
        )
        assert result.allowed is False
        assert "invalid_action_type" in result.blocked_reasons
        assert result.required_token is None


def test_review_batch_apply_guard_deduplicates_selected_ids() -> None:
    result = check_review_batch_apply_allowed(
        **_allowed_kwargs(selected_ids=[2, 1, 2, 3, 1])
    )

    assert result.allowed is True
    assert result.selected_ids == (2, 1, 3)


def test_review_batch_apply_guard_has_safe_flags() -> None:
    result = check_review_batch_apply_allowed(**_allowed_kwargs())

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False


def test_review_batch_apply_guard_result_type_fields() -> None:
    result = check_review_batch_apply_allowed(**_allowed_kwargs())

    assert isinstance(result, ReviewBatchApplyGuardResult)
    assert result.action_type == "approve_messages"
    assert result.message is None
