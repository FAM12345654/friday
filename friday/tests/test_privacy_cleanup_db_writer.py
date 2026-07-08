"""Tests for the guarded SQLite privacy cleanup writer."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sqlite3

from friday.app.privacy_cleanup_db_guard import check_privacy_cleanup_db_write_allowed
from friday.app.privacy_cleanup_db_preview import (
    CONTACT_DB_CLEANUP_TOKEN,
    REVIEW_DB_CLEANUP_TOKEN,
    build_privacy_cleanup_db_preview,
)
from friday.app.privacy_cleanup_db_writer import apply_privacy_cleanup_db_write
from friday.storage.database import setup_local_database

from friday.tests.test_privacy_cleanup_db_preview import (
    _insert_contact_context,
    _insert_review_candidates,
)


def _db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)
    return db_path


def _count(db_path: Path, table_name: str, where_sql: str = "1 = 1") -> int:
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            f"SELECT COUNT(*) FROM {table_name} WHERE {where_sql}"
        ).fetchone()
    return int(row[0])


def _review_guard(db_path: Path):
    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Review-History",),
    )
    return check_privacy_cleanup_db_write_allowed(
        cleanup_area="Review-History",
        preview=preview,
        approval_token=REVIEW_DB_CLEANUP_TOKEN,
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )


def _contact_guard(db_path: Path, contact_id: str):
    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Kontakt-Kontext",),
        contact_id=contact_id,
    )
    return check_privacy_cleanup_db_write_allowed(
        cleanup_area="Kontakt-Kontext",
        preview=preview,
        approval_token=CONTACT_DB_CLEANUP_TOKEN,
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )


def test_db_writer_deletes_only_safe_review_history_candidates(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_review_candidates(db_path)
    guard = _review_guard(db_path)

    result = apply_privacy_cleanup_db_write(
        db_path=db_path,
        guard_result=guard,
    )

    assert result.allowed is True
    assert result.deleted_counts == {
        "message_suggestions": 1,
        "task_suggestions": 1,
    }
    assert result.transaction_used is True
    assert result.rollback_performed is False
    assert _count(db_path, "message_suggestions", "status = 'rejected'") == 0
    assert _count(db_path, "task_suggestions", "status = 'converted'") == 0
    assert _count(db_path, "message_suggestions", "status = 'pending'") == 1
    assert _count(db_path, "task_suggestions", "status = 'pending'") == 1
    assert _count(db_path, "tasks", "title = 'Konvertierte Aufgabe'") == 1


def test_db_writer_deletes_only_selected_contact_context(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_contact_context(db_path, "contact-01")
    _insert_contact_context(db_path, "contact-02")
    guard = _contact_guard(db_path, "contact-01")

    result = apply_privacy_cleanup_db_write(
        db_path=db_path,
        guard_result=guard,
        contact_id="contact-01",
    )

    assert result.allowed is True
    assert result.deleted_counts == {"contact_contexts": 1}
    assert _count(db_path, "contact_contexts", "contact_id = 'contact-01'") == 0
    assert _count(db_path, "contact_contexts", "contact_id = 'contact-02'") == 1


def test_db_writer_blocks_when_guard_is_not_allowed(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_review_candidates(db_path)
    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Review-History",),
    )
    guard = check_privacy_cleanup_db_write_allowed(
        cleanup_area="Review-History",
        preview=preview,
        approval_token="JA",
        backup_available=True,
        transaction_available=True,
        rollback_available=True,
        scanner_smoke_passed=True,
    )

    result = apply_privacy_cleanup_db_write(
        db_path=db_path,
        guard_result=guard,
    )

    assert result.allowed is False
    assert "invalid_token" in result.blocked_reasons
    assert result.delete_performed is False
    assert _count(db_path, "message_suggestions", "status = 'rejected'") == 1


def test_db_writer_blocks_contact_without_selection(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_contact_context(db_path, "contact-01")
    guard = _contact_guard(db_path, "contact-01")

    result = apply_privacy_cleanup_db_write(
        db_path=db_path,
        guard_result=guard,
    )

    assert result.allowed is False
    assert result.blocked_reasons == ("missing_contact_selection",)
    assert _count(db_path, "contact_contexts", "contact_id = 'contact-01'") == 1


def test_db_writer_rolls_back_on_candidate_count_mismatch(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_review_candidates(db_path)
    guard = replace(_review_guard(db_path), candidate_count=99)

    result = apply_privacy_cleanup_db_write(
        db_path=db_path,
        guard_result=guard,
    )

    assert result.allowed is False
    assert result.blocked_reasons == ("candidate_count_mismatch",)
    assert result.transaction_used is True
    assert result.rollback_performed is True
    assert _count(db_path, "message_suggestions", "status = 'rejected'") == 1
    assert _count(db_path, "task_suggestions", "status = 'converted'") == 1


def test_db_writer_reports_safe_side_effect_flags(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_review_candidates(db_path)
    guard = _review_guard(db_path)

    result = apply_privacy_cleanup_db_write(
        db_path=db_path,
        guard_result=guard,
    )

    assert result.schema_changed is False
    assert result.external_action_used is False
    assert result.sensitive_content_returned is False
    assert result.write_performed is True
    assert result.delete_performed is True
