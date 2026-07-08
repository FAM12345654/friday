"""Tests for the side-effect-free privacy cleanup write guard."""

from __future__ import annotations

from pathlib import Path

import pytest

from friday.app.privacy_cleanup_write_guard import (
    PRIVACY_CLEANUP_TOKENS,
    check_privacy_cleanup_write_allowed,
)


_DEFAULT_TOKEN = object()


def _guard(
    tmp_path: Path,
    *,
    cleanup_area: str = "exports",
    target_path: Path | None = None,
    allowed_base_path: Path | None = None,
    approval_token: str | None | object = _DEFAULT_TOKEN,
    preview_was_shown: bool = True,
    scanner_smoke_passed: bool = True,
    external_actions_enabled: bool = False,
    active_database_path: Path | None = None,
    obsidian_vault_path: Path | None = None,
):
    base = allowed_base_path or tmp_path / "local_data" / "exports"
    target = target_path if target_path is not None else base / "old_export"
    token = (
        PRIVACY_CLEANUP_TOKENS.get(cleanup_area)
        if approval_token is _DEFAULT_TOKEN
        else approval_token
    )
    return check_privacy_cleanup_write_allowed(
        cleanup_area=cleanup_area,
        target_path=target,
        project_root=tmp_path,
        allowed_base_path=base,
        preview_was_shown=preview_was_shown,
        approval_token=token,  # type: ignore[arg-type]
        scanner_smoke_passed=scanner_smoke_passed,
        external_actions_enabled=external_actions_enabled,
        active_database_path=active_database_path,
        obsidian_vault_path=obsidian_vault_path,
    )


def test_privacy_cleanup_write_guard_allows_valid_export_scope(tmp_path) -> None:
    result = _guard(tmp_path)

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert result.required_token == "EXPORT AUFRAEUMEN"


@pytest.mark.parametrize(
    ("cleanup_area", "token"),
    [
        ("exports", "EXPORT AUFRAEUMEN"),
        ("backups", "BACKUP AUFRAEUMEN"),
        ("restore_work", "RESTORE AUFRAEUMEN"),
        ("review_history", "REVIEW AUFRAEUMEN"),
        ("contact_context", "KONTAKT L\u00d6SCHEN"),
    ],
)
def test_privacy_cleanup_write_guard_maps_required_tokens(
    tmp_path,
    cleanup_area: str,
    token: str,
) -> None:
    result = _guard(
        tmp_path,
        cleanup_area=cleanup_area,
        approval_token=token,
        target_path=None if cleanup_area not in ("exports", "backups", "restore_work") else None,
    )

    assert result.required_token == token
    assert "invalid_token" not in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_unknown_area(tmp_path) -> None:
    result = _guard(tmp_path, cleanup_area="unknown", approval_token="EXPORT AUFRAEUMEN")

    assert result.allowed is False
    assert "unknown_cleanup_area" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_missing_preview(tmp_path) -> None:
    result = _guard(tmp_path, preview_was_shown=False)

    assert result.allowed is False
    assert "missing_preview" in result.blocked_reasons


@pytest.mark.parametrize("token", [None, "", "ja", "JA", "EXPORT AUFRAEUMEN "])
def test_privacy_cleanup_write_guard_blocks_invalid_tokens(tmp_path, token) -> None:
    result = _guard(tmp_path, approval_token=token)

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_scanner_smoke_failure(tmp_path) -> None:
    result = _guard(tmp_path, scanner_smoke_passed=False)

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_external_actions_enabled(tmp_path) -> None:
    result = _guard(tmp_path, external_actions_enabled=True)

    assert result.allowed is False
    assert "external_actions_enabled" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_missing_required_target_path(tmp_path) -> None:
    result = check_privacy_cleanup_write_allowed(
        cleanup_area="exports",
        target_path=None,
        project_root=tmp_path,
        allowed_base_path=tmp_path / "local_data" / "exports",
        preview_was_shown=True,
        approval_token="EXPORT AUFRAEUMEN",
        scanner_smoke_passed=True,
    )

    assert result.allowed is False
    assert "missing_target_path" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_target_outside_allowed_scope(tmp_path) -> None:
    result = _guard(
        tmp_path,
        target_path=tmp_path / "local_data" / "backups" / "old_backup",
        allowed_base_path=tmp_path / "local_data" / "exports",
    )

    assert result.allowed is False
    assert "target_outside_allowed_scope" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_project_root(tmp_path) -> None:
    result = _guard(
        tmp_path,
        target_path=tmp_path,
        allowed_base_path=tmp_path,
    )

    assert result.allowed is False
    assert "target_is_project_root" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_root_drive(tmp_path) -> None:
    root_drive = Path(tmp_path.anchor)
    result = _guard(
        tmp_path,
        target_path=root_drive,
        allowed_base_path=root_drive,
    )

    assert result.allowed is False
    assert "target_is_root" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_sensitive_paths(tmp_path) -> None:
    result = _guard(
        tmp_path,
        target_path=tmp_path / "local_data" / "exports" / ".env",
    )

    assert result.allowed is False
    assert "sensitive_path" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_obsidian_vault_path(tmp_path) -> None:
    vault = tmp_path / "ObsidianVault"
    result = _guard(
        tmp_path,
        target_path=vault / "Kontakt.md",
        allowed_base_path=tmp_path,
        obsidian_vault_path=vault,
    )

    assert result.allowed is False
    assert "obsidian_vault_path" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_active_database_path(tmp_path) -> None:
    db_path = tmp_path / "local_data" / "friday.db"
    result = _guard(
        tmp_path,
        target_path=db_path,
        allowed_base_path=tmp_path / "local_data",
        active_database_path=db_path,
    )

    assert result.allowed is False
    assert "active_database_path" in result.blocked_reasons


def test_privacy_cleanup_write_guard_blocks_protected_project_files(tmp_path) -> None:
    result = _guard(
        tmp_path,
        target_path=tmp_path / "requirements.txt",
        allowed_base_path=tmp_path,
    )

    assert result.allowed is False
    assert "protected_project_file" in result.blocked_reasons


def test_privacy_cleanup_write_guard_has_safe_flags(tmp_path) -> None:
    result = _guard(tmp_path)

    assert result.preview_required is True
    assert result.token_required is True
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
    assert result.write_performed is False


def test_privacy_cleanup_write_guard_does_not_write_files(tmp_path) -> None:
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = _guard(tmp_path)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert result.allowed is True
    assert before == after
