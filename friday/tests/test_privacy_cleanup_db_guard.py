"""Tests for the side-effect-free SQLite privacy cleanup guard."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from friday.app.privacy_cleanup_db_guard import check_privacy_cleanup_db_write_allowed
from friday.app.privacy_cleanup_db_preview import (
    CONTACT_DB_CLEANUP_TOKEN,
    REVIEW_DB_CLEANUP_TOKEN,
    PrivacyCleanupDBPreview,
    build_privacy_cleanup_db_preview,
)
from friday.storage.database import setup_local_database

from friday.tests.test_privacy_cleanup_db_preview import (
    _insert_contact_context,
    _insert_review_candidates,
)


def _db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)
    return db_path


def _review_preview(tmp_path: Path) -> PrivacyCleanupDBPreview:
    db_path = _db_path(tmp_path)
    _insert_review_candidates(db_path)
    return build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Review-History",),
    )


def _contact_preview(tmp_path: Path) -> PrivacyCleanupDBPreview:
    db_path = _db_path(tmp_path)
    _insert_contact_context(db_path, "contact-01")
    return build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Kontakt-Kontext",),
        contact_id="contact-01",
    )


def _guard(
    preview: PrivacyCleanupDBPreview | None,
    *,
    cleanup_area: str = "Review-History",
    approval_token: str | None = REVIEW_DB_CLEANUP_TOKEN,
    backup_available: bool = True,
    transaction_available: bool = True,
    rollback_available: bool = True,
    scanner_smoke_passed: bool = True,
    external_actions_enabled: bool = False,
):
    return check_privacy_cleanup_db_write_allowed(
        cleanup_area=cleanup_area,
        preview=preview,
        approval_token=approval_token,
        backup_available=backup_available,
        transaction_available=transaction_available,
        rollback_available=rollback_available,
        scanner_smoke_passed=scanner_smoke_passed,
        external_actions_enabled=external_actions_enabled,
    )


def test_db_guard_allows_safe_review_preview(tmp_path: Path) -> None:
    result = _guard(_review_preview(tmp_path))

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert result.required_token == REVIEW_DB_CLEANUP_TOKEN
    assert result.candidate_count == 2


def test_db_guard_allows_safe_contact_preview(tmp_path: Path) -> None:
    result = _guard(
        _contact_preview(tmp_path),
        cleanup_area="Kontakt-Kontext",
        approval_token=CONTACT_DB_CLEANUP_TOKEN,
    )

    assert result.allowed is True
    assert result.blocked_reasons == ()
    assert result.required_token == CONTACT_DB_CLEANUP_TOKEN
    assert result.candidate_count == 1


def test_db_guard_blocks_missing_preview() -> None:
    result = _guard(None)

    assert result.allowed is False
    assert "missing_preview" in result.blocked_reasons


def test_db_guard_blocks_unknown_area(tmp_path: Path) -> None:
    result = _guard(
        _review_preview(tmp_path),
        cleanup_area="Aufgaben",
        approval_token="REVIEW AUFRAEUMEN",
    )

    assert result.allowed is False
    assert "unknown_cleanup_area" in result.blocked_reasons
    assert "preview_item_not_found" in result.blocked_reasons


def test_db_guard_blocks_invalid_tokens(tmp_path: Path) -> None:
    preview = _review_preview(tmp_path)

    for token in (None, "", "ja", "JA", " REVIEW AUFRAEUMEN "):
        result = _guard(preview, approval_token=token)

        assert result.allowed is False
        assert "invalid_token" in result.blocked_reasons


def test_db_guard_blocks_missing_backup_transaction_and_rollback(tmp_path: Path) -> None:
    result = _guard(
        _review_preview(tmp_path),
        backup_available=False,
        transaction_available=False,
        rollback_available=False,
    )

    assert result.allowed is False
    assert "missing_backup" in result.blocked_reasons
    assert "transaction_unavailable" in result.blocked_reasons
    assert "rollback_unavailable" in result.blocked_reasons


def test_db_guard_blocks_scanner_failure_and_external_actions(tmp_path: Path) -> None:
    result = _guard(
        _review_preview(tmp_path),
        scanner_smoke_passed=False,
        external_actions_enabled=True,
    )

    assert result.allowed is False
    assert "scanner_smoke_failed" in result.blocked_reasons
    assert "external_actions_enabled" in result.blocked_reasons


def test_db_guard_blocks_preview_item_blocked(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Kontakt-Kontext",),
    )

    result = _guard(
        preview,
        cleanup_area="Kontakt-Kontext",
        approval_token=CONTACT_DB_CLEANUP_TOKEN,
    )

    assert result.allowed is False
    assert "preview_item_blocked" in result.blocked_reasons


def test_db_guard_blocks_unsafe_scope_from_preview(tmp_path: Path) -> None:
    preview = _review_preview(tmp_path)
    unsafe_item = replace(
        preview.items[0],
        status_filter="status != pending",
    )
    unsafe_preview = replace(preview, items=(unsafe_item,))

    result = _guard(unsafe_preview)

    assert result.allowed is False
    assert "unsafe_status_filter" in result.blocked_reasons


def test_db_guard_blocks_when_sensitive_content_is_not_hidden(tmp_path: Path) -> None:
    preview = _review_preview(tmp_path)
    unsafe_item = replace(
        preview.items[0],
        sensitive_content_hidden=False,
    )
    unsafe_preview = replace(preview, items=(unsafe_item,))

    result = _guard(unsafe_preview)

    assert result.allowed is False
    assert "sensitive_content_not_hidden" in result.blocked_reasons


def test_db_guard_blocks_zero_candidate_write(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Review-History",),
    )

    result = _guard(preview)

    assert result.allowed is False
    assert "no_cleanup_candidates" in result.blocked_reasons


def test_db_guard_has_safe_side_effect_flags(tmp_path: Path) -> None:
    result = _guard(_review_preview(tmp_path))

    assert result.preview_required is True
    assert result.backup_required is True
    assert result.transaction_required is True
    assert result.rollback_required is True
    assert result.token_required is True
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_action_used is False
    assert result.write_performed is False
    assert result.delete_performed is False
    assert result.schema_changed is False
