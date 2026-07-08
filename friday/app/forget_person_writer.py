"""Guarded local Forget Person writer for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from friday.app.forget_person_write_guard import ForgetPersonWriteGuardResult


@dataclass(frozen=True)
class ForgetPersonWriteResult:
    """Result of a guarded Forget Person write."""

    allowed: bool
    deleted_counts: dict[str, int]
    target_contact_ids: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    message: str | None
    transaction_used: bool
    rollback_performed: bool
    schema_changed: bool
    external_action_used: bool
    obsidian_write_performed: bool
    sensitive_content_returned: bool
    write_performed: bool
    delete_performed: bool


def _blocked_result(
    *,
    target_contact_ids: tuple[str, ...],
    blocked_reasons: tuple[str, ...],
    deleted_counts: dict[str, int] | None = None,
    transaction_used: bool = False,
    rollback_performed: bool = False,
) -> ForgetPersonWriteResult:
    return ForgetPersonWriteResult(
        allowed=False,
        deleted_counts=deleted_counts or {},
        target_contact_ids=target_contact_ids,
        blocked_reasons=blocked_reasons,
        message="Forget Person wurde nicht ausgefuehrt.",
        transaction_used=transaction_used,
        rollback_performed=rollback_performed,
        schema_changed=False,
        external_action_used=False,
        obsidian_write_performed=False,
        sensitive_content_returned=False,
        write_performed=False,
        delete_performed=False,
    )


def _allowed_result(
    *,
    target_contact_ids: tuple[str, ...],
    deleted_counts: dict[str, int],
) -> ForgetPersonWriteResult:
    return ForgetPersonWriteResult(
        allowed=True,
        deleted_counts=deleted_counts,
        target_contact_ids=target_contact_ids,
        blocked_reasons=(),
        message=None,
        transaction_used=True,
        rollback_performed=False,
        schema_changed=False,
        external_action_used=False,
        obsidian_write_performed=False,
        sensitive_content_returned=False,
        write_performed=True,
        delete_performed=sum(deleted_counts.values()) > 0,
    )


def _delete_contact_contexts(
    connection: sqlite3.Connection,
    contact_ids: tuple[str, ...],
) -> dict[str, int]:
    placeholders = ", ".join("?" for _ in contact_ids)
    cursor = connection.execute(
        f"""
        DELETE FROM contact_contexts
        WHERE contact_id IN ({placeholders})
        """,
        contact_ids,
    )
    return {"contact_contexts": int(cursor.rowcount)}


def apply_forget_person_write(
    *,
    db_path: Path | str,
    guard_result: ForgetPersonWriteGuardResult,
) -> ForgetPersonWriteResult:
    """Apply a guarded local Forget Person write.

    The writer only deletes guard-approved `contact_contexts` rows from the
    local SQLite database. It never writes Obsidian files, calls providers,
    changes schema, or deletes unrelated tables.
    """

    target_contact_ids = guard_result.target_contact_ids
    if not guard_result.allowed:
        return _blocked_result(
            target_contact_ids=target_contact_ids,
            blocked_reasons=guard_result.blocked_reasons or ("guard_not_allowed",),
        )

    if not target_contact_ids:
        return _blocked_result(
            target_contact_ids=target_contact_ids,
            blocked_reasons=("missing_guard_targets",),
        )

    resolved_db_path = Path(db_path)
    if not resolved_db_path.exists() or not resolved_db_path.is_file():
        return _blocked_result(
            target_contact_ids=target_contact_ids,
            blocked_reasons=("database_missing",),
        )

    connection = sqlite3.connect(resolved_db_path)
    transaction_started = False
    try:
        connection.execute("BEGIN")
        transaction_started = True
        deleted_counts = _delete_contact_contexts(connection, target_contact_ids)
        deleted_total = sum(deleted_counts.values())
        if deleted_total != guard_result.candidate_count:
            connection.rollback()
            return _blocked_result(
                target_contact_ids=target_contact_ids,
                blocked_reasons=("candidate_count_mismatch",),
                deleted_counts=deleted_counts,
                transaction_used=True,
                rollback_performed=True,
            )

        connection.commit()
        return _allowed_result(
            target_contact_ids=target_contact_ids,
            deleted_counts=deleted_counts,
        )
    except sqlite3.Error:
        if transaction_started:
            connection.rollback()
        return _blocked_result(
            target_contact_ids=target_contact_ids,
            blocked_reasons=("sqlite_error",),
            transaction_used=transaction_started,
            rollback_performed=transaction_started,
        )
    finally:
        connection.close()
