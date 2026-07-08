"""Local backup write guard.

This module checks whether a future local backup write would be allowed.
It does not copy, write, zip, upload, restore, or mutate files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from friday.app.backup_preview import BackupPreview, BackupPreviewSection


BACKUP_WRITE_APPROVAL_TOKEN = "BACKUP ERSTELLEN"

BackupWriteBlockReason = Literal[
    "missing_preview",
    "invalid_token",
    "target_outside_backups",
    "scanner_smoke_failed",
    "excluded_section_present",
]


@dataclass(frozen=True)
class BackupWriteGuardResult:
    """Structured guard result for a future local backup write."""

    allowed: bool
    planned_backup_root: str | None
    blocked_reasons: tuple[BackupWriteBlockReason, ...]
    message: str | None
    checked_sections: tuple[str, ...]
    excluded_sections: tuple[str, ...]
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _section_names_by_status(
    sections: tuple[BackupPreviewSection, ...],
    status: str,
) -> tuple[str, ...]:
    return tuple(section.name for section in sections if section.status == status)


def check_backup_write_allowed(
    preview: BackupPreview | None,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    project_root: str | Path,
) -> BackupWriteGuardResult:
    """Check whether a future backup write would be allowed."""
    blocked_reasons: list[BackupWriteBlockReason] = []
    checked_sections: tuple[str, ...] = ()
    excluded_sections: tuple[str, ...] = ()
    planned_backup_root: str | None = None

    root = Path(project_root)
    allowed_backup_parent = root / "local_data" / "backups"

    if preview is None:
        blocked_reasons.append("missing_preview")
    else:
        planned_backup_root = preview.planned_backup_root
        planned_path = Path(preview.planned_backup_root)
        checked_sections = tuple(section.name for section in preview.sections)
        excluded_sections = _section_names_by_status(preview.sections, "excluded")

        if not _is_relative_to(planned_path, allowed_backup_parent):
            blocked_reasons.append("target_outside_backups")

        dangerous_excluded_sections = {"secrets", "obsidian_vault", "venv_cache"}
        included_dangerous_sections = tuple(
            section.name
            for section in preview.sections
            if section.name in dangerous_excluded_sections and section.status != "excluded"
        )

        if included_dangerous_sections:
            blocked_reasons.append("excluded_section_present")

    if (approval_token or "").strip() != BACKUP_WRITE_APPROVAL_TOKEN:
        blocked_reasons.append("invalid_token")

    if not scanner_smoke_passed:
        blocked_reasons.append("scanner_smoke_failed")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return BackupWriteGuardResult(
        allowed=allowed,
        planned_backup_root=planned_backup_root,
        blocked_reasons=unique_blocked_reasons,
        message=None if allowed else "Backup wurde nicht freigegeben.",
        checked_sections=checked_sections,
        excluded_sections=excluded_sections,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
