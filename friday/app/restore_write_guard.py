"""Local restore write guard.

This module checks whether a future restore write would be allowed.
It does not restore, copy, overwrite, delete, upload, or mutate files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from friday.app.restore_dry_run import RestoreDryRunResult


RESTORE_WRITE_APPROVAL_TOKEN = "RESTORE AUSFUEHREN"

RestoreWriteBlockReason = Literal[
    "missing_dry_run",
    "dry_run_not_allowed",
    "invalid_token",
    "backup_outside_backups",
    "target_outside_project",
    "active_database_conflict",
    "missing_manifest",
    "forbidden_backup_content",
]


@dataclass(frozen=True)
class RestoreWriteGuardResult:
    """Structured guard result for a future restore write."""

    allowed: bool
    backup_root: str | None
    target_root: str
    blocked_reasons: tuple[RestoreWriteBlockReason, ...]
    warnings: tuple[str, ...]
    message: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def check_restore_write_allowed(
    dry_run: RestoreDryRunResult | None,
    approval_token: str | None,
    project_root: str | Path,
) -> RestoreWriteGuardResult:
    """Check whether a future restore write would be allowed."""
    root = Path(project_root)
    allowed_backup_parent = root / "local_data" / "backups"
    blocked_reasons: list[RestoreWriteBlockReason] = []
    warnings: list[str] = []
    backup_root: str | None = None

    if dry_run is None:
        blocked_reasons.append("missing_dry_run")
    else:
        backup_root = dry_run.backup_root
        warnings.extend(dry_run.warnings)

        if not dry_run.allowed:
            blocked_reasons.append("dry_run_not_allowed")

        if not dry_run.manifest_found or not dry_run.manifest_valid:
            blocked_reasons.append("missing_manifest")

        if "forbidden_backup_content" in dry_run.blocked_reasons:
            blocked_reasons.append("forbidden_backup_content")

        if dry_run.backup_root is None or not _is_relative_to(
            Path(dry_run.backup_root),
            allowed_backup_parent,
        ):
            blocked_reasons.append("backup_outside_backups")

    if not _is_relative_to(root, root):
        blocked_reasons.append("target_outside_project")

    active_db_candidates = (
        root / "local_data" / "friday.sqlite",
        root / "local_data" / "friday.db",
        root / "friday.sqlite",
        root / "friday.db",
    )
    if any(path.exists() for path in active_db_candidates):
        blocked_reasons.append("active_database_conflict")

    if (approval_token or "").strip() != RESTORE_WRITE_APPROVAL_TOKEN:
        blocked_reasons.append("invalid_token")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return RestoreWriteGuardResult(
        allowed=allowed,
        backup_root=backup_root,
        target_root=str(root),
        blocked_reasons=unique_blocked_reasons,
        warnings=tuple(warnings),
        message=(
            "Restore Write waere erlaubt. Es wurde nichts zurueckgeschrieben."
            if allowed
            else "Restore Write wurde nicht freigegeben."
        ),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
