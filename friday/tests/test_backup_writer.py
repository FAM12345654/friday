"""Tests for the guarded local backup writer."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.backup_preview import BackupPreview, BackupPreviewSection, build_backup_preview
from friday.app.backup_write_guard import BACKUP_WRITE_APPROVAL_TOKEN
from friday.app.backup_writer import write_local_backup


def _write_safety_docs(project_root: Path) -> None:
    docs = project_root / "friday" / "docs"
    docs.mkdir(parents=True)
    (docs / "SAFETY_MATRIX.md").write_text("# Safety\n", encoding="utf-8")
    (docs / "TEST_MATRIX.md").write_text("# Tests\n", encoding="utf-8")
    (docs / "FRIDAY_ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")


def _prepare_backup_sources(project_root: Path) -> None:
    local_data = project_root / "local_data"
    exports = local_data / "exports"
    local_data.mkdir()
    exports.mkdir()
    (local_data / "friday.sqlite").write_text("db", encoding="utf-8")
    (exports / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    _write_safety_docs(project_root)


def _section(name: str, status: str) -> BackupPreviewSection:
    return BackupPreviewSection(
        name=name,
        status=status,  # type: ignore[arg-type]
        path=None,
        reason="test",
        file_count=0,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def test_write_local_backup_writes_allowed_sections(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    target = Path(result.target_path)
    written_paths = {file.relative_path for file in result.written_files}
    assert result.allowed is True
    assert result.persisted is True
    assert target.exists()
    assert "manifest.json" in written_paths
    assert "README_BACKUP.md" in written_paths
    assert "database/friday.sqlite" in written_paths
    assert "exports/tasks.md" in written_paths
    assert "safety/SAFETY_MATRIX.md" in written_paths


def test_write_local_backup_blocks_wrong_token_without_writing(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = write_local_backup(
        preview=preview,
        approval_token="JA",
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.persisted is False
    assert "invalid_token" in result.blocked_reasons
    assert Path(preview.planned_backup_root).exists() is False


def test_write_local_backup_blocks_guard_failure_without_writing(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
        project_root=tmp_path,
    )

    assert result.persisted is False
    assert "scanner_smoke_failed" in result.blocked_reasons
    assert Path(preview.planned_backup_root).exists() is False


def test_write_local_backup_blocks_target_outside_backups(tmp_path) -> None:
    preview = BackupPreview(
        project_root=str(tmp_path),
        planned_backup_root=str(tmp_path / "outside" / "backup"),
        sections=(
            _section("secrets", "excluded"),
            _section("obsidian_vault", "excluded"),
            _section("venv_cache", "excluded"),
        ),
        manifest_preview={},
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.persisted is False
    assert "target_outside_backups" in result.blocked_reasons
    assert (tmp_path / "outside").exists() is False


def test_write_local_backup_does_not_copy_env_or_obsidian_vault(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    (tmp_path / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    obsidian = tmp_path / "ObsidianVault"
    obsidian.mkdir()
    (obsidian / "secret.md").write_text("vault", encoding="utf-8")
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    target = Path(result.target_path)
    assert result.persisted is True
    assert (target / ".env").exists() is False
    assert (target / "ObsidianVault").exists() is False
    assert (target / "obsidian_vault").exists() is False


def test_write_local_backup_skips_sensitive_export_paths(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    exports = tmp_path / "local_data" / "exports"
    sensitive_files = (
        exports / ".env.local",
        exports / "secrets" / "token.txt",
        exports / "obsidian_vault" / "note.md",
        exports / "Obsidian Vault" / "note.md",
        exports / ".obsidian" / "workspace.json",
        exports / "api_keys.json",
        exports / "credentials.txt",
        exports / "tokens.json",
        exports / "private_key.pem",
        exports / "passwords.txt",
    )
    for path in sensitive_files:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("sensitive test payload\n", encoding="utf-8")
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    target = Path(result.target_path)
    written_paths = {file.relative_path for file in result.written_files}
    assert result.persisted is True
    assert "exports/tasks.md" in written_paths
    assert "exports/.env.local" not in written_paths
    assert "exports/secrets/token.txt" not in written_paths
    assert "exports/obsidian_vault/note.md" not in written_paths
    assert "exports/Obsidian Vault/note.md" not in written_paths
    assert "exports/.obsidian/workspace.json" not in written_paths
    assert "exports/api_keys.json" not in written_paths
    assert "exports/credentials.txt" not in written_paths
    assert "exports/tokens.json" not in written_paths
    assert "exports/private_key.pem" not in written_paths
    assert "exports/passwords.txt" not in written_paths
    assert (target / "exports" / ".env.local").exists() is False
    assert (target / "exports" / "secrets").exists() is False
    assert (target / "exports" / "Obsidian Vault").exists() is False
    assert (target / "exports" / ".obsidian").exists() is False


def test_write_local_backup_skips_symlink_database(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    db_path = tmp_path / "local_data" / "friday.sqlite"
    db_path.unlink()
    external_secret = tmp_path / "outside_secret.sqlite"
    external_secret.write_text("secret\n", encoding="utf-8")
    try:
        db_path.symlink_to(external_secret)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    written_paths = {file.relative_path for file in result.written_files}
    target = Path(result.target_path)
    assert result.persisted is True
    assert "database/friday.sqlite" not in written_paths
    assert (target / "database" / "friday.sqlite").exists() is False


def test_write_local_backup_skips_export_symlink_files(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    external_secret = tmp_path / "outside_secret.txt"
    external_secret.write_text("secret\n", encoding="utf-8")
    symlink_path = tmp_path / "local_data" / "exports" / "linked_task.md"
    try:
        symlink_path.symlink_to(external_secret)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    target = Path(result.target_path)
    written_paths = {file.relative_path for file in result.written_files}
    assert result.persisted is True
    assert "exports/linked_task.md" not in written_paths
    assert (target / "exports" / "linked_task.md").exists() is False


def test_write_local_backup_skips_fake_preview_sources_outside_project(tmp_path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside = tmp_path / "outside_backup_source"
    outside.mkdir()
    outside_db = outside / "outside.sqlite"
    outside_db.write_text("outside db\n", encoding="utf-8")
    outside_exports = outside / "exports"
    outside_exports.mkdir()
    (outside_exports / "tasks.md").write_text("# Outside\n", encoding="utf-8")
    preview = BackupPreview(
        project_root=str(project_root),
        planned_backup_root=str(project_root / "local_data" / "backups" / "friday_backup_fake"),
        sections=(
            BackupPreviewSection(
                name="database",
                status="included",
                path=str(outside_db),
                reason="fake",
                file_count=1,
                preview_only=True,
                persisted=False,
                external_lookup_used=False,
            ),
            BackupPreviewSection(
                name="exports",
                status="included",
                path=str(outside_exports),
                reason="fake",
                file_count=1,
                preview_only=True,
                persisted=False,
                external_lookup_used=False,
            ),
            _section("secrets", "excluded"),
            _section("obsidian_vault", "excluded"),
            _section("venv_cache", "excluded"),
        ),
        manifest_preview={},
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=project_root,
    )

    target = Path(result.target_path)
    written_paths = {file.relative_path for file in result.written_files}
    assert result.persisted is True
    assert "database/outside.sqlite" not in written_paths
    assert "exports/tasks.md" not in written_paths
    assert (target / "database" / "outside.sqlite").exists() is False
    assert (target / "exports" / "tasks.md").exists() is False


def test_write_local_backup_blocks_existing_target_without_overwrite(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")
    target = Path(preview.planned_backup_root)
    target.mkdir(parents=True)
    marker = target / "marker.txt"
    marker.write_text("keep", encoding="utf-8")

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.persisted is False
    assert result.blocked_reasons == ("target_exists",)
    assert marker.read_text(encoding="utf-8") == "keep"


def test_write_local_backup_has_safe_flags(tmp_path) -> None:
    _prepare_backup_sources(tmp_path)
    preview = build_backup_preview(tmp_path)

    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.preview_only is False
    assert result.persisted is True
    assert result.external_lookup_used is False
