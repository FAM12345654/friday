"""Preview-only self-building orchestration models for Friday."""

from __future__ import annotations

from dataclasses import dataclass


SELF_BUILDING_COMMIT_APPROVAL_TOKEN = "COMMIT ERSTELLEN"

ALLOWED_TEST_RUNNER_COMMANDS: tuple[str, ...] = (
    "python -m pytest friday/tests",
    "python -m compileall friday",
    "python scripts/friday_safety_smoke.py",
    "git diff --check",
)

READ_ONLY_GIT_VIEW_COMMANDS: tuple[str, ...] = (
    "git status --short",
    "git diff --stat",
    "git diff --check",
)


@dataclass(frozen=True)
class BuildQueueItem:
    """One proposed local build step."""

    title: str
    scope: str
    requested_commands: tuple[str, ...]
    status: str = "planned"


@dataclass(frozen=True)
class BuildQueuePreview:
    """Read-only build queue preview."""

    items: tuple[BuildQueueItem, ...]
    allowed_commands: tuple[str, ...]
    blocked_commands: tuple[str, ...]
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class TestRunnerPreview:
    """Preview of whether a local test command is allowlisted."""

    command: str
    allowed: bool
    reason: str
    would_execute: bool
    executed: bool
    preview_only: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class GitStatusViewerPreview:
    """Read-only git status viewer plan without invoking git."""

    allowed_commands: tuple[str, ...]
    read_only: bool
    executed: bool
    preview_only: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class CommitDraft:
    """Commit message draft that never creates a commit."""

    summary: str
    changed_files: tuple[str, ...]
    message: str
    approval_token_required: str
    would_commit: bool
    committed: bool
    preview_only: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class CommitApprovalPreview:
    """Preview of commit approval token validation without committing."""

    approval_valid: bool
    approval_token_required: str
    would_commit: bool
    committed: bool
    preview_only: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class SelfBuildingFinalizationGate:
    """Read-only release gate summary for self-building orchestration."""

    status: str
    allowed_test_commands: tuple[str, ...]
    read_only_git_commands: tuple[str, ...]
    commit_approval_token_required: str
    completed_checks: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    deferred_items: tuple[str, ...]
    preview_only: bool = True
    persisted: bool = False
    external_lookup_used: bool = False


def build_build_queue_preview(items: tuple[BuildQueueItem, ...]) -> BuildQueuePreview:
    """Build a queue preview and classify requested commands."""

    requested = tuple(command for item in items for command in item.requested_commands)
    allowed = tuple(
        command for command in requested if command in ALLOWED_TEST_RUNNER_COMMANDS
    )
    blocked = tuple(
        command for command in requested if command not in ALLOWED_TEST_RUNNER_COMMANDS
    )

    return BuildQueuePreview(
        items=items,
        allowed_commands=allowed,
        blocked_commands=blocked,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def build_test_runner_preview(command: str) -> TestRunnerPreview:
    """Preview whether a command is allowlisted without executing it."""

    normalized = (command or "").strip()
    allowed = normalized in ALLOWED_TEST_RUNNER_COMMANDS
    reason = "allowlisted" if allowed else "not_allowlisted"

    return TestRunnerPreview(
        command=normalized,
        allowed=allowed,
        reason=reason,
        would_execute=allowed,
        executed=False,
        preview_only=True,
        external_lookup_used=False,
    )


def build_git_status_viewer_preview() -> GitStatusViewerPreview:
    """Return the read-only git viewer plan without invoking git."""

    return GitStatusViewerPreview(
        allowed_commands=READ_ONLY_GIT_VIEW_COMMANDS,
        read_only=True,
        executed=False,
        preview_only=True,
        external_lookup_used=False,
    )


def build_commit_draft(summary: str, changed_files: tuple[str, ...]) -> CommitDraft:
    """Build a local commit message draft without staging or committing."""

    clean_summary = (summary or "").strip() or "Local Friday update"
    clean_files = tuple(file_path.strip() for file_path in changed_files if file_path.strip())
    if clean_files:
        body = "\n".join(f"- {file_path}" for file_path in clean_files)
        message = f"{clean_summary}\n\nChanged files:\n{body}"
    else:
        message = clean_summary

    return CommitDraft(
        summary=clean_summary,
        changed_files=clean_files,
        message=message,
        approval_token_required=SELF_BUILDING_COMMIT_APPROVAL_TOKEN,
        would_commit=False,
        committed=False,
        preview_only=True,
        external_lookup_used=False,
    )


def preview_commit_approval(confirmation: str) -> CommitApprovalPreview:
    """Validate the hard commit token without creating a commit."""

    approval_valid = confirmation == SELF_BUILDING_COMMIT_APPROVAL_TOKEN
    return CommitApprovalPreview(
        approval_valid=approval_valid,
        approval_token_required=SELF_BUILDING_COMMIT_APPROVAL_TOKEN,
        would_commit=False,
        committed=False,
        preview_only=True,
        external_lookup_used=False,
    )


def build_self_building_finalization_gate() -> SelfBuildingFinalizationGate:
    """Return the local-only self-building release gate status."""

    return SelfBuildingFinalizationGate(
        status="finalized_preview_ready_execution_disabled",
        allowed_test_commands=ALLOWED_TEST_RUNNER_COMMANDS,
        read_only_git_commands=READ_ONLY_GIT_VIEW_COMMANDS,
        commit_approval_token_required=SELF_BUILDING_COMMIT_APPROVAL_TOKEN,
        completed_checks=(
            "build_queue_preview_available",
            "test_runner_allowlist_available",
            "git_status_viewer_read_only",
            "commit_draft_preview_available",
            "hard_commit_token_documented",
            "no_runner_execution",
            "no_git_mutation",
        ),
        blocked_actions=(
            "arbitrary_shell_command",
            "test_runner_without_allowlist",
            "git_add",
            "git_commit",
            "git_push",
            "git_pull",
            "branch_switch",
            "git_reset",
            "git_revert",
            "pull_request_creation",
            "commit_without_hard_token",
            "network_action",
        ),
        deferred_items=(
            "test_runner_execution_gate",
            "git_status_runtime_adapter",
            "commit_execution_gate",
            "build_history_writer",
        ),
    )
