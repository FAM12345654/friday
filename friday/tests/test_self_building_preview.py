"""Tests for preview-only self-building orchestration models."""

from __future__ import annotations

from friday.app.self_building_preview import (
    ALLOWED_TEST_RUNNER_COMMANDS,
    READ_ONLY_GIT_VIEW_COMMANDS,
    SELF_BUILDING_COMMIT_APPROVAL_TOKEN,
    BuildQueueItem,
    build_build_queue_preview,
    build_commit_draft,
    build_git_status_viewer_preview,
    build_self_building_finalization_gate,
    build_test_runner_preview,
    preview_commit_approval,
)


def test_build_queue_preview_classifies_allowed_and_blocked_commands() -> None:
    preview = build_build_queue_preview(
        (
            BuildQueueItem(
                title="Local validation",
                scope="tests",
                requested_commands=(
                    "python -m pytest friday/tests",
                    "python -m pip install unsafe",
                ),
            ),
        )
    )

    assert preview.allowed_commands == ("python -m pytest friday/tests",)
    assert preview.blocked_commands == ("python -m pip install unsafe",)
    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False


def test_build_queue_preview_preserves_order_and_empty_state() -> None:
    items = (
        BuildQueueItem("A", "tests", ("python -m pytest friday/tests",)),
        BuildQueueItem("B", "unsafe", ("git push",)),
    )

    preview = build_build_queue_preview(items)
    empty = build_build_queue_preview(())

    assert preview.items == items
    assert preview.allowed_commands == ("python -m pytest friday/tests",)
    assert preview.blocked_commands == ("git push",)
    assert empty.items == ()
    assert empty.allowed_commands == ()
    assert empty.blocked_commands == ()


def test_test_runner_preview_allowlist_does_not_execute() -> None:
    preview = build_test_runner_preview(" python scripts/friday_safety_smoke.py ")

    assert preview.command == "python scripts/friday_safety_smoke.py"
    assert preview.allowed is True
    assert preview.reason == "allowlisted"
    assert preview.would_execute is True
    assert preview.executed is False
    assert preview.preview_only is True
    assert preview.external_lookup_used is False


def test_test_runner_preview_blocks_unknown_command() -> None:
    preview = build_test_runner_preview("git push")

    assert preview.allowed is False
    assert preview.reason == "not_allowlisted"
    assert preview.would_execute is False
    assert preview.executed is False


def test_test_runner_preview_blocks_network_publish_and_git_mutation_commands() -> None:
    blocked_commands = (
        "curl https://example.test",
        "Invoke-WebRequest https://example.test",
        "npx eas-cli update",
        "git commit -m test",
        "git push",
        "git pull",
        "git status --short",
        "git add friday/app/self_building_preview.py",
        "python -m pytest friday/tests && git push",
        "python -m pytest friday/tests; git push",
        "",
    )

    for command in blocked_commands:
        preview = build_test_runner_preview(command)

        assert preview.allowed is False
        assert preview.would_execute is False
        assert preview.executed is False


def test_git_status_viewer_preview_is_read_only() -> None:
    preview = build_git_status_viewer_preview()

    assert "git status --short" in preview.allowed_commands
    assert "git diff --check" in preview.allowed_commands
    assert "git commit" not in preview.allowed_commands
    assert "git push" not in preview.allowed_commands
    assert "git reset --hard" not in preview.allowed_commands
    assert preview.read_only is True
    assert preview.executed is False
    assert preview.preview_only is True
    assert preview.external_lookup_used is False


def test_commit_draft_never_commits() -> None:
    draft = build_commit_draft(
        summary="Self-building preview",
        changed_files=("friday/app/self_building_preview.py", ""),
    )

    assert draft.summary == "Self-building preview"
    assert draft.changed_files == ("friday/app/self_building_preview.py",)
    assert "Changed files:" in draft.message
    assert draft.approval_token_required == SELF_BUILDING_COMMIT_APPROVAL_TOKEN
    assert draft.would_commit is False
    assert draft.committed is False
    assert draft.preview_only is True
    assert draft.external_lookup_used is False


def test_commit_approval_requires_hard_token_without_committing() -> None:
    wrong = preview_commit_approval("JA")
    valid = preview_commit_approval(SELF_BUILDING_COMMIT_APPROVAL_TOKEN)

    assert wrong.approval_valid is False
    assert valid.approval_valid is True
    assert valid.would_commit is False
    assert valid.committed is False
    assert valid.preview_only is True
    assert valid.external_lookup_used is False


def test_commit_draft_defaults_and_hard_token_are_exact() -> None:
    draft = build_commit_draft(" ", (" a.py ", "b.py"))

    assert draft.summary == "Local Friday update"
    assert draft.changed_files == ("a.py", "b.py")
    assert "- a.py" in draft.message
    assert "- b.py" in draft.message

    for token in ("", "JA", "ok", "COMMIT ERSTELLEN ", "commit erstellen"):
        assert preview_commit_approval(token).approval_valid is False

    assert preview_commit_approval(SELF_BUILDING_COMMIT_APPROVAL_TOKEN).committed is False


def test_self_building_finalization_gate_is_preview_only() -> None:
    gate = build_self_building_finalization_gate()

    assert gate.status == "finalized_preview_ready_execution_disabled"
    assert gate.allowed_test_commands == ALLOWED_TEST_RUNNER_COMMANDS
    assert gate.read_only_git_commands == READ_ONLY_GIT_VIEW_COMMANDS
    assert gate.commit_approval_token_required == SELF_BUILDING_COMMIT_APPROVAL_TOKEN
    assert "no_runner_execution" in gate.completed_checks
    assert "no_git_mutation" in gate.completed_checks
    assert "git_commit" in gate.blocked_actions
    assert "git_add" in gate.blocked_actions
    assert "git_push" in gate.blocked_actions
    assert "git_pull" in gate.blocked_actions
    assert "branch_switch" in gate.blocked_actions
    assert "git_reset" in gate.blocked_actions
    assert "git_revert" in gate.blocked_actions
    assert "pull_request_creation" in gate.blocked_actions
    assert "arbitrary_shell_command" in gate.blocked_actions
    assert gate.preview_only is True
    assert gate.persisted is False
    assert gate.external_lookup_used is False
