"""Read-only SQLite cleanup preview model for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3


REVIEW_DB_CLEANUP_TOKEN = "REVIEW AUFRAEUMEN"
CONTACT_DB_CLEANUP_TOKEN = "KONTAKT LÖSCHEN"

ALLOWED_DB_PREVIEW_AREAS = {
    "Review-History",
    "Kontakt-Kontext",
}

BLOCKED_DB_PREVIEW_AREAS = {
    "Aufgaben": "task_cleanup_requires_separate_gate",
    "Nachrichten": "message_cleanup_requires_separate_gate",
    "Kalender": "calendar_cleanup_requires_separate_gate",
    "aktive SQLite-DB": "active_database_blocked",
    "Datenbankschema": "schema_cleanup_blocked",
    "unbekannte Tabellen": "unknown_tables_blocked",
}


@dataclass(frozen=True)
class PrivacyCleanupDBPreviewItem:
    """One read-only SQLite cleanup candidate."""

    area_name: str
    table_name: str
    status_filter: str
    candidate_count: int
    preview_status: str
    allowed: bool
    blocked_reasons: tuple[str, ...]
    requires_token: str
    backup_required: bool
    transaction_required: bool
    rollback_required: bool
    sensitive_content_hidden: bool


@dataclass(frozen=True)
class PrivacyCleanupDBPreview:
    """Side-effect-free SQLite cleanup preview result."""

    items: tuple[PrivacyCleanupDBPreviewItem, ...]
    blocked_actions: tuple[str, ...]
    writes_performed: bool
    deletes_performed: bool
    schema_changed: bool
    external_lookup_used: bool


def _connect_read_only(db_path: Path | str) -> sqlite3.Connection:
    path = Path(db_path).resolve()
    uri = f"{path.as_uri()}?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _count_rejected_message_suggestions(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM message_suggestions
        WHERE status = ?
        """,
        ("rejected",),
    ).fetchone()
    return int(row["count"])


def _count_converted_task_suggestions(connection: sqlite3.Connection) -> int:
    row = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM task_suggestions
        WHERE status = ?
          AND created_task_id IS NOT NULL
          AND EXISTS (
              SELECT 1
              FROM tasks
              WHERE tasks.id = task_suggestions.created_task_id
          )
        """,
        ("converted",),
    ).fetchone()
    return int(row["count"])


def _count_contact_context(connection: sqlite3.Connection, contact_id: str) -> int:
    row = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM contact_contexts
        WHERE contact_id = ?
        """,
        (contact_id,),
    ).fetchone()
    return int(row["count"])


def _review_history_item(connection: sqlite3.Connection) -> PrivacyCleanupDBPreviewItem:
    rejected_count = _count_rejected_message_suggestions(connection)
    converted_count = _count_converted_task_suggestions(connection)
    return PrivacyCleanupDBPreviewItem(
        area_name="Review-History",
        table_name="message_suggestions, task_suggestions",
        status_filter="message_suggestions.status = rejected; task_suggestions.status = converted",
        candidate_count=rejected_count + converted_count,
        preview_status="preview_only",
        allowed=True,
        blocked_reasons=(),
        requires_token=REVIEW_DB_CLEANUP_TOKEN,
        backup_required=True,
        transaction_required=True,
        rollback_required=True,
        sensitive_content_hidden=True,
    )


def _contact_context_item(
    connection: sqlite3.Connection,
    contact_id: str | None,
) -> PrivacyCleanupDBPreviewItem:
    if not contact_id or not contact_id.strip():
        return PrivacyCleanupDBPreviewItem(
            area_name="Kontakt-Kontext",
            table_name="contact_contexts",
            status_filter="contact_id = <nicht ausgewaehlt>",
            candidate_count=0,
            preview_status="blocked",
            allowed=False,
            blocked_reasons=("missing_contact_selection",),
            requires_token=CONTACT_DB_CLEANUP_TOKEN,
            backup_required=True,
            transaction_required=True,
            rollback_required=True,
            sensitive_content_hidden=True,
        )

    selected_contact_id = contact_id.strip()
    return PrivacyCleanupDBPreviewItem(
        area_name="Kontakt-Kontext",
        table_name="contact_contexts",
        status_filter="contact_id = <ausgewaehlt>",
        candidate_count=_count_contact_context(connection, selected_contact_id),
        preview_status="preview_only",
        allowed=True,
        blocked_reasons=(),
        requires_token=CONTACT_DB_CLEANUP_TOKEN,
        backup_required=True,
        transaction_required=True,
        rollback_required=True,
        sensitive_content_hidden=True,
    )


def _blocked_item(area_name: str, reason: str) -> PrivacyCleanupDBPreviewItem:
    return PrivacyCleanupDBPreviewItem(
        area_name=area_name,
        table_name="nicht freigegeben",
        status_filter="nicht freigegeben",
        candidate_count=0,
        preview_status="blocked",
        allowed=False,
        blocked_reasons=(reason,),
        requires_token="nicht freigegeben",
        backup_required=False,
        transaction_required=False,
        rollback_required=False,
        sensitive_content_hidden=True,
    )


def build_privacy_cleanup_db_preview(
    *,
    db_path: Path | str,
    requested_areas: tuple[str, ...] | None = None,
    contact_id: str | None = None,
) -> PrivacyCleanupDBPreview:
    """Build a read-only SQLite cleanup preview.

    This function opens SQLite in read-only mode. It counts known safe cleanup
    candidates and never writes, deletes, migrates, or calls external services.
    """

    area_order = requested_areas or ("Review-History", "Kontakt-Kontext")
    items: list[PrivacyCleanupDBPreviewItem] = []
    blocked_actions: list[str] = []

    with _connect_read_only(db_path) as connection:
        for area_name in area_order:
            if area_name == "Review-History":
                items.append(_review_history_item(connection))
                continue

            if area_name == "Kontakt-Kontext":
                item = _contact_context_item(connection, contact_id)
                items.append(item)
                blocked_actions.extend(item.blocked_reasons)
                continue

            reason = BLOCKED_DB_PREVIEW_AREAS.get(area_name, "missing_future_gate")
            blocked_actions.append(reason)
            items.append(_blocked_item(area_name, reason))

    return PrivacyCleanupDBPreview(
        items=tuple(items),
        blocked_actions=tuple(dict.fromkeys(blocked_actions)),
        writes_performed=False,
        deletes_performed=False,
        schema_changed=False,
        external_lookup_used=False,
    )
