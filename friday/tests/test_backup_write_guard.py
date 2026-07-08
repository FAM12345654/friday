"""Tests for the local backup write guard model."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.backup_preview import (
    BackupPreview,
    BackupPreviewSection,
    build_backup_preview,
)
from friday.app.backup_write_guard import (
    BACKUP_WRITE_APPROVAL_TOKEN,
    check_backup_write_allowed,
)


def _section(
    name: str,
    status: str,
    path: str | None = None,
) -> BackupPreviewSection:
    return BackupPreviewSection(
        name=name,
        status=status,  # type: ignore[arg-type]
        path=path,
        reason="test",
        file_count=0,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _fake_preview(
    project_root: Path,
    planned_backup_root: Path,
    sections: tuple[BackupPreviewSection, ...],
) -> BackupPreview:
    return BackupPreview(
        project_root=str(project_root),
        planned_backup_root=str(planned_backup_root),
        sections=sections,
        manifest_preview={},
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def test_backup_write_guard_allows_valid_preview_and_token(tmp_path) -> None:
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert "local_data" in result.planned_backup_root
    assert "backups" in result.planned_backup_root


def test_backup_write_guard_blocks_missing_preview(tmp_path) -> None:
    result = check_backup_write_allowed(
        preview=None,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "missing_preview" in result.blocked_reasons


@pytest.mark.parametrize(
    "token",
    [None, "", "ja", "JA", "ok", "yes", "speichern", "BACKUP"],
)
def test_backup_write_guard_blocks_wrong_token(tmp_path, token) -> None:
    preview = build_backup_preview(tmp_path)

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=token,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_backup_write_guard_blocks_smoke_failure(tmp_path) -> None:
    preview = build_backup_preview(tmp_path)

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons


def test_backup_write_guard_blocks_target_outside_backups(tmp_path) -> None:
    preview = _fake_preview(
        project_root=tmp_path,
        planned_backup_root=tmp_path / "outside" / "backup",
        sections=(
            _section("database", "missing"),
            _section("secrets", "excluded"),
            _section("obsidian_vault", "excluded"),
            _section("venv_cache", "excluded"),
        ),
    )

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "target_outside_backups" in result.blocked_reasons


def test_backup_write_guard_blocks_if_secrets_marked_included(tmp_path) -> None:
    preview = _fake_preview(
        project_root=tmp_path,
        planned_backup_root=tmp_path / "local_data" / "backups" / "backup",
        sections=(
            _section("database", "missing"),
            _section("secrets", "included"),
            _section("obsidian_vault", "excluded"),
            _section("venv_cache", "excluded"),
        ),
    )

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "excluded_section_present" in result.blocked_reasons


def test_backup_write_guard_blocks_if_obsidian_vault_marked_included(tmp_path) -> None:
    preview = _fake_preview(
        project_root=tmp_path,
        planned_backup_root=tmp_path / "local_data" / "backups" / "backup",
        sections=(
            _section("database", "missing"),
            _section("secrets", "excluded"),
            _section("obsidian_vault", "included"),
            _section("venv_cache", "excluded"),
        ),
    )

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "excluded_section_present" in result.blocked_reasons


def test_backup_write_guard_has_safe_flags(tmp_path) -> None:
    preview = build_backup_preview(tmp_path)

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_backup_write_guard_does_not_create_backup_directory(tmp_path) -> None:
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = check_backup_write_allowed(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert Path(preview.planned_backup_root).exists() is False
