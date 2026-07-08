"""Tests for the local data export guard model."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.local_data_export_guard import (
    REQUIRED_LOCAL_DATA_EXPORT_EXCLUSIONS,
    check_local_data_export_allowed,
)
from friday.app.local_data_export_preview import (
    LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
    LocalDataExportPreview,
    LocalDataExportSection,
    build_local_data_export_preview,
)


def _section(
    name: str = "Aufgaben",
    sensitive_details_excluded: bool = True,
) -> LocalDataExportSection:
    return LocalDataExportSection(
        name=name,
        file_format="summary_json",
        planned=True,
        sensitive_details_excluded=sensitive_details_excluded,
        notes=("test_section",),
    )


def _fake_preview(
    target_root: Path,
    sections: tuple[LocalDataExportSection, ...] | None = None,
    excluded_items: tuple[str, ...] = REQUIRED_LOCAL_DATA_EXPORT_EXCLUSIONS,
) -> LocalDataExportPreview:
    return LocalDataExportPreview(
        target_root=str(target_root),
        sections=sections or (_section(),),
        excluded_items=excluded_items,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def test_local_data_export_guard_allows_valid_preview_and_token(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
        timestamp="20260707_213200",
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert "local_data" in result.target_root
    assert "exports" in result.target_root


def test_local_data_export_guard_blocks_missing_preview(tmp_path: Path) -> None:
    result = check_local_data_export_allowed(
        preview=None,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "missing_preview" in result.blocked_reasons


@pytest.mark.parametrize(
    "token",
    [None, "", "ja", "JA", "ok", "DATEN", "DATEN EXPORTIEREN "],
)
def test_local_data_export_guard_blocks_wrong_token(
    tmp_path: Path,
    token: str | None,
) -> None:
    preview = build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=token,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_local_data_export_guard_blocks_smoke_failure(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons


def test_local_data_export_guard_blocks_target_outside_exports(tmp_path: Path) -> None:
    preview = _fake_preview(target_root=tmp_path / "outside" / "export")

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "target_outside_exports" in result.blocked_reasons


def test_local_data_export_guard_blocks_missing_required_exclusion(tmp_path: Path) -> None:
    preview = _fake_preview(
        target_root=tmp_path / "local_data" / "exports" / "export",
        excluded_items=tuple(
            item
            for item in REQUIRED_LOCAL_DATA_EXPORT_EXCLUSIONS
            if item != "raw_active_database"
        ),
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "required_exclusion_missing" in result.blocked_reasons
    assert "raw_active_database" in result.missing_exclusions


def test_local_data_export_guard_blocks_sensitive_details_included(tmp_path: Path) -> None:
    preview = _fake_preview(
        target_root=tmp_path / "local_data" / "exports" / "export",
        sections=(_section(sensitive_details_excluded=False),),
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "sensitive_details_not_excluded" in result.blocked_reasons


def test_local_data_export_guard_has_safe_flags(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False
    assert result.scanner_smoke_required is True


def test_local_data_export_guard_does_not_create_export_directory(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
        timestamp="20260707_213200",
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert Path(preview.target_root).exists() is False


def test_local_data_export_guard_reports_checked_sections(tmp_path: Path) -> None:
    preview = build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
    )

    result = check_local_data_export_allowed(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert "Aufgaben" in result.checked_sections
    assert "Kontakt-Kontexte" in result.checked_sections
