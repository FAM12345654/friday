"""Guarded local data import apply writer prototype.

This module performs a limited local import only when the side-effect-free
import apply write guard has already allowed it. It does not replace the active
database file, perform restore operations, call providers, or use external
services.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any, Literal, Mapping

from friday.app.contact_context_preview import normalize_contact_name, normalize_contact_type
from friday.app.contact_context_save_guard import check_contact_context_fields_for_save
from friday.app.local_data_import_apply_write_guard import (
    LocalDataImportApplyWriteGuardResult,
)
from friday.storage.database import get_connection


LocalDataImportApplyWriterStatus = Literal[
    "applied",
    "blocked",
    "rolled_back",
    "invalid",
]

LocalDataImportApplyWriterBlockReason = Literal[
    "guard_blocked",
    "missing_export_file",
    "invalid_export_payload",
    "task_conflict",
    "contact_conflict",
    "sensitive_contact_context",
    "database_error",
]


@dataclass(frozen=True)
class LocalDataImportApplyWriteCounts:
    """Counts for one local import section."""

    tasks: int = 0
    contact_contexts: int = 0
    review_suggestions: int = 0


@dataclass(frozen=True)
class LocalDataImportApplyWriterResult:
    """Structured result for a guarded local import apply attempt."""

    applied: bool
    status: LocalDataImportApplyWriterStatus
    created_counts: LocalDataImportApplyWriteCounts
    skipped_counts: LocalDataImportApplyWriteCounts
    blocked_reasons: tuple[LocalDataImportApplyWriterBlockReason, ...]
    message: str
    rollback_used: bool
    preview_only: bool
    persisted: bool
    external_action_used: bool
    database_schema_changed: bool


def _read_json_list(export_root: Path, relative_path: str) -> list[Mapping[str, Any]]:
    path = export_root / relative_path
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(relative_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(relative_path)
    if not all(isinstance(item, dict) for item in payload):
        raise ValueError(relative_path)
    return payload


def _normalize_task(item: Mapping[str, Any]) -> dict[str, Any]:
    title = str(item.get("title") or "").strip()
    if not title:
        raise ValueError("task_title")
    return {
        "title": title,
        "category": str(item.get("category") or "other").strip() or "other",
        "status": str(item.get("status") or "open").strip() or "open",
        "due_date": (str(item.get("due_date")).strip() if item.get("due_date") is not None else None) or None,
        "notes": "" if item.get("notes") is None else str(item.get("notes")),
        "priority": str(item.get("priority") or "normal").strip().lower() or "normal",
    }


def _normalize_contact_context(item: Mapping[str, Any]) -> dict[str, Any]:
    contact_id = str(item.get("contact_id") or "").strip()
    display_name = str(item.get("display_name") or "").strip()
    contact_type = normalize_contact_type(str(item.get("contact_type") or "other"))
    relationship_context = (
        str(item.get("relationship_context")).strip()
        if item.get("relationship_context") is not None
        else None
    ) or None
    if not contact_id or not display_name:
        raise ValueError("contact_context")
    guard = check_contact_context_fields_for_save(relationship_context=relationship_context)
    if not guard.allowed:
        raise PermissionError("sensitive_contact_context")
    return {
        "contact_id": contact_id,
        "display_name": display_name,
        "normalized_name": normalize_contact_name(display_name),
        "contact_type": contact_type,
        "nickname": (str(item.get("nickname")).strip() if item.get("nickname") is not None else None) or None,
        "relationship_context": relationship_context,
        "source_context": str(item.get("source_context") or "local_data_import").strip()
        or "local_data_import",
        "user_approved_persistence": 1,
        "sensitivity_checked": 1,
        "created_at": str(item.get("updated_at") or "2026-07-07T00:00:00+00:00"),
        "updated_at": str(item.get("updated_at") or "2026-07-07T00:00:00+00:00"),
    }


def _normalize_review_suggestion(item: Mapping[str, Any]) -> dict[str, Any] | None:
    suggestion_id = item.get("suggestion_id", item.get("id"))
    if suggestion_id is None:
        return None
    status = str(item.get("status") or "").strip().lower()
    if not status:
        return None
    return {
        "id": int(suggestion_id),
        "message_id": int(item.get("message_id") or int(suggestion_id)),
        "suggestion_type": str(item.get("type") or item.get("suggestion_type") or "imported").strip()
        or "imported",
        "draft_text": str(item.get("title") or item.get("draft_text") or "Importierter Vorschlag").strip()
        or "Importierter Vorschlag",
        "status": status if status in {"pending", "approved", "rejected", "edited"} else "pending",
        "notes": str(item.get("source") or "local_data_import"),
        "created_at": "2026-07-07T00:00:00+00:00",
        "updated_at": "2026-07-07T00:00:00+00:00",
    }


def _task_is_identical(existing: sqlite3.Row, task: Mapping[str, Any]) -> bool:
    return all(
        (existing[key] or None) == (task[key] or None)
        for key in ("title", "category", "status", "due_date", "notes", "priority")
    )


def _apply_tasks(connection: sqlite3.Connection, items: list[Mapping[str, Any]]) -> tuple[int, int]:
    created = 0
    skipped = 0
    for item in items:
        task = _normalize_task(item)
        existing = connection.execute(
            """
            SELECT title, category, status, due_date, notes, priority
            FROM tasks
            WHERE LOWER(title) = LOWER(?)
            LIMIT 1
            """,
            (task["title"],),
        ).fetchone()
        if existing is not None:
            if _task_is_identical(existing, task):
                skipped += 1
                continue
            raise RuntimeError("task_conflict")
        connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES (:title, :category, :status, :due_date, :notes, :priority)
            """,
            task,
        )
        created += 1
    return created, skipped


def _apply_contact_contexts(
    connection: sqlite3.Connection,
    items: list[Mapping[str, Any]],
) -> tuple[int, int]:
    created = 0
    skipped = 0
    for item in items:
        contact = _normalize_contact_context(item)
        existing = connection.execute(
            """
            SELECT contact_id, display_name, normalized_name, contact_type, source_context
            FROM contact_contexts
            WHERE contact_id = ?
            LIMIT 1
            """,
            (contact["contact_id"],),
        ).fetchone()
        if existing is not None:
            same_core = (
                existing["display_name"] == contact["display_name"]
                and existing["normalized_name"] == contact["normalized_name"]
                and existing["contact_type"] == contact["contact_type"]
                and existing["source_context"] == contact["source_context"]
            )
            if same_core:
                skipped += 1
                continue
            raise RuntimeError("contact_conflict")
        connection.execute(
            """
            INSERT INTO contact_contexts (
                contact_id,
                display_name,
                normalized_name,
                contact_type,
                nickname,
                relationship_context,
                source_context,
                user_approved_persistence,
                sensitivity_checked,
                created_at,
                updated_at
            ) VALUES (
                :contact_id,
                :display_name,
                :normalized_name,
                :contact_type,
                :nickname,
                :relationship_context,
                :source_context,
                :user_approved_persistence,
                :sensitivity_checked,
                :created_at,
                :updated_at
            )
            """,
            contact,
        )
        created += 1
    return created, skipped


def _apply_review_suggestions(
    connection: sqlite3.Connection,
    items: list[Mapping[str, Any]],
) -> tuple[int, int]:
    created = 0
    skipped = 0
    for item in items:
        suggestion = _normalize_review_suggestion(item)
        if suggestion is None:
            continue
        existing = connection.execute(
            """
            SELECT id, status
            FROM message_suggestions
            WHERE id = ?
            LIMIT 1
            """,
            (suggestion["id"],),
        ).fetchone()
        if existing is not None:
            skipped += 1
            continue
        connection.execute(
            """
            INSERT INTO message_suggestions (
                id,
                message_id,
                suggestion_type,
                draft_text,
                status,
                notes,
                created_at,
                updated_at
            ) VALUES (
                :id,
                :message_id,
                :suggestion_type,
                :draft_text,
                :status,
                :notes,
                :created_at,
                :updated_at
            )
            """,
            suggestion,
        )
        created += 1
    return created, skipped


def apply_local_data_import(
    *,
    guard_result: LocalDataImportApplyWriteGuardResult,
    export_root: str | Path,
    db_path: str | Path,
) -> LocalDataImportApplyWriterResult:
    """Apply allowed local import summary data into a local SQLite database."""

    if not guard_result.allowed:
        return LocalDataImportApplyWriterResult(
            applied=False,
            status="blocked",
            created_counts=LocalDataImportApplyWriteCounts(),
            skipped_counts=LocalDataImportApplyWriteCounts(),
            blocked_reasons=("guard_blocked",),
            message=guard_result.message or "Import-Apply wurde nicht freigegeben.",
            rollback_used=False,
            preview_only=False,
            persisted=False,
            external_action_used=False,
            database_schema_changed=False,
        )

    root = Path(export_root)
    try:
        task_items = _read_json_list(root, "tasks/tasks.json") if "tasks" in guard_result.write_scope else []
        contact_items = (
            _read_json_list(root, "contacts/contact_contexts.json")
            if "contact_contexts" in guard_result.write_scope
            else []
        )
        review_items = (
            _read_json_list(root, "review/review_suggestions.json")
            if "review_suggestions" in guard_result.write_scope
            else []
        )
    except FileNotFoundError:
        return LocalDataImportApplyWriterResult(
            applied=False,
            status="invalid",
            created_counts=LocalDataImportApplyWriteCounts(),
            skipped_counts=LocalDataImportApplyWriteCounts(),
            blocked_reasons=("missing_export_file",),
            message="Import-Apply wurde blockiert, weil eine Exportdatei fehlt.",
            rollback_used=False,
            preview_only=False,
            persisted=False,
            external_action_used=False,
            database_schema_changed=False,
        )
    except (json.JSONDecodeError, ValueError):
        return LocalDataImportApplyWriterResult(
            applied=False,
            status="invalid",
            created_counts=LocalDataImportApplyWriteCounts(),
            skipped_counts=LocalDataImportApplyWriteCounts(),
            blocked_reasons=("invalid_export_payload",),
            message="Import-Apply wurde blockiert, weil Exportdaten ungueltig sind.",
            rollback_used=False,
            preview_only=False,
            persisted=False,
            external_action_used=False,
            database_schema_changed=False,
        )

    try:
        with get_connection(db_path) as connection:
            task_created, task_skipped = _apply_tasks(connection, task_items)
            contact_created, contact_skipped = _apply_contact_contexts(connection, contact_items)
            review_created, review_skipped = _apply_review_suggestions(connection, review_items)
    except PermissionError:
        return LocalDataImportApplyWriterResult(
            applied=False,
            status="blocked",
            created_counts=LocalDataImportApplyWriteCounts(),
            skipped_counts=LocalDataImportApplyWriteCounts(),
            blocked_reasons=("sensitive_contact_context",),
            message="Import-Apply wurde wegen sensibler Kontakt-Daten blockiert.",
            rollback_used=True,
            preview_only=False,
            persisted=False,
            external_action_used=False,
            database_schema_changed=False,
        )
    except RuntimeError as error:
        reason = str(error)
        if reason not in {"task_conflict", "contact_conflict"}:
            reason = "database_error"
        return LocalDataImportApplyWriterResult(
            applied=False,
            status="rolled_back",
            created_counts=LocalDataImportApplyWriteCounts(),
            skipped_counts=LocalDataImportApplyWriteCounts(),
            blocked_reasons=(reason,),  # type: ignore[arg-type]
            message="Import-Apply wurde zurueckgerollt.",
            rollback_used=True,
            preview_only=False,
            persisted=False,
            external_action_used=False,
            database_schema_changed=False,
        )
    except sqlite3.DatabaseError:
        return LocalDataImportApplyWriterResult(
            applied=False,
            status="rolled_back",
            created_counts=LocalDataImportApplyWriteCounts(),
            skipped_counts=LocalDataImportApplyWriteCounts(),
            blocked_reasons=("database_error",),
            message="Import-Apply wurde wegen eines Datenbankfehlers zurueckgerollt.",
            rollback_used=True,
            preview_only=False,
            persisted=False,
            external_action_used=False,
            database_schema_changed=False,
        )

    return LocalDataImportApplyWriterResult(
        applied=True,
        status="applied",
        created_counts=LocalDataImportApplyWriteCounts(
            tasks=task_created,
            contact_contexts=contact_created,
            review_suggestions=review_created,
        ),
        skipped_counts=LocalDataImportApplyWriteCounts(
            tasks=task_skipped,
            contact_contexts=contact_skipped,
            review_suggestions=review_skipped,
        ),
        blocked_reasons=(),
        message="Import-Apply wurde lokal angewendet.",
        rollback_used=False,
        preview_only=False,
        persisted=True,
        external_action_used=False,
        database_schema_changed=False,
    )
