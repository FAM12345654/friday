"""Tests for the guarded local privacy cleanup writer prototype."""

from __future__ import annotations

from pathlib import Path

from friday.app.privacy_cleanup_write_guard import (
    PRIVACY_CLEANUP_TOKENS,
    check_privacy_cleanup_write_allowed,
)
from friday.app.privacy_cleanup_writer import apply_privacy_cleanup


def _allowed_guard(
    tmp_path: Path,
    *,
    cleanup_area: str = "exports",
    target_path: Path | None = None,
    allowed_base_path: Path | None = None,
):
    base = allowed_base_path or tmp_path / "local_data" / cleanup_area
    target = target_path or base / "old_item"
    return check_privacy_cleanup_write_allowed(
        cleanup_area=cleanup_area,
        target_path=target,
        project_root=tmp_path,
        allowed_base_path=base,
        preview_was_shown=True,
        approval_token=PRIVACY_CLEANUP_TOKENS[cleanup_area],
        scanner_smoke_passed=True,
    )


def test_privacy_cleanup_writer_blocks_missing_guard(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "exports" / "old_item"
    target.mkdir(parents=True)

    result = apply_privacy_cleanup(
        guard_result=None,
        cleanup_area="exports",
        target_path=target,
    )

    assert result.performed is False
    assert "missing_guard" in result.blocked_reasons
    assert target.exists() is True


def test_privacy_cleanup_writer_blocks_guard_failure_without_deleting(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "exports" / "old_item"
    target.mkdir(parents=True)
    guard = check_privacy_cleanup_write_allowed(
        cleanup_area="exports",
        target_path=target,
        project_root=tmp_path,
        allowed_base_path=tmp_path / "local_data" / "exports",
        preview_was_shown=True,
        approval_token="JA",
        scanner_smoke_passed=True,
    )

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="exports",
        target_path=target,
        dry_run=False,
    )

    assert result.performed is False
    assert "guard_blocked" in result.blocked_reasons
    assert "invalid_token" in result.blocked_reasons
    assert target.exists() is True


def test_privacy_cleanup_writer_dry_run_does_not_delete(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "exports" / "old_item"
    target.mkdir(parents=True)
    (target / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    guard = _allowed_guard(tmp_path, target_path=target)

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="exports",
        target_path=target,
        dry_run=True,
    )

    assert result.status == "dry_run"
    assert result.performed is False
    assert result.deleted_count == 0
    assert result.planned_count == 2
    assert target.exists() is True


def test_privacy_cleanup_writer_deletes_allowed_file_target(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "exports" / "old_export.md"
    target.parent.mkdir(parents=True)
    target.write_text("old", encoding="utf-8")
    guard = _allowed_guard(tmp_path, target_path=target)

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="exports",
        target_path=target,
        dry_run=False,
    )

    assert result.status == "deleted"
    assert result.performed is True
    assert result.deleted_count == 1
    assert target.exists() is False


def test_privacy_cleanup_writer_deletes_allowed_directory_target(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "restore_work" / "old_restore"
    target.mkdir(parents=True)
    (target / "manifest.json").write_text("{}", encoding="utf-8")
    nested = target / "nested"
    nested.mkdir()
    (nested / "item.txt").write_text("data", encoding="utf-8")
    guard = _allowed_guard(
        tmp_path,
        cleanup_area="restore_work",
        target_path=target,
        allowed_base_path=tmp_path / "local_data" / "restore_work",
    )

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="restore_work",
        target_path=target,
        dry_run=False,
    )

    assert result.status == "deleted"
    assert result.performed is True
    assert result.deleted_count == 4
    assert target.exists() is False


def test_privacy_cleanup_writer_blocks_cleanup_area_mismatch(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "exports" / "old_item"
    target.mkdir(parents=True)
    guard = _allowed_guard(tmp_path, cleanup_area="exports", target_path=target)

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="backups",
        target_path=target,
        dry_run=False,
    )

    assert result.performed is False
    assert "cleanup_area_mismatch" in result.blocked_reasons
    assert target.exists() is True


def test_privacy_cleanup_writer_blocks_target_path_mismatch(tmp_path: Path) -> None:
    guarded_target = tmp_path / "local_data" / "exports" / "guarded"
    actual_target = tmp_path / "local_data" / "exports" / "actual"
    guarded_target.mkdir(parents=True)
    actual_target.mkdir(parents=True)
    guard = _allowed_guard(tmp_path, target_path=guarded_target)

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="exports",
        target_path=actual_target,
        dry_run=False,
    )

    assert result.performed is False
    assert "target_path_mismatch" in result.blocked_reasons
    assert actual_target.exists() is True


def test_privacy_cleanup_writer_blocks_latest_backup(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "backups" / "latest"
    target.mkdir(parents=True)
    guard = _allowed_guard(
        tmp_path,
        cleanup_area="backups",
        target_path=target,
        allowed_base_path=tmp_path / "local_data" / "backups",
    )

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="backups",
        target_path=target,
        latest_backup_path=target,
        dry_run=False,
    )

    assert result.performed is False
    assert "latest_backup_protected" in result.blocked_reasons
    assert target.exists() is True


def test_privacy_cleanup_writer_blocks_db_cleanup_areas(tmp_path: Path) -> None:
    guard = check_privacy_cleanup_write_allowed(
        cleanup_area="contact_context",
        target_path=None,
        project_root=tmp_path,
        allowed_base_path=None,
        preview_was_shown=True,
        approval_token=PRIVACY_CLEANUP_TOKENS["contact_context"],
        scanner_smoke_passed=True,
    )

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="contact_context",
        target_path=None,
        dry_run=False,
    )

    assert result.performed is False
    assert "unsupported_cleanup_area" in result.blocked_reasons
    assert "backup_required" in result.blocked_reasons
    assert "rollback_required" in result.blocked_reasons


def test_privacy_cleanup_writer_has_safe_flags(tmp_path: Path) -> None:
    target = tmp_path / "local_data" / "exports" / "old_item"
    target.mkdir(parents=True)
    guard = _allowed_guard(tmp_path, target_path=target)

    result = apply_privacy_cleanup(
        guard_result=guard,
        cleanup_area="exports",
        target_path=target,
        dry_run=True,
    )

    assert result.preview_only is False
    assert result.persisted is False
    assert result.external_action_used is False
    assert result.write_performed is False
