"""Local restore writer.

This module performs a guarded local restore copy only into a separate
restore folder. It never overwrites the active Friday database and never
restores files in-place.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
from typing import Literal

from friday.app.restore_dry_run import RestoreDryRunResult
from friday.app.restore_write_guard import (
    RestoreWriteBlockReason,
    check_restore_write_allowed,
)
from friday.app.backup_restore_path_safety import is_forbidden_backup_restore_path


RestoreWriteImplementationBlockReason = RestoreWriteBlockReason | Literal[
    "target_exists",
]

RESTORE_README_TEXT = """# Friday Local Restore Copy

Dieses Restore-Ergebnis wurde lokal von Friday erstellt.

- Keine aktive Datenbank wurde ersetzt
- Keine Dateien wurden in das Projekt zurueckkopiert
- Keine externen Speicherziele
- Keine Cloud
- Keine Secrets
- Kein Obsidian-Vault-Restore
"""


@dataclass(frozen=True)
class RestoreWrittenFile:
    """One file written into a local restore folder."""

    relative_path: str
    source_path: str | None
    bytes_written: int


@dataclass(frozen=True)
class RestoreWriteResult:
    """Result of a guarded local restore copy attempt."""

    allowed: bool
    persisted: bool
    target_root: str | None
    written_files: tuple[RestoreWrittenFile, ...]
    blocked_reasons: tuple[RestoreWriteImplementationBlockReason, ...]
    warnings: tuple[str, ...]
    message: str
    preview_only: bool
    external_lookup_used: bool


def _write_text_file(target_root: Path, relative_path: str, text: str) -> RestoreWrittenFile:
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return RestoreWrittenFile(
        relative_path=relative_path,
        source_path=None,
        bytes_written=target.stat().st_size,
    )


def _copy_file(target_root: Path, source: Path, relative_path: str) -> RestoreWrittenFile:
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return RestoreWrittenFile(
        relative_path=relative_path,
        source_path=str(source),
        bytes_written=target.stat().st_size,
    )


def _copy_directory(
    target_root: Path,
    source_dir: Path,
    target_subdir: str,
    allowed_root: Path | None = None,
) -> tuple[RestoreWrittenFile, ...]:
    if (
        not source_dir.exists()
        or not source_dir.is_dir()
        or is_forbidden_backup_restore_path(
            source_dir,
            root=allowed_root or source_dir.parent,
        )
    ):
        return ()

    written: list[RestoreWrittenFile] = []
    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        if is_forbidden_backup_restore_path(source, root=source_dir):
            continue
        relative_source = source.relative_to(source_dir)
        relative_target = Path(target_subdir) / relative_source
        written.append(_copy_file(target_root, source, relative_target.as_posix()))
    return tuple(written)


def _write_restore_manifest(
    target_root: Path,
    dry_run: RestoreDryRunResult,
) -> RestoreWrittenFile:
    manifest = {
        "friday_restore_version": 1,
        "backup_root": dry_run.backup_root,
        "sections_checked": tuple(section.name for section in dry_run.sections_checked),
        "missing_sections": dry_run.missing_sections,
        "warnings": dry_run.warnings,
        "active_database_replaced": False,
        "preview_only": False,
        "persisted": True,
        "external_lookup_used": False,
    }
    text = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)
    return _write_text_file(target_root, "RESTORE_MANIFEST.json", text + "\n")


def _restore_target_root(project_root: Path, timestamp: str) -> Path:
    return project_root / "local_data" / "restores" / f"friday_restore_{timestamp}"


def write_local_restore_copy(
    dry_run: RestoreDryRunResult | None,
    approval_token: str | None,
    project_root: str | Path,
    timestamp: str = "YYYYMMDD_HHMMSS",
) -> RestoreWriteResult:
    """Copy allowed backup sections into a separate restore folder."""
    root = Path(project_root)
    guard = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=approval_token,
        project_root=root,
    )
    target_root = _restore_target_root(root, timestamp)

    if not guard.allowed or dry_run is None:
        return RestoreWriteResult(
            allowed=False,
            persisted=False,
            target_root=str(target_root),
            written_files=(),
            blocked_reasons=guard.blocked_reasons,
            warnings=guard.warnings,
            message=guard.message,
            preview_only=True,
            external_lookup_used=False,
        )

    if target_root.exists():
        return RestoreWriteResult(
            allowed=False,
            persisted=False,
            target_root=str(target_root),
            written_files=(),
            blocked_reasons=("target_exists",),
            warnings=guard.warnings,
            message="Restore wurde nicht erstellt, weil der Zielordner bereits existiert.",
            preview_only=True,
            external_lookup_used=False,
        )

    target_root.mkdir(parents=True, exist_ok=False)
    written: list[RestoreWrittenFile] = [
        _write_restore_manifest(target_root, dry_run),
        _write_text_file(target_root, "README_RESTORE.md", RESTORE_README_TEXT),
    ]

    section_target_names = {
        "database": "database",
        "exports": "exports",
        "safety_docs": "safety",
    }
    backup_root_path = Path(dry_run.backup_root) if dry_run.backup_root else None
    for section in dry_run.sections_checked:
        target_subdir = section_target_names.get(section.name)
        if not target_subdir or section.status != "present" or section.path is None:
            continue
        source_path = Path(section.path)
        allowed_root = backup_root_path or source_path.parent
        if is_forbidden_backup_restore_path(source_path, root=allowed_root):
            continue
        if source_path.is_dir():
            written.extend(
                _copy_directory(
                    target_root,
                    source_path,
                    target_subdir,
                    allowed_root=allowed_root,
                )
            )
        elif source_path.is_file():
            written.append(
                _copy_file(target_root, source_path, f"{target_subdir}/{source_path.name}")
            )

    return RestoreWriteResult(
        allowed=True,
        persisted=True,
        target_root=str(target_root),
        written_files=tuple(written),
        blocked_reasons=(),
        warnings=guard.warnings,
        message="Restore wurde lokal in einen separaten Ordner kopiert.",
        preview_only=False,
        external_lookup_used=False,
    )
