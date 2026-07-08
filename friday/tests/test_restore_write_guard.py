"""Tests for the local restore write guard model."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.backup_preview import build_backup_preview
from friday.app.backup_write_guard import BACKUP_WRITE_APPROVAL_TOKEN
from friday.app.backup_writer import write_local_backup
from friday.app.restore_dry_run import build_restore_dry_run
from friday.app.restore_write_guard import (
    RESTORE_WRITE_APPROVAL_TOKEN,
    check_restore_write_allowed,
)


def _write_safety_docs(project_root: Path) -> None:
    docs = project_root / "friday" / "docs"
    docs.mkdir(parents=True)
    (docs / "SAFETY_MATRIX.md").write_text("# Safety\n", encoding="utf-8")
    (docs / "TEST_MATRIX.md").write_text("# Tests\n", encoding="utf-8")
    (docs / "FRIDAY_ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")


def _write_backup(project_root: Path, include_active_db: bool = False):
    local_data = project_root / "local_data"
    exports = local_data / "exports"
    local_data.mkdir()
    exports.mkdir()
    db_path = local_data / "friday.sqlite"
    db_path.write_text("db", encoding="utf-8")
    (exports / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    _write_safety_docs(project_root)

    preview = build_backup_preview(project_root, timestamp="20260707_120000")
    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=project_root,
    )
    assert result.persisted is True
    assert result.target_path is not None

    if not include_active_db:
        db_path.unlink()

    return build_restore_dry_run(result.target_path, project_root)


def test_restore_write_guard_allows_clean_dry_run_and_token(tmp_path) -> None:
    dry_run = _write_backup(tmp_path)

    result = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_restore_write_guard_blocks_missing_dry_run(tmp_path) -> None:
    result = check_restore_write_allowed(
        dry_run=None,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "missing_dry_run" in result.blocked_reasons


@pytest.mark.parametrize(
    "token",
    [None, "", "JA", "ja", "ok", "yes", "SPEICHERN", "BACKUP ERSTELLEN"],
)
def test_restore_write_guard_blocks_wrong_tokens(tmp_path, token) -> None:
    dry_run = _write_backup(tmp_path)

    result = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=token,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_restore_write_guard_blocks_failed_dry_run(tmp_path) -> None:
    backup = tmp_path / "local_data" / "backups" / "backup"
    backup.mkdir(parents=True)
    dry_run = build_restore_dry_run(backup, tmp_path)

    result = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "dry_run_not_allowed" in result.blocked_reasons
    assert "missing_manifest" in result.blocked_reasons


def test_restore_write_guard_blocks_backup_outside_backups(tmp_path) -> None:
    outside = tmp_path / "outside_backup"
    outside.mkdir()
    dry_run = build_restore_dry_run(outside, tmp_path)

    result = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "backup_outside_backups" in result.blocked_reasons


def test_restore_write_guard_blocks_forbidden_backup_content(tmp_path) -> None:
    dry_run = _write_backup(tmp_path)
    assert dry_run.backup_root is not None
    (Path(dry_run.backup_root) / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    dry_run = build_restore_dry_run(dry_run.backup_root, tmp_path)

    result = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "forbidden_backup_content" in result.blocked_reasons


def test_restore_write_guard_blocks_active_database_conflict(tmp_path) -> None:
    dry_run = _write_backup(tmp_path, include_active_db=True)

    result = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "active_database_conflict" in result.blocked_reasons


def test_restore_write_guard_carries_dry_run_warnings(tmp_path) -> None:
    dry_run = _write_backup(tmp_path)
    assert dry_run.backup_root is not None
    database_file = Path(dry_run.backup_root) / "database" / "friday.sqlite"
    database_file.unlink()
    (Path(dry_run.backup_root) / "database").rmdir()
    dry_run = build_restore_dry_run(dry_run.backup_root, tmp_path)

    result = check_restore_write_allowed(
        dry_run=dry_run,
        approval_token=RESTORE_WRITE_APPROVAL_TOKEN,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert "Backup-Sektion fehlt: database" in result.warnings
