"""Tests for the local backup preview model."""

from __future__ import annotations

from pathlib import Path

from friday.app.backup_preview import build_backup_preview


def _section_by_name(preview, name: str):
    return next(section for section in preview.sections if section.name == name)


def _write_safety_docs(project_root: Path) -> None:
    docs = project_root / "friday" / "docs"
    docs.mkdir(parents=True)
    (docs / "SAFETY_MATRIX.md").write_text("# Safety\n", encoding="utf-8")
    (docs / "TEST_MATRIX.md").write_text("# Tests\n", encoding="utf-8")
    (docs / "FRIDAY_ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")


def test_build_backup_preview_includes_existing_database(tmp_path) -> None:
    local_data = tmp_path / "local_data"
    local_data.mkdir()
    database = local_data / "friday.sqlite"
    database.write_text("sqlite placeholder", encoding="utf-8")

    preview = build_backup_preview(tmp_path)
    section = _section_by_name(preview, "database")

    assert section.status == "included"
    assert section.path == str(database)
    assert section.file_count == 1


def test_build_backup_preview_marks_missing_database(tmp_path) -> None:
    preview = build_backup_preview(tmp_path)
    section = _section_by_name(preview, "database")

    assert section.status == "missing"
    assert section.path is None


def test_build_backup_preview_includes_exports_directory(tmp_path) -> None:
    exports = tmp_path / "local_data" / "exports"
    exports.mkdir(parents=True)
    (exports / "example.md").write_text("# Export\n", encoding="utf-8")

    preview = build_backup_preview(tmp_path)
    section = _section_by_name(preview, "exports")

    assert section.status == "included"
    assert section.path == str(exports)
    assert section.file_count == 1


def test_build_backup_preview_excludes_secrets_and_env(tmp_path) -> None:
    (tmp_path / ".env").write_text("TOKEN=secret\n", encoding="utf-8")

    preview = build_backup_preview(tmp_path)
    section = _section_by_name(preview, "secrets")

    assert section.status == "excluded"
    assert section.path is None
    assert ".env" not in preview.manifest_preview["included_sections"]


def test_build_backup_preview_excludes_obsidian_vault(tmp_path) -> None:
    preview = build_backup_preview(tmp_path)
    section = _section_by_name(preview, "obsidian_vault")

    assert section.status == "excluded"
    assert section.path is None


def test_build_backup_preview_includes_safety_docs_if_present(tmp_path) -> None:
    _write_safety_docs(tmp_path)

    preview = build_backup_preview(tmp_path)
    section = _section_by_name(preview, "safety_docs")

    assert section.status == "included"
    assert section.file_count == 3


def test_build_backup_preview_manifest_preview(tmp_path) -> None:
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")
    manifest = preview.manifest_preview

    assert manifest["friday_backup_version"] == 1
    assert manifest["backup_created_at"] == "20260707_120000"
    assert manifest["planned_backup_root"] == preview.planned_backup_root
    assert "included_sections" in manifest
    assert "excluded_sections" in manifest
    assert manifest["preview_only"] is True


def test_build_backup_preview_has_safe_flags(tmp_path) -> None:
    preview = build_backup_preview(tmp_path)

    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False
    for section in preview.sections:
        assert section.preview_only is True
        assert section.persisted is False
        assert section.external_lookup_used is False


def test_build_backup_preview_does_not_create_backup_directory(tmp_path) -> None:
    preview = build_backup_preview(tmp_path, timestamp="20260707_120000")

    assert Path(preview.planned_backup_root).exists() is False
