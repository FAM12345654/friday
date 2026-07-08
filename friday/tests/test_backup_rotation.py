"""Tests for local backup rotation preview, guard and writer."""

from __future__ import annotations

from pathlib import Path

from friday.app.backup_rotation_guard import (
    BACKUP_ROTATION_APPROVAL_TOKEN,
    check_backup_rotation_allowed,
)
from friday.app.backup_rotation_preview import build_backup_rotation_preview
from friday.app.backup_rotation_writer import apply_backup_rotation


def _backup_dir(root: Path, name: str) -> Path:
    path = root / "local_data" / "backups" / name
    path.mkdir(parents=True)
    (path / "marker.txt").write_text(name, encoding="utf-8")
    return path


def test_backup_rotation_preview_selects_old_backups_and_protects_latest(tmp_path: Path) -> None:
    old_backup = _backup_dir(tmp_path, "friday_backup_20260701_100000")
    latest_backup = _backup_dir(tmp_path, "friday_backup_20260702_100000")

    preview = build_backup_rotation_preview(tmp_path)

    assert preview.cleanup_count == 1
    assert preview.protected_count == 1
    selected = [candidate.path for candidate in preview.candidates if candidate.selected_for_cleanup]
    protected = [candidate.path for candidate in preview.candidates if candidate.protected]
    assert selected == [str(old_backup)]
    assert protected == [str(latest_backup)]
    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False


def test_backup_rotation_guard_allows_valid_preview_token_and_smoke(tmp_path: Path) -> None:
    _backup_dir(tmp_path, "friday_backup_20260701_100000")
    _backup_dir(tmp_path, "friday_backup_20260702_100000")
    preview = build_backup_rotation_preview(tmp_path)

    result = check_backup_rotation_allowed(
        preview=preview,
        approval_token=BACKUP_ROTATION_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert len(result.delete_paths) == 1
    assert len(result.protected_paths) == 1


def test_backup_rotation_guard_blocks_wrong_token(tmp_path: Path) -> None:
    _backup_dir(tmp_path, "friday_backup_20260701_100000")
    _backup_dir(tmp_path, "friday_backup_20260702_100000")
    preview = build_backup_rotation_preview(tmp_path)

    result = check_backup_rotation_allowed(
        preview=preview,
        approval_token="JA",
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_backup_rotation_guard_blocks_smoke_failure(tmp_path: Path) -> None:
    _backup_dir(tmp_path, "friday_backup_20260701_100000")
    _backup_dir(tmp_path, "friday_backup_20260702_100000")
    preview = build_backup_rotation_preview(tmp_path)

    result = check_backup_rotation_allowed(
        preview=preview,
        approval_token=BACKUP_ROTATION_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons


def test_backup_rotation_guard_blocks_when_only_latest_exists(tmp_path: Path) -> None:
    _backup_dir(tmp_path, "friday_backup_20260702_100000")
    preview = build_backup_rotation_preview(tmp_path)

    result = check_backup_rotation_allowed(
        preview=preview,
        approval_token=BACKUP_ROTATION_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "no_cleanup_candidates" in result.blocked_reasons


def test_backup_rotation_writer_deletes_old_backup_and_keeps_latest(tmp_path: Path) -> None:
    old_backup = _backup_dir(tmp_path, "friday_backup_20260701_100000")
    latest_backup = _backup_dir(tmp_path, "friday_backup_20260702_100000")
    preview = build_backup_rotation_preview(tmp_path)
    guard = check_backup_rotation_allowed(
        preview=preview,
        approval_token=BACKUP_ROTATION_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    result = apply_backup_rotation(guard)

    assert result.performed is True
    assert str(old_backup) in result.deleted_paths
    assert old_backup.exists() is False
    assert latest_backup.exists() is True
    assert result.persisted is True
    assert result.external_action_used is False


def test_backup_rotation_writer_blocks_guard_failure_without_deleting(tmp_path: Path) -> None:
    old_backup = _backup_dir(tmp_path, "friday_backup_20260701_100000")
    latest_backup = _backup_dir(tmp_path, "friday_backup_20260702_100000")
    preview = build_backup_rotation_preview(tmp_path)
    guard = check_backup_rotation_allowed(
        preview=preview,
        approval_token="",
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    result = apply_backup_rotation(guard)

    assert result.performed is False
    assert "guard_blocked" in result.blocked_reasons
    assert old_backup.exists() is True
    assert latest_backup.exists() is True
