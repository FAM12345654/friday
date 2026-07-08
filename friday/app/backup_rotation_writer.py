"""Guarded writer for local backup rotation cleanup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Literal

from friday.app.backup_rotation_guard import (
    BackupRotationBlockReason,
    BackupRotationGuardResult,
)


BackupRotationWriterBlockReason = BackupRotationBlockReason | Literal[
    "missing_guard",
    "guard_blocked",
    "guard_write_marker_invalid",
    "guard_external_action_used",
    "path_not_found",
    "path_is_symlink",
]


@dataclass(frozen=True)
class BackupRotationWriteResult:
    """Result of a guarded local backup rotation cleanup."""

    performed: bool
    deleted_paths: tuple[str, ...]
    protected_paths: tuple[str, ...]
    blocked_reasons: tuple[BackupRotationWriterBlockReason, ...]
    message: str
    preview_only: bool
    persisted: bool
    external_action_used: bool
    write_performed: bool


def apply_backup_rotation(
    guard_result: BackupRotationGuardResult | None,
) -> BackupRotationWriteResult:
    """Delete only guard-approved old local backup folders."""

    blocked_reasons: list[BackupRotationWriterBlockReason] = []

    if guard_result is None:
        blocked_reasons.append("missing_guard")
        delete_paths: tuple[str, ...] = ()
        protected_paths: tuple[str, ...] = ()
    else:
        delete_paths = guard_result.delete_paths
        protected_paths = guard_result.protected_paths

        if not guard_result.allowed:
            blocked_reasons.append("guard_blocked")
            blocked_reasons.extend(guard_result.blocked_reasons)

        if guard_result.write_performed:
            blocked_reasons.append("guard_write_marker_invalid")

        if guard_result.external_action_used:
            blocked_reasons.append("guard_external_action_used")

    for raw_path in delete_paths:
        path = Path(raw_path)
        if not path.exists():
            blocked_reasons.append("path_not_found")
        elif path.is_symlink():
            blocked_reasons.append("path_is_symlink")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    if unique_blocked_reasons:
        return BackupRotationWriteResult(
            performed=False,
            deleted_paths=(),
            protected_paths=protected_paths,
            blocked_reasons=unique_blocked_reasons,
            message="Backup-Rotation wurde nicht ausgefuehrt.",
            preview_only=False,
            persisted=False,
            external_action_used=False,
            write_performed=False,
        )

    deleted: list[str] = []
    for raw_path in delete_paths:
        path = Path(raw_path)
        shutil.rmtree(path)
        deleted.append(str(path))

    return BackupRotationWriteResult(
        performed=True,
        deleted_paths=tuple(deleted),
        protected_paths=protected_paths,
        blocked_reasons=(),
        message="Backup-Rotation wurde lokal ausgefuehrt.",
        preview_only=False,
        persisted=True,
        external_action_used=False,
        write_performed=True,
    )
