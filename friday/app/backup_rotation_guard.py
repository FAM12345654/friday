"""Guard for local backup rotation cleanup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from friday.app.backup_rotation_preview import BackupRotationPreview
from friday.app.privacy_cleanup_write_guard import PRIVACY_CLEANUP_TOKENS


BACKUP_ROTATION_APPROVAL_TOKEN = PRIVACY_CLEANUP_TOKENS["backups"]

BackupRotationBlockReason = Literal[
    "missing_preview",
    "invalid_token",
    "scanner_smoke_failed",
    "no_cleanup_candidates",
    "target_outside_backups",
    "protected_candidate_selected",
]


@dataclass(frozen=True)
class BackupRotationGuardResult:
    """Structured guard result for local backup rotation."""

    allowed: bool
    backups_root: str | None
    delete_paths: tuple[str, ...]
    protected_paths: tuple[str, ...]
    blocked_reasons: tuple[BackupRotationBlockReason, ...]
    message: str | None
    required_token: str
    scanner_smoke_required: bool
    preview_only: bool
    persisted: bool
    external_action_used: bool
    write_performed: bool


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def check_backup_rotation_allowed(
    *,
    preview: BackupRotationPreview | None,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    project_root: str | Path,
) -> BackupRotationGuardResult:
    """Check whether backup rotation cleanup is allowed."""

    blocked_reasons: list[BackupRotationBlockReason] = []
    delete_paths: tuple[str, ...] = ()
    protected_paths: tuple[str, ...] = ()
    backups_root: str | None = None
    allowed_backups_root = Path(project_root) / "local_data" / "backups"

    if preview is None:
        blocked_reasons.append("missing_preview")
    else:
        backups_root = preview.backups_root
        delete_paths = tuple(
            candidate.path
            for candidate in preview.candidates
            if candidate.selected_for_cleanup
        )
        protected_paths = tuple(
            candidate.path
            for candidate in preview.candidates
            if candidate.protected
        )

        if not delete_paths:
            blocked_reasons.append("no_cleanup_candidates")

        for path in delete_paths + protected_paths:
            if not _is_relative_to(Path(path), allowed_backups_root):
                blocked_reasons.append("target_outside_backups")
                break

        if any(
            candidate.selected_for_cleanup and candidate.protected
            for candidate in preview.candidates
        ):
            blocked_reasons.append("protected_candidate_selected")

    if approval_token != BACKUP_ROTATION_APPROVAL_TOKEN:
        blocked_reasons.append("invalid_token")

    if not scanner_smoke_passed:
        blocked_reasons.append("scanner_smoke_failed")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return BackupRotationGuardResult(
        allowed=allowed,
        backups_root=backups_root,
        delete_paths=delete_paths,
        protected_paths=protected_paths,
        blocked_reasons=unique_blocked_reasons,
        message=None if allowed else "Backup-Rotation wurde nicht freigegeben.",
        required_token=BACKUP_ROTATION_APPROVAL_TOKEN,
        scanner_smoke_required=True,
        preview_only=True,
        persisted=False,
        external_action_used=False,
        write_performed=False,
    )
