"""Local backup writer.

This module performs a guarded local backup write only when explicitly called
with a valid preview, a passing smoke status, and the hard approval token.
It does not restore, zip, upload, or call external services.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
from typing import Literal

from friday.app.backup_preview import BackupPreview
from friday.app.backup_write_guard import (
    BACKUP_WRITE_APPROVAL_TOKEN,
    BackupWriteBlockReason,
    check_backup_write_allowed,
)
from friday.app.backup_restore_path_safety import is_forbidden_backup_restore_path


BackupWriteImplementationBlockReason = BackupWriteBlockReason | Literal["target_exists"]

BACKUP_README_TEXT = """# Friday Local Backup

Dieses Backup wurde lokal von Friday erstellt.

- Keine externen Speicherziele
- Keine Cloud
- Keine Secrets
- Kein Obsidian-Vault-Backup
- Kein Restore in diesem Schritt
"""

EXCLUDED_COPY_PARTS: tuple[str, ...] = (".venv", "venv", "__pycache__", ".pytest_cache")


@dataclass(frozen=True)
class BackupWrittenFile:
    """One file written into a local backup folder."""

    relative_path: str
    source_path: str | None
    bytes_written: int


@dataclass(frozen=True)
class BackupWriteResult:
    """Result of a guarded local backup write attempt."""

    allowed: bool
    persisted: bool
    target_path: str | None
    written_files: tuple[BackupWrittenFile, ...]
    blocked_reasons: tuple[BackupWriteImplementationBlockReason, ...]
    message: str
    preview_only: bool
    external_lookup_used: bool


def _relative_backup_path(target_root: Path, file_path: Path) -> str:
    return file_path.relative_to(target_root).as_posix()


def _is_excluded_copy_path(path: Path, source_dir: Path | None = None) -> bool:
    return any(part in EXCLUDED_COPY_PARTS for part in path.parts) or is_forbidden_backup_restore_path(
        path,
        root=source_dir,
    )


def _write_text_file(target_root: Path, relative_path: str, text: str) -> BackupWrittenFile:
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return BackupWrittenFile(
        relative_path=relative_path,
        source_path=None,
        bytes_written=target.stat().st_size,
    )


def _copy_file(target_root: Path, source: Path, relative_path: str) -> BackupWrittenFile:
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return BackupWrittenFile(
        relative_path=relative_path,
        source_path=str(source),
        bytes_written=target.stat().st_size,
    )


def _copy_directory(
    target_root: Path,
    source_dir: Path,
    target_subdir: str,
    allowed_root: Path | None = None,
) -> tuple[BackupWrittenFile, ...]:
    written: list[BackupWrittenFile] = []
    if (
        not source_dir.exists()
        or not source_dir.is_dir()
        or is_forbidden_backup_restore_path(
            source_dir,
            root=allowed_root or source_dir.parent,
        )
    ):
        return ()

    for source in sorted(path for path in source_dir.rglob("*") if path.is_file()):
        if _is_excluded_copy_path(source, source_dir):
            continue
        relative_source = source.relative_to(source_dir)
        relative_target = Path(target_subdir) / relative_source
        written.append(_copy_file(target_root, source, relative_target.as_posix()))

    return tuple(written)


def _write_manifest(target_root: Path, preview: BackupPreview) -> BackupWrittenFile:
    manifest = dict(preview.manifest_preview)
    manifest["preview_only"] = False
    manifest["persisted"] = True
    text = json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True)
    return _write_text_file(target_root, "manifest.json", text + "\n")


def _write_safety_docs(target_root: Path, project_root: Path) -> tuple[BackupWrittenFile, ...]:
    docs_root = project_root / "friday" / "docs"
    docs = (
        docs_root / "SAFETY_MATRIX.md",
        docs_root / "TEST_MATRIX.md",
        docs_root / "FRIDAY_ARCHITECTURE.md",
    )
    written: list[BackupWrittenFile] = []
    for source in docs:
        if (
            source.exists()
            and source.is_file()
            and not is_forbidden_backup_restore_path(source, root=docs_root)
        ):
            written.append(_copy_file(target_root, source, f"safety/{source.name}"))
    return tuple(written)


def write_local_backup(
    preview: BackupPreview | None,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    project_root: str | Path,
) -> BackupWriteResult:
    """Write a local backup only when guard checks allow it."""
    guard = check_backup_write_allowed(
        preview=preview,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        project_root=project_root,
    )

    if not guard.allowed or preview is None or guard.planned_backup_root is None:
        return BackupWriteResult(
            allowed=False,
            persisted=False,
            target_path=guard.planned_backup_root,
            written_files=(),
            blocked_reasons=guard.blocked_reasons,
            message=guard.message or "Backup wurde nicht freigegeben.",
            preview_only=True,
            external_lookup_used=False,
        )

    target_root = Path(guard.planned_backup_root)
    if target_root.exists():
        return BackupWriteResult(
            allowed=False,
            persisted=False,
            target_path=str(target_root),
            written_files=(),
            blocked_reasons=("target_exists",),
            message="Backup wurde nicht erstellt, weil der Zielordner bereits existiert.",
            preview_only=True,
            external_lookup_used=False,
        )

    project_root_path = Path(project_root)
    target_root.mkdir(parents=True, exist_ok=False)
    written: list[BackupWrittenFile] = [
        _write_manifest(target_root, preview),
        _write_text_file(target_root, "README_BACKUP.md", BACKUP_README_TEXT),
    ]

    for section in preview.sections:
        if section.name == "database" and section.status == "included" and section.path:
            source = Path(section.path)
            if not is_forbidden_backup_restore_path(source, root=project_root_path):
                written.append(_copy_file(target_root, source, f"database/{source.name}"))
        if section.name == "exports" and section.status == "included" and section.path:
            written.extend(
                _copy_directory(
                    target_root,
                    Path(section.path),
                    "exports",
                    allowed_root=project_root_path,
                )
            )
        if section.name == "safety_docs" and section.status == "included":
            written.extend(_write_safety_docs(target_root, project_root_path))

    return BackupWriteResult(
        allowed=True,
        persisted=True,
        target_path=str(target_root),
        written_files=tuple(written),
        blocked_reasons=(),
        message="Backup wurde lokal erstellt.",
        preview_only=False,
        external_lookup_used=False,
    )
