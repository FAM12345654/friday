"""Tests for the guarded local review export model."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.review_export_guard import check_review_export_allowed
from friday.app.review_export_preview import (
    REVIEW_EXPORT_APPROVAL_TOKEN,
    REVIEW_EXPORT_REQUIRED_EXCLUSIONS,
    ReviewExportPreview,
    ReviewExportSection,
    build_review_export_preview,
)


def _section(sensitive_details_excluded: bool = True) -> ReviewExportSection:
    return ReviewExportSection(
        name="Review",
        file_format="summary_json",
        planned=True,
        sensitive_details_excluded=sensitive_details_excluded,
        notes=("test",),
    )


def _fake_preview(
    target_root: Path,
    excluded_items: tuple[str, ...] = REVIEW_EXPORT_REQUIRED_EXCLUSIONS,
    sensitive_details_excluded: bool = True,
) -> ReviewExportPreview:
    return ReviewExportPreview(
        target_root=str(target_root),
        sections=(_section(sensitive_details_excluded=sensitive_details_excluded),),
        excluded_items=excluded_items,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def test_review_export_guard_allows_valid_preview_and_token(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path, timestamp="20260708_120000")

    result = check_review_export_allowed(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert "Nachrichten-Vorschlaege" in result.checked_sections


def test_review_export_guard_blocks_missing_preview(tmp_path: Path) -> None:
    result = check_review_export_allowed(
        preview=None,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "missing_preview" in result.blocked_reasons


@pytest.mark.parametrize(
    "token",
    [None, "", "ja", "JA", "ok", "REVIEW", "REVIEW EXPORTIEREN "],
)
def test_review_export_guard_blocks_wrong_token(
    tmp_path: Path,
    token: str | None,
) -> None:
    preview = build_review_export_preview(tmp_path)

    result = check_review_export_allowed(
        preview=preview,
        approval_token=token,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_review_export_guard_blocks_smoke_failure(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = check_review_export_allowed(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons


def test_review_export_guard_blocks_target_outside_exports(tmp_path: Path) -> None:
    preview = _fake_preview(tmp_path / "outside" / "review_export")

    result = check_review_export_allowed(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "target_outside_exports" in result.blocked_reasons


def test_review_export_guard_blocks_missing_required_exclusion(tmp_path: Path) -> None:
    preview = _fake_preview(
        tmp_path / "local_data" / "exports" / "review_export",
        excluded_items=tuple(
            item
            for item in REVIEW_EXPORT_REQUIRED_EXCLUSIONS
            if item != "raw_private_messages"
        ),
    )

    result = check_review_export_allowed(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "required_exclusion_missing" in result.blocked_reasons
    assert "raw_private_messages" in result.missing_exclusions


def test_review_export_guard_blocks_sensitive_details_included(tmp_path: Path) -> None:
    preview = _fake_preview(
        tmp_path / "local_data" / "exports" / "review_export",
        sensitive_details_excluded=False,
    )

    result = check_review_export_allowed(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "sensitive_details_not_excluded" in result.blocked_reasons


def test_review_export_guard_has_safe_flags(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = check_review_export_allowed(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
    )

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False
    assert result.scanner_smoke_required is True
