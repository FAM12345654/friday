"""Guarded local privacy cleanup writer prototype.

This module performs only tightly scoped local filesystem cleanup when called
explicitly with an allowed privacy cleanup guard result. It is not connected to
the CLI and does not touch SQLite data.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Literal

from friday.app.privacy_cleanup_write_guard import (
    PrivacyCleanupWriteBlockReason,
    PrivacyCleanupWriteGuardResult,
)


PrivacyCleanupWriterStatus = Literal[
    "deleted",
    "dry_run",
    "blocked",
    "not_found",
]

PrivacyCleanupWriterBlockReason = PrivacyCleanupWriteBlockReason | Literal[
    "missing_guard",
    "guard_blocked",
    "guard_write_marker_invalid",
    "guard_external_action_used",
    "cleanup_area_mismatch",
    "target_path_mismatch",
    "unsupported_cleanup_area",
    "missing_target_path",
    "target_not_found",
    "target_is_symlink",
    "symlink_present",
    "latest_backup_protected",
    "backup_required",
    "rollback_required",
]

FILE_CLEANUP_AREAS = ("exports", "backups", "restore_work")
DB_CLEANUP_AREAS = ("review_history", "contact_context")


@dataclass(frozen=True)
class PrivacyCleanupWriterResult:
    """Structured result for a guarded privacy cleanup writer attempt."""

    performed: bool
    status: PrivacyCleanupWriterStatus
    cleanup_area: str
    target_path: str | None
    planned_count: int
    deleted_count: int
    skipped_count: int
    dry_run: bool
    backup_used: bool
    rollback_available: bool
    blocked_reasons: tuple[PrivacyCleanupWriterBlockReason, ...]
    message: str
    preview_only: bool
    persisted: bool
    external_action_used: bool
    write_performed: bool


def _same_path(left: str | Path | None, right: str | Path | None) -> bool:
    if left is None or right is None:
        return left is right
    return Path(left).resolve() == Path(right).resolve()


def _planned_entries(target: Path) -> tuple[Path, ...]:
    if target.is_file():
        return (target,)
    if not target.is_dir():
        return ()
    children = tuple(sorted(target.rglob("*"), key=lambda item: len(item.parts), reverse=True))
    return children + (target,)


def _has_symlink(entries: tuple[Path, ...]) -> bool:
    return any(entry.is_symlink() for entry in entries)


def _delete_target(target: Path) -> int:
    if target.is_file():
        target.unlink()
        return 1

    entries = _planned_entries(target)
    shutil.rmtree(target)
    return len(entries)


def apply_privacy_cleanup(
    *,
    guard_result: PrivacyCleanupWriteGuardResult | None,
    cleanup_area: str,
    target_path: str | Path | None,
    dry_run: bool = True,
    backup_ready: bool = False,
    rollback_available: bool = False,
    latest_backup_path: str | Path | None = None,
) -> PrivacyCleanupWriterResult:
    """Apply a guarded local privacy cleanup for supported file areas only."""

    blocked_reasons: list[PrivacyCleanupWriterBlockReason] = []
    normalized_target = Path(target_path) if target_path is not None else None
    planned_count = 0

    if guard_result is None:
        blocked_reasons.append("missing_guard")
    else:
        if not guard_result.allowed:
            blocked_reasons.append("guard_blocked")
            blocked_reasons.extend(guard_result.blocked_reasons)

        if guard_result.write_performed:
            blocked_reasons.append("guard_write_marker_invalid")

        if guard_result.external_action_used:
            blocked_reasons.append("guard_external_action_used")

        if guard_result.cleanup_area != cleanup_area:
            blocked_reasons.append("cleanup_area_mismatch")

        if not _same_path(guard_result.target_path, target_path):
            blocked_reasons.append("target_path_mismatch")

    if cleanup_area in DB_CLEANUP_AREAS:
        blocked_reasons.append("unsupported_cleanup_area")
        if not backup_ready:
            blocked_reasons.append("backup_required")
        if not rollback_available:
            blocked_reasons.append("rollback_required")

    if cleanup_area not in FILE_CLEANUP_AREAS and cleanup_area not in DB_CLEANUP_AREAS:
        blocked_reasons.append("unsupported_cleanup_area")

    if cleanup_area in FILE_CLEANUP_AREAS and normalized_target is None:
        blocked_reasons.append("missing_target_path")

    if cleanup_area == "backups" and latest_backup_path is not None and _same_path(
        normalized_target,
        latest_backup_path,
    ):
        blocked_reasons.append("latest_backup_protected")

    if normalized_target is not None:
        if not normalized_target.exists():
            blocked_reasons.append("target_not_found")
        elif normalized_target.is_symlink():
            blocked_reasons.append("target_is_symlink")
        else:
            entries = _planned_entries(normalized_target)
            planned_count = len(entries)
            if _has_symlink(entries):
                blocked_reasons.append("symlink_present")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    if unique_blocked_reasons:
        status: PrivacyCleanupWriterStatus = (
            "not_found" if unique_blocked_reasons == ("target_not_found",) else "blocked"
        )
        return PrivacyCleanupWriterResult(
            performed=False,
            status=status,
            cleanup_area=cleanup_area,
            target_path=str(normalized_target) if normalized_target is not None else None,
            planned_count=planned_count,
            deleted_count=0,
            skipped_count=planned_count,
            dry_run=dry_run,
            backup_used=False,
            rollback_available=rollback_available,
            blocked_reasons=unique_blocked_reasons,
            message="Privacy Cleanup wurde nicht ausgefuehrt.",
            preview_only=False,
            persisted=False,
            external_action_used=False,
            write_performed=False,
        )

    if dry_run or normalized_target is None:
        return PrivacyCleanupWriterResult(
            performed=False,
            status="dry_run",
            cleanup_area=cleanup_area,
            target_path=str(normalized_target) if normalized_target is not None else None,
            planned_count=planned_count,
            deleted_count=0,
            skipped_count=planned_count,
            dry_run=True,
            backup_used=backup_ready,
            rollback_available=rollback_available,
            blocked_reasons=(),
            message="Privacy Cleanup Dry-Run wurde erstellt. Es wurde nichts geloescht.",
            preview_only=False,
            persisted=False,
            external_action_used=False,
            write_performed=False,
        )

    deleted_count = _delete_target(normalized_target)
    return PrivacyCleanupWriterResult(
        performed=True,
        status="deleted",
        cleanup_area=cleanup_area,
        target_path=str(normalized_target),
        planned_count=planned_count,
        deleted_count=deleted_count,
        skipped_count=0,
        dry_run=False,
        backup_used=backup_ready,
        rollback_available=rollback_available,
        blocked_reasons=(),
        message="Privacy Cleanup wurde lokal ausgefuehrt.",
        preview_only=False,
        persisted=True,
        external_action_used=False,
        write_performed=True,
    )
