"""Tests for the side-effect-free local data import apply write guard."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.local_data_import_apply_preview import (
    LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
    LocalDataImportApplyPreviewResult,
    LocalDataImportApplyPreviewSection,
)
from friday.app.local_data_import_apply_write_guard import (
    check_local_data_import_apply_write_allowed,
)


def _section(name: str, planned_count: int = 1) -> LocalDataImportApplyPreviewSection:
    return LocalDataImportApplyPreviewSection(
        name=name,
        planned_count=planned_count,
        action="preview_import_or_update",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _preview(
    *,
    status: str = "preview_ready",
    allowed_to_request_token: bool = True,
    blocked_reasons: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
    backup_ready: bool = True,
    external_lookup_used: bool = False,
    sections: tuple[LocalDataImportApplyPreviewSection, ...] | None = None,
) -> LocalDataImportApplyPreviewResult:
    return LocalDataImportApplyPreviewResult(
        status=status,  # type: ignore[arg-type]
        allowed_to_request_token=allowed_to_request_token,
        export_root="local_data/exports/friday_export_test",
        sections=sections
        or (
            _section("tasks"),
            _section("contact_contexts"),
            _section("review_suggestions"),
        ),
        blocked_reasons=blocked_reasons,  # type: ignore[arg-type]
        warnings=warnings,
        message="Import-Apply-Vorschau ist bereit. Es wurde nichts importiert.",
        backup_required=True,
        backup_ready=backup_ready,
        approval_token_required=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=external_lookup_used,
    )


def test_import_apply_write_guard_allows_valid_preview_and_exact_token() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    assert result.allowed is True
    assert result.status == "allowed"
    assert result.blocked_reasons == ()
    assert result.write_scope == ("tasks", "contact_contexts", "review_suggestions")
    assert result.required_token == LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN


def test_import_apply_write_guard_allows_warning_preview_without_blocking() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(status="warnings", warnings=("Hinweis fuer Import.",)),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    assert result.allowed is True
    assert result.status == "warnings"
    assert result.warnings == ("Hinweis fuer Import.",)


def test_import_apply_write_guard_blocks_missing_preview() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=None,
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert result.status == "invalid"
    assert "missing_preview" in result.blocked_reasons


@pytest.mark.parametrize(
    "token",
    [None, "", "ja", "JA", "ok", "import", "Import anwenden", "IMPORT", "IMPORT ANWENDEN "],
)
def test_import_apply_write_guard_blocks_wrong_tokens(token: str | None) -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=token,
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_import_apply_write_guard_blocks_scanner_smoke_failure() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
    )

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons


def test_import_apply_write_guard_blocks_preview_invalid() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(status="invalid", allowed_to_request_token=False),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert result.status == "invalid"
    assert "preview_invalid" in result.blocked_reasons
    assert "token_not_requestable" in result.blocked_reasons


def test_import_apply_write_guard_blocks_preview_blocked() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(status="blocked", allowed_to_request_token=False),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert result.status == "blocked"
    assert "preview_blocked" in result.blocked_reasons


def test_import_apply_write_guard_blocks_missing_backup_ready() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(backup_ready=False),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert "backup_required" in result.blocked_reasons


def test_import_apply_write_guard_blocks_conflicts_from_preview_and_input() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(blocked_reasons=("conflicts_present",)),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        conflicts_present=True,
    )

    assert result.allowed is False
    assert result.blocked_reasons.count("conflicts_present") == 1


def test_import_apply_write_guard_blocks_sensitive_data() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        sensitive_data_present=True,
    )

    assert result.allowed is False
    assert "sensitive_data_present" in result.blocked_reasons


def test_import_apply_write_guard_blocks_secrets_and_private_raw_messages() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        secrets_present=True,
        private_raw_messages_present=True,
    )

    assert result.allowed is False
    assert "secrets_present" in result.blocked_reasons
    assert "private_raw_messages_present" in result.blocked_reasons


def test_import_apply_write_guard_blocks_external_lookup_marker() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(external_lookup_used=True),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        external_lookup_used=True,
    )

    assert result.allowed is False
    assert result.blocked_reasons.count("external_lookup_used") == 1


def test_import_apply_write_guard_blocks_forbidden_write_scope() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        requested_write_scope=("tasks", "safety_status", "raw_active_database"),
    )

    assert result.allowed is False
    assert "forbidden_write_scope" in result.blocked_reasons
    assert result.forbidden_write_scope == ("safety_status", "raw_active_database")


def test_import_apply_write_guard_blocks_database_schema_change() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        database_schema_change_required=True,
    )

    assert result.allowed is False
    assert "database_schema_change_required" in result.blocked_reasons
    assert result.database_schema_change_required is True


def test_import_apply_write_guard_has_safe_flags() -> None:
    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
    assert result.database_schema_change_required is False


def test_import_apply_write_guard_does_not_write_files(tmp_path: Path) -> None:
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert result.allowed is True
    assert before == after
