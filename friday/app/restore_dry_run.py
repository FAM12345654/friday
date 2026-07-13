"""Local restore dry-run model.

This module validates a local Friday backup folder without restoring,
copying, overwriting, uploading, or mutating files.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal

from friday.app.backup_restore_path_safety import is_forbidden_backup_restore_path


RestoreDryRunSectionStatus = Literal["present", "missing", "blocked"]
RestoreDryRunBlockReason = Literal[
    "backup_missing",
    "target_outside_backups",
    "manifest_missing",
    "manifest_invalid",
    "external_path_in_manifest",
    "forbidden_backup_content",
]

FORBIDDEN_BACKUP_PARTS: tuple[str, ...] = (
    ".env",
    ".env.local",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "secret",
    "secrets",
    "token",
    "tokens",
    "api_key",
    "api_keys",
    "credential",
    "credentials",
    "password",
    "passwords",
    "private_key",
    "private_keys",
    ".obsidian",
    "obsidian vault",
    "obsidian_vault",
    "obsidianvault",
)


@dataclass(frozen=True)
class RestoreDryRunSection:
    """One section checked during restore dry-run."""

    name: str
    status: RestoreDryRunSectionStatus
    path: str | None
    file_count: int
    message: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class RestoreDryRunResult:
    """Structured result of a local restore dry-run."""

    allowed: bool
    backup_root: str | None
    manifest_found: bool
    manifest_valid: bool
    sections_checked: tuple[RestoreDryRunSection, ...]
    missing_sections: tuple[str, ...]
    blocked_reasons: tuple[RestoreDryRunBlockReason, ...]
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


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return 1
    return sum(1 for candidate in path.rglob("*") if candidate.is_file())


def _section(name: str, path: Path, message: str) -> RestoreDryRunSection:
    status: RestoreDryRunSectionStatus = "present" if path.exists() else "missing"
    return RestoreDryRunSection(
        name=name,
        status=status,
        path=str(path) if path.exists() else None,
        file_count=_count_files(path),
        message=message,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _has_forbidden_backup_content(backup_root: Path) -> bool:
    if not backup_root.exists() or not backup_root.is_dir():
        return False

    for candidate in backup_root.rglob("*"):
        lowered_parts = tuple(part.lower() for part in candidate.relative_to(backup_root).parts)
        if any(part in FORBIDDEN_BACKUP_PARTS for part in lowered_parts):
            return True
        if is_forbidden_backup_restore_path(candidate, root=backup_root):
            return True
    return False


def _manifest_has_external_path(
    manifest: dict[str, object],
    project_root: Path,
) -> bool:
    planned_root = manifest.get("planned_backup_root")
    if not isinstance(planned_root, str) or not planned_root:
        return False

    planned_path = Path(planned_root)
    if not planned_path.is_absolute():
        # Recognize foreign-OS absolute paths (e.g. "C:/..." checked on POSIX,
        # or "/..." checked on Windows) and treat them as external: they can
        # never live under the allowed backup parent on this OS.
        if PureWindowsPath(planned_root).is_absolute() or PurePosixPath(planned_root).is_absolute():
            return True
        return False

    allowed_backup_parent = project_root / "local_data" / "backups"
    return not _is_relative_to(planned_path, allowed_backup_parent)


def _included_sections_from_manifest(manifest: dict[str, object]) -> tuple[str, ...]:
    sections = manifest.get("included_sections", ())
    if not isinstance(sections, (list, tuple)):
        return ()
    return tuple(str(section) for section in sections)


def build_restore_dry_run(
    backup_root: str | Path,
    project_root: str | Path,
) -> RestoreDryRunResult:
    """Validate a local backup folder without restoring anything."""
    root = Path(project_root)
    backup = Path(backup_root)
    allowed_backup_parent = root / "local_data" / "backups"

    blocked_reasons: list[RestoreDryRunBlockReason] = []
    warnings: list[str] = []
    sections_checked: list[RestoreDryRunSection] = []
    missing_sections: list[str] = []
    manifest: dict[str, object] = {}
    manifest_found = False
    manifest_valid = False

    if not _is_relative_to(backup, allowed_backup_parent):
        blocked_reasons.append("target_outside_backups")
        return RestoreDryRunResult(
            allowed=False,
            backup_root=str(backup),
            manifest_found=False,
            manifest_valid=False,
            sections_checked=(),
            missing_sections=(),
            blocked_reasons=tuple(blocked_reasons),
            warnings=(),
            message="Restore Dry-Run wurde blockiert.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    if not backup.exists() or not backup.is_dir():
        blocked_reasons.append("backup_missing")
        return RestoreDryRunResult(
            allowed=False,
            backup_root=str(backup),
            manifest_found=False,
            manifest_valid=False,
            sections_checked=(),
            missing_sections=(),
            blocked_reasons=tuple(blocked_reasons),
            warnings=(),
            message="Backup-Ordner wurde nicht gefunden.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    manifest_path = backup / "manifest.json"
    manifest_found = manifest_path.exists() and manifest_path.is_file()
    sections_checked.append(
        _section("manifest", manifest_path, "Manifest fuer Restore Dry-Run.")
    )

    if not manifest_found:
        blocked_reasons.append("manifest_missing")
    else:
        try:
            loaded_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded_manifest, dict):
                manifest = loaded_manifest
                manifest_valid = True
            else:
                blocked_reasons.append("manifest_invalid")
        except (OSError, json.JSONDecodeError):
            blocked_reasons.append("manifest_invalid")

    if manifest_valid and _manifest_has_external_path(manifest, root):
        blocked_reasons.append("external_path_in_manifest")

    if _has_forbidden_backup_content(backup):
        blocked_reasons.append("forbidden_backup_content")

    sections_checked.append(
        _section("readme", backup / "README_BACKUP.md", "Backup-Hinweisdatei.")
    )

    included_sections = _included_sections_from_manifest(manifest)
    planned_section_paths = {
        "database": backup / "database",
        "exports": backup / "exports",
        "safety_docs": backup / "safety",
    }

    for section_name, section_path in planned_section_paths.items():
        if section_name not in included_sections:
            continue
        checked = _section(section_name, section_path, f"Backup-Sektion {section_name}.")
        sections_checked.append(checked)
        if checked.status == "missing":
            missing_sections.append(section_name)
            warnings.append(f"Backup-Sektion fehlt: {section_name}")

    if any(section.name == "readme" and section.status == "missing" for section in sections_checked):
        warnings.append("README_BACKUP.md fehlt.")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return RestoreDryRunResult(
        allowed=allowed,
        backup_root=str(backup),
        manifest_found=manifest_found,
        manifest_valid=manifest_valid,
        sections_checked=tuple(sections_checked),
        missing_sections=tuple(missing_sections),
        blocked_reasons=unique_blocked_reasons,
        warnings=tuple(warnings),
        message=(
            "Restore Dry-Run ist bereit. Es wurde nichts zurueckgeschrieben."
            if allowed
            else "Restore Dry-Run wurde blockiert."
        ),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
