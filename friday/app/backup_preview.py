"""Local backup preview model.

This module builds a preview of what a future backup would include.
It does not copy, write, zip, upload, or restore files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


BackupSectionStatus = Literal["included", "excluded", "missing", "planned"]


@dataclass(frozen=True)
class BackupPreviewSection:
    """One planned backup section in preview mode."""

    name: str
    status: BackupSectionStatus
    path: str | None
    reason: str
    file_count: int
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class BackupPreview:
    """Structured preview of a future local Friday backup."""

    project_root: str
    planned_backup_root: str
    sections: tuple[BackupPreviewSection, ...]
    manifest_preview: dict[str, object]
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return 1
    return sum(1 for candidate in path.rglob("*") if candidate.is_file())


def _section(
    name: str,
    status: BackupSectionStatus,
    path: Path | None,
    reason: str,
) -> BackupPreviewSection:
    return BackupPreviewSection(
        name=name,
        status=status,
        path=str(path) if path is not None else None,
        reason=reason,
        file_count=_count_files(path) if path is not None else 0,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def build_backup_preview(
    project_root: str | Path,
    timestamp: str = "YYYYMMDD_HHMMSS",
) -> BackupPreview:
    """Build a local backup preview without writing files."""
    root = Path(project_root)
    local_data = root / "local_data"
    planned_backup_root = local_data / "backups" / f"friday_backup_{timestamp}"

    database_candidates = (
        local_data / "friday.sqlite",
        local_data / "friday.db",
        root / "friday.sqlite",
        root / "friday.db",
    )
    database_path = next((path for path in database_candidates if path.exists()), None)

    exports_path = local_data / "exports"
    docs_path = root / "friday" / "docs"

    safety_docs = (
        docs_path / "SAFETY_MATRIX.md",
        docs_path / "TEST_MATRIX.md",
        docs_path / "FRIDAY_ARCHITECTURE.md",
    )
    existing_safety_docs = tuple(path for path in safety_docs if path.exists())

    sections = (
        _section(
            name="database",
            status="included" if database_path else "missing",
            path=database_path,
            reason=(
                "Local SQLite database candidate."
                if database_path
                else "No local SQLite database found."
            ),
        ),
        _section(
            name="exports",
            status="included" if exports_path.exists() else "missing",
            path=exports_path,
            reason=(
                "Local exports directory."
                if exports_path.exists()
                else "No local exports directory found."
            ),
        ),
        BackupPreviewSection(
            name="safety_docs",
            status="included" if existing_safety_docs else "missing",
            path=str(docs_path) if existing_safety_docs else None,
            reason=(
                "Safety documentation snapshot."
                if existing_safety_docs
                else "Safety docs not found."
            ),
            file_count=len(existing_safety_docs),
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        ),
        _section(
            name="obsidian_vault",
            status="excluded",
            path=None,
            reason="Obsidian Vault is not backed up automatically; separate gate required.",
        ),
        _section(
            name="secrets",
            status="excluded",
            path=None,
            reason=".env, API keys and secrets are excluded.",
        ),
        _section(
            name="venv_cache",
            status="excluded",
            path=None,
            reason=".venv, venv, __pycache__ and caches are excluded.",
        ),
    )

    manifest_preview: dict[str, object] = {
        "friday_backup_version": 1,
        "backup_created_at": timestamp,
        "planned_backup_root": str(planned_backup_root),
        "included_sections": tuple(
            section.name for section in sections if section.status == "included"
        ),
        "excluded_sections": tuple(
            section.name for section in sections if section.status == "excluded"
        ),
        "preview_only": True,
        "external_lookup_used": False,
    }

    return BackupPreview(
        project_root=str(root),
        planned_backup_root=str(planned_backup_root),
        sections=sections,
        manifest_preview=manifest_preview,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
