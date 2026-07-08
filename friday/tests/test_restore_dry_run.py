"""Tests for the local restore dry-run model."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.backup_preview import BackupPreview, BackupPreviewSection, build_backup_preview
from friday.app.backup_write_guard import BACKUP_WRITE_APPROVAL_TOKEN
from friday.app.backup_writer import write_local_backup
from friday.app.restore_dry_run import build_restore_dry_run


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


def _write_valid_backup(project_root: Path) -> Path:
    _prepare_backup_sources(project_root)
    preview = build_backup_preview(project_root, timestamp="20260707_120000")
    result = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=project_root,
    )
    assert result.persisted is True
    assert result.target_path is not None
    return Path(result.target_path)


def test_restore_dry_run_allows_valid_backup_without_writing(tmp_path) -> None:
    backup_root = _write_valid_backup(tmp_path)
    before = sorted(path.relative_to(backup_root).as_posix() for path in backup_root.rglob("*"))

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    after = sorted(path.relative_to(backup_root).as_posix() for path in backup_root.rglob("*"))
    checked_names = {section.name for section in result.sections_checked}
    assert result.allowed is True
    assert result.manifest_found is True
    assert result.manifest_valid is True
    assert result.persisted is False
    assert result.preview_only is True
    assert result.external_lookup_used is False
    assert before == after
    assert {"manifest", "readme", "database", "exports", "safety_docs"}.issubset(
        checked_names
    )


def test_restore_dry_run_blocks_missing_backup_folder(tmp_path) -> None:
    result = build_restore_dry_run(
        backup_root=tmp_path / "local_data" / "backups" / "missing",
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "backup_missing" in result.blocked_reasons
    assert result.persisted is False


def test_restore_dry_run_blocks_path_outside_backups(tmp_path) -> None:
    outside = tmp_path / "outside_backup"
    outside.mkdir()

    result = build_restore_dry_run(backup_root=outside, project_root=tmp_path)

    assert result.allowed is False
    assert result.blocked_reasons == ("target_outside_backups",)
    assert result.sections_checked == ()


def test_restore_dry_run_blocks_missing_manifest(tmp_path) -> None:
    backup_root = tmp_path / "local_data" / "backups" / "backup"
    backup_root.mkdir(parents=True)

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is False
    assert result.manifest_found is False
    assert "manifest_missing" in result.blocked_reasons


def test_restore_dry_run_blocks_invalid_manifest(tmp_path) -> None:
    backup_root = tmp_path / "local_data" / "backups" / "backup"
    backup_root.mkdir(parents=True)
    (backup_root / "manifest.json").write_text("{invalid", encoding="utf-8")

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is False
    assert result.manifest_found is True
    assert result.manifest_valid is False
    assert "manifest_invalid" in result.blocked_reasons


def test_restore_dry_run_blocks_external_manifest_path(tmp_path) -> None:
    backup_root = tmp_path / "local_data" / "backups" / "backup"
    backup_root.mkdir(parents=True)
    (backup_root / "manifest.json").write_text(
        '{"planned_backup_root": "C:/outside/friday_backup"}\n',
        encoding="utf-8",
    )

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is False
    assert "external_path_in_manifest" in result.blocked_reasons


def test_restore_dry_run_blocks_env_inside_backup(tmp_path) -> None:
    backup_root = _write_valid_backup(tmp_path)
    (backup_root / ".env").write_text("TOKEN=secret\n", encoding="utf-8")

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is False
    assert "forbidden_backup_content" in result.blocked_reasons


def test_restore_dry_run_blocks_obsidian_vault_inside_backup(tmp_path) -> None:
    backup_root = _write_valid_backup(tmp_path)
    vault = backup_root / "ObsidianVault"
    vault.mkdir()
    (vault / "note.md").write_text("secret", encoding="utf-8")

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is False
    assert "forbidden_backup_content" in result.blocked_reasons


@pytest.mark.parametrize(
    "relative_path",
    (
        ".env.local",
        "exports/Obsidian Vault/note.md",
        "exports/.obsidian/workspace.json",
        "exports/api_keys.json",
        "exports/credentials.txt",
        "exports/tokens.json",
        "exports/private_key.pem",
        "exports/passwords.txt",
    ),
)
def test_restore_dry_run_blocks_sensitive_backup_path_variants(
    tmp_path,
    relative_path: str,
) -> None:
    backup_root = _write_valid_backup(tmp_path)
    sensitive_path = backup_root / relative_path
    sensitive_path.parent.mkdir(parents=True, exist_ok=True)
    sensitive_path.write_text("sensitive test payload\n", encoding="utf-8")

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is False
    assert "forbidden_backup_content" in result.blocked_reasons


def test_restore_dry_run_blocks_symlink_inside_backup(tmp_path) -> None:
    backup_root = _write_valid_backup(tmp_path)
    external_secret = tmp_path / "outside_secret.txt"
    external_secret.write_text("secret\n", encoding="utf-8")
    symlink_path = backup_root / "exports" / "linked_task.md"
    try:
        symlink_path.symlink_to(external_secret)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is False
    assert "forbidden_backup_content" in result.blocked_reasons


def test_restore_dry_run_warns_about_missing_included_section(tmp_path) -> None:
    backup_root = _write_valid_backup(tmp_path)
    database_file = backup_root / "database" / "friday.sqlite"
    database_file.unlink()
    (backup_root / "database").rmdir()

    result = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert result.allowed is True
    assert "database" in result.missing_sections
    assert "Backup-Sektion fehlt: database" in result.warnings


def test_restore_dry_run_blocks_backup_from_preview_with_forbidden_section(tmp_path) -> None:
    backup_root = tmp_path / "local_data" / "backups" / "backup"
    preview = BackupPreview(
        project_root=str(tmp_path),
        planned_backup_root=str(backup_root),
        sections=(
            BackupPreviewSection(
                name="secrets",
                status="excluded",
                path=None,
                reason="test",
                file_count=0,
                preview_only=True,
                persisted=False,
                external_lookup_used=False,
            ),
        ),
        manifest_preview={
            "planned_backup_root": str(backup_root),
            "included_sections": (),
            "excluded_sections": ("secrets",),
        },
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
    assert result.persisted is True
    (backup_root / "secrets").mkdir()
    (backup_root / "secrets" / "token.txt").write_text("secret", encoding="utf-8")

    dry_run = build_restore_dry_run(backup_root=backup_root, project_root=tmp_path)

    assert dry_run.allowed is False
    assert "forbidden_backup_content" in dry_run.blocked_reasons
