"""Tests for the local data export preview model."""

from __future__ import annotations

from pathlib import Path

from friday.app.local_data_export_preview import (
    LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
    build_local_data_export_preview,
)


def test_local_data_export_preview_is_preview_only(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(local_data_dir=tmp_path / "local_data")

    assert preview.preview_only is True
    assert preview.persisted is False
    assert preview.external_lookup_used is False


def test_local_data_export_preview_targets_local_exports_folder(tmp_path: Path) -> None:
    local_data_dir = tmp_path / "local_data"

    preview = build_local_data_export_preview(
        local_data_dir=local_data_dir,
        timestamp="20260707_213200",
    )

    assert preview.target_root == str(
        local_data_dir / "exports" / "friday_data_export_20260707_213200"
    )


def test_local_data_export_preview_does_not_create_paths(tmp_path: Path) -> None:
    local_data_dir = tmp_path / "local_data"

    build_local_data_export_preview(local_data_dir=local_data_dir)

    assert not local_data_dir.exists()


def test_local_data_export_preview_lists_expected_sections(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(local_data_dir=tmp_path / "local_data")
    section_names = {section.name for section in preview.sections}

    assert "Aufgaben" in section_names
    assert "Kontakt-Kontexte" in section_names
    assert "Review-Vorschlaege" in section_names
    assert "Privacy Dashboard Summary" in section_names
    assert "Safety Matrix" in section_names


def test_local_data_export_preview_excludes_secrets_and_sensitive_payloads(
    tmp_path: Path,
) -> None:
    preview = build_local_data_export_preview(local_data_dir=tmp_path / "local_data")

    assert ".env" in preview.excluded_items
    assert "api_keys" in preview.excluded_items
    assert "tokens" in preview.excluded_items
    assert "obsidian_vault" in preview.excluded_items
    assert "full_private_messages" in preview.excluded_items
    assert "raw_active_database" in preview.excluded_items


def test_local_data_export_preview_uses_hard_approval_token(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(local_data_dir=tmp_path / "local_data")

    assert preview.approval_token == LOCAL_DATA_EXPORT_APPROVAL_TOKEN
    assert preview.approval_token == "DATEN EXPORTIEREN"


def test_local_data_export_preview_sections_exclude_sensitive_details(
    tmp_path: Path,
) -> None:
    preview = build_local_data_export_preview(local_data_dir=tmp_path / "local_data")

    assert preview.sections
    assert all(section.planned for section in preview.sections)
    assert all(section.sensitive_details_excluded for section in preview.sections)
