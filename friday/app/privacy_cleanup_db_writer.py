"""Guarded SQLite privacy cleanup writer for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from friday.app.privacy_cleanup_db_guard import PrivacyCleanupDBGuardResult


@dataclass(frozen=True)
class PrivacyCleanupDBWriterResult:
    """Result for a guarded SQLite privacy cleanup write."""

    allowed: bool
    cleanup_area: str
    deleted_counts: dict[str, int]
    blocked_reasons: tuple[str, ...]
    message: str | None
    transaction_used: bool
    rollback_performed: bool
    schema_changed: bool
    external_action_used: bool
    sensitive_content_returned: bool
    write_performed: bool
    delete_performed: bool


def _blocked_result(
    *,
    cleanup_area: str,
    blocked_reasons: tuple[str, ...],
    transaction_used: bool = False,
    rollback_performed: bool = False,
    deleted_counts: dict[str, int] | None = None,
) -> PrivacyCleanupDBWriterResult:
    return PrivacyCleanupDBWriterResult(
        allowed=False,
        cleanup_area=cleanup_area,
        deleted_counts=deleted_counts or {},
        blocked_reasons=blocked_reasons,
        message="SQLite Privacy Cleanup wurde nicht ausgefuehrt.",
        transaction_used=transaction_used,
        rollback_performed=rollback_performed,
        schema_changed=False,
        external_action_used=False,
        sensitive_content_returned=False,
        write_performed=False,
        delete_performed=False,
    )


def _allowed_result(
    *,
    cleanup_area: str,
    deleted_counts: dict[str, int],
    transaction_used: bool,
) -> PrivacyCleanupDBWriterResult:
    return PrivacyCleanupDBWriterResult(
        allowed=True,
        cleanup_area=cleanup_area,
        deleted_counts=deleted_counts,
        blocked_reasons=(),
        message=None,
        transaction_used=transaction_used,
        rollback_performed=False,
        schema_changed=False,
        external_action_used=False,
        sensitive_content_returned=False,
        write_performed=True,
        delete_performed=sum(deleted_counts.values()) > 0,
    )


def _delete_review_history(connection: sqlite3.Connection) -> dict[str, int]:
    message_cursor = connection.execute(
        """
        DELETE FROM message_suggestions
        WHERE status = ?
        """,
        ("rejected",),
    )
    task_cursor = connection.execute(
        """
        DELETE FROM task_suggestions
        WHERE status = ?
          AND created_task_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM tasks
              WHERE tasks.id = task_suggestions.created_task_id
          )
        """,
        ("converted",),
    )
    return {
        "message_suggestions": int(message_cursor.rowcount),
        "task_suggestions": int(task_cursor.rowcount),
    }


def _delete_contact_context(
    connection: sqlite3.Connection,
    contact_id: str,
) -> dict[str, int]:
    cursor = connection.execute(
        """
        DELETE FROM contact_contexts
        WHERE contact_id = ?
        """,
        (contact_id,),
    )
    return {"contact_contexts": int(cursor.rowcount)}


def apply_privacy_cleanup_db_write(
    *,
    db_path: Path | str,
    guard_result: PrivacyCleanupDBGuardResult,
    contact_id: str | None = None,
) -> PrivacyCleanupDBWriterResult:
    """Apply a guarded SQLite privacy cleanup write.

    This writer only supports known cleanup areas, only runs with an allowed
    guard result, uses an explicit transaction, and never changes schema or
    calls external services.
    """

    if not guard_result.allowed:
        return _blocked_result(
            cleanup_area=guard_result.cleanup_area,
            blocked_reasons=guard_result.blocked_reasons or ("guard_not_allowed",),
        )

    cleanup_area = guard_result.cleanup_area
    if cleanup_area not in ("Review-History", "Kontakt-Kontext"):
        return _blocked_result(
            cleanup_area=cleanup_area,
            blocked_reasons=("unsupported_cleanup_area",),
        )

    selected_contact_id = contact_id.strip() if contact_id else ""
    if cleanup_area == "Kontakt-Kontext" and not selected_contact_id:
        return _blocked_result(
            cleanup_area=cleanup_area,
            blocked_reasons=("missing_contact_selection",),
        )

    connection = sqlite3.connect(Path(db_path))
    transaction_started = False
    try:
        connection.execute("BEGIN")
        transaction_started = True

        if cleanup_area == "Review-History":
            deleted_counts = _delete_review_history(connection)
        else:
            deleted_counts = _delete_contact_context(connection, selected_contact_id)

        deleted_total = sum(deleted_counts.values())
        if deleted_total != guard_result.candidate_count:
            connection.rollback()
            return _blocked_result(
                cleanup_area=cleanup_area,
                blocked_reasons=("candidate_count_mismatch",),
                transaction_used=True,
                rollback_performed=True,
                deleted_counts=deleted_counts,
            )

        connection.commit()
        return _allowed_result(
            cleanup_area=cleanup_area,
            deleted_counts=deleted_counts,
            transaction_used=True,
        )
    except sqlite3.Error:
        if transaction_started:
            connection.rollback()
        return _blocked_result(
            cleanup_area=cleanup_area,
            blocked_reasons=("sqlite_error",),
            transaction_used=transaction_started,
            rollback_performed=transaction_started,
        )
    finally:
        connection.close()
