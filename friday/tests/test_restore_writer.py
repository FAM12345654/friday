"""Tests for the guarded local restore writer."""

from __future__ import annotations

from pathlib import Path

from friday.app.backup_preview import build_backup_preview
from friday.app.backup_write_guard import BACKUP_WRITE_APPROVAL_TOKEN
from friday.app.backup_writer import write_local_backup
from friday.app.restore_dry_run import (
    RestoreDryRunResult,
    RestoreDryRunSection,
    build_restore_dry_run,
)
from friday.app.restore_write_guard import RESTORE_WRITE_APPROVAL_TOKEN
from friday.app.restore_writer import write_local_restore_copy


def _write_safety_docs(project_root: Path) -> None:
    docs = project_root / "friday" / "docs"
    docs.mkdir(parents=True)
    (docs / "SAFETY_MATRIX.md").write_text("# Safety\n", encoding="utf-8")
    (docs / "TEST_MATRIX.md").write_text("# Tests\n", encoding="utf-8")
    (docs / "FRIDAY_ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")


def _write_backup(project_root: Path, keep_active_db: bool = False):
    local_data = project_root / "local_data"
    exports = local_data / "exports"
    local_data.mkdir()
    exports.mkdir()
    db_path = local_data / "friday.sqlite"
    db_path.write_text("active-db", encoding="utf-8")
    (exports / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    _write_safety_docs(project_root)

    preview = build_backup_preview(project_root, timestamp="20260707_120000")
    backup = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=project_root,
    )
    assert backup.persisted is True
    assert backup.target_path is not None

    if not keep_active_db:
        db_path.unlink()

    return build_restore_dry_run(backup.target_path, project_root), db_path


def test_write_local_restore_copy_writes_only_separate_restore_folder(tmp_path) -> None:
    dry_run, active_db_path = _write_backup(tmp_path)

    result = write_local_restore_copy(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    target = Path(result.target_root)
    written_paths = {file.relative_path for file in result.written_files}
    assert result.allowed is True
    assert result.persisted is True
    assert target == tmp_path / "local_data" / "restores" / "friday_restore_20260707_130000"
    assert target.exists()
    assert "RESTORE_MANIFEST.json" in written_paths
    assert "README_RESTORE.md" in written_paths
    assert "database/friday.sqlite" in written_paths
    assert "exports/tasks.md" in written_paths
    assert "safety/SAFETY_MATRIX.md" in written_paths
    assert active_db_path.exists() is False


def test_write_local_restore_copy_blocks_wrong_token_without_writing(tmp_path) -> None:
    dry_run, _active_db_path = _write_backup(tmp_path)

    result = write_local_restore_copy(
        dry_run=dry_run,
        approval_token="JA",
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    assert result.persisted is False
    assert "invalid_token" in result.blocked_reasons
    assert Path(result.target_root).exists() is False


def test_write_local_restore_copy_blocks_missing_dry_run_without_writing(tmp_path) -> None:
    result = write_local_restore_copy(
        dry_run=None,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    assert result.persisted is False
    assert "missing_dry_run" in result.blocked_reasons
    assert Path(result.target_root).exists() is False


def test_write_local_restore_copy_blocks_guard_failure_without_writing(tmp_path) -> None:
    dry_run, active_db_path = _write_backup(tmp_path, keep_active_db=True)

    result = write_local_restore_copy(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    assert result.persisted is False
    assert "active_database_conflict" in result.blocked_reasons
    assert active_db_path.read_text(encoding="utf-8") == "active-db"
    assert Path(result.target_root).exists() is False


def test_write_local_restore_copy_blocks_existing_target_without_overwrite(tmp_path) -> None:
    dry_run, _active_db_path = _write_backup(tmp_path)
    target = tmp_path / "local_data" / "restores" / "friday_restore_20260707_130000"
    target.mkdir(parents=True)
    marker = target / "marker.txt"
    marker.write_text("keep", encoding="utf-8")

    result = write_local_restore_copy(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    assert result.persisted is False
    assert result.blocked_reasons == ("target_exists",)
    assert marker.read_text(encoding="utf-8") == "keep"


def test_write_local_restore_copy_does_not_copy_forbidden_backup_content(tmp_path) -> None:
    dry_run, _active_db_path = _write_backup(tmp_path)
    assert dry_run.backup_root is not None
    (Path(dry_run.backup_root) / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    dry_run = build_restore_dry_run(dry_run.backup_root, tmp_path)

    result = write_local_restore_copy(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    assert result.persisted is False
    assert "forbidden_backup_content" in result.blocked_reasons
    assert Path(result.target_root).exists() is False


def test_write_local_restore_copy_skips_fake_dry_run_sources_outside_backup_root(
    tmp_path,
) -> None:
    backup_root = tmp_path / "local_data" / "backups" / "friday_backup_fake"
    backup_root.mkdir(parents=True)
    outside = tmp_path / "outside_restore_source"
    outside_exports = outside / "exports"
    outside_exports.mkdir(parents=True)
    outside_db = outside / "outside.sqlite"
    outside_db.write_text("outside db\n", encoding="utf-8")
    (outside_exports / "tasks.md").write_text("# Outside\n", encoding="utf-8")
    dry_run = RestoreDryRunResult(
        allowed=True,
        backup_root=str(backup_root),
        manifest_found=True,
        manifest_valid=True,
        sections_checked=(
            RestoreDryRunSection(
                name="database",
                status="present",
                path=str(outside_db),
                file_count=1,
                message="fake",
                preview_only=True,
                persisted=False,
                external_lookup_used=False,
            ),
            RestoreDryRunSection(
                name="exports",
                status="present",
                path=str(outside_exports),
                file_count=1,
                message="fake",
                preview_only=True,
                persisted=False,
                external_lookup_used=False,
            ),
        ),
        missing_sections=(),
        blocked_reasons=(),
        warnings=(),
        message="fake dry-run",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )

    result = write_local_restore_copy(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    target = Path(result.target_root)
    written_paths = {file.relative_path for file in result.written_files}
    assert result.persisted is True
    assert "database/outside.sqlite" not in written_paths
    assert "exports/tasks.md" not in written_paths
    assert (target / "database" / "outside.sqlite").exists() is False
    assert (target / "exports" / "tasks.md").exists() is False


def test_write_local_restore_copy_has_safe_flags(tmp_path) -> None:
    dry_run, _active_db_path = _write_backup(tmp_path)

    result = write_local_restore_copy(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
        timestamp="20260707_130000",
    )

    assert result.preview_only is False
    assert result.persisted is True
    assert result.external_lookup_used is False
