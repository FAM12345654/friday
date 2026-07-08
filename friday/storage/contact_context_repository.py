"""Repository for local contact context preview rows."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import sqlite3

from friday.app.contact_context_save_guard import (
    CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE,
    check_contact_context_fields_for_save,
)
from friday.app.contact_context_preview import ContactType, normalize_contact_name, normalize_contact_type
from friday.storage.database import get_connection


def _now_iso_timestamp() -> str:
    """Return an UTC timestamp for local record metadata."""
    return datetime.now(timezone.utc).isoformat()


def _to_int_bool(value: bool | int) -> int:
    """Normalize a boolean-like value for sqlite integer flags."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int) and value in (0, 1):
        return value
    raise ValueError("Ein boolscher Wert ist nur mit 0 oder 1 erlaubt.")


def _normalize_contact_type(contact_type: str | None) -> str:
    """Return a stable persisted contact type."""
    return normalize_contact_type(contact_type)


class ContactContextRepository:
    """Local preview storage for discovered contact contexts."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path

    def create_contact_context(
        self,
        contact_id: str,
        display_name: str,
        contact_type: str | None = None,
        nickname: str | None = None,
        relationship_context: str | None = None,
        source_context: str = "manuell",
        user_approved_persistence: bool | int = False,
        sensitivity_checked: bool | int = False,
    ) -> dict:
        """Create a preview contact context unless it already exists."""
        normalized_contact_id = (contact_id or "").strip()
        if not normalized_contact_id:
            raise ValueError("Kontakt-ID wird benötigt.")

        normalized_display_name = (display_name or "").strip()
        if not normalized_display_name:
            raise ValueError("Anzeige-Name darf nicht leer sein.")

        normalized_name = normalize_contact_name(normalized_display_name)
        normalized_contact_type: ContactType = _normalize_contact_type(contact_type)
        normalized_source_context = (source_context or "").strip() or "manuell"
        normalized_relationship_context = (relationship_context or "").strip() or None
        guard_result = check_contact_context_fields_for_save(
            relationship_context=normalized_relationship_context,
        )
        if not guard_result.allowed:
            raise ValueError(CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE)

        now = _now_iso_timestamp()

        with get_connection(self.db_path) as connection:
            existing = connection.execute(
                """
                SELECT
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
                FROM contact_contexts
                WHERE contact_id = ?
                LIMIT 1
                """,
                (normalized_contact_id,),
            ).fetchone()
            if existing is not None:
                return dict(existing)

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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized_contact_id,
                    normalized_display_name,
                    normalized_name,
                    normalized_contact_type,
                    (nickname or "").strip() or None,
                    normalized_relationship_context,
                    normalized_source_context,
                    _to_int_bool(user_approved_persistence),
                    _to_int_bool(sensitivity_checked),
                    now,
                    now,
                ),
            )

            return dict(
                connection.execute(
                    """
                    SELECT
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
                    FROM contact_contexts
                    WHERE contact_id = ?
                    """,
                    (normalized_contact_id,),
                ).fetchone(),
            )

    def get_contact_context(self, contact_id: str) -> dict | None:
        """Return one contact context by id."""
        normalized_contact_id = (contact_id or "").strip()
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT
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
                FROM contact_contexts
                WHERE contact_id = ?
                LIMIT 1
                """,
                (normalized_contact_id,),
            ).fetchone()
            return dict(row) if row is not None else None

    def find_contact_by_normalized_name(self, normalized_name: str) -> dict | None:
        """Find a contact context by normalized display name."""
        normalized_key = normalize_contact_name(normalized_name)
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT
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
                FROM contact_contexts
                WHERE normalized_name = ?
                LIMIT 1
                """,
                (normalized_key,),
            ).fetchone()
            return dict(row) if row is not None else None

    def list_contact_contexts(self) -> list[dict]:
        """Return all local contact contexts."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT
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
                FROM contact_contexts
                ORDER BY normalized_name, display_name
                """,
            ).fetchall()
            return [dict(row) for row in rows]

    def update_contact_context(
        self,
        contact_id: str,
        display_name: str | None = None,
        contact_type: ContactType | None = None,
        nickname: str | None = None,
        relationship_context: str | None = None,
        source_context: str | None = None,
        user_approved_persistence: bool | int | None = None,
        sensitivity_checked: bool | int | None = None,
    ) -> dict | None:
        """Update an existing local contact context."""
        normalized_contact_id = (contact_id or "").strip()
        if not normalized_contact_id:
            return None

        updates: list[str] = []
        params: dict[str, object] = {"contact_id": normalized_contact_id, "updated_at": _now_iso_timestamp()}

        if display_name is not None:
            normalized_display_name = (display_name or "").strip()
            if not normalized_display_name:
                raise ValueError("Anzeige-Name darf nicht leer sein.")
            updates.extend(
                [
                    "display_name = :display_name",
                    "normalized_name = :normalized_name",
                ]
            )
            params["display_name"] = normalized_display_name
            params["normalized_name"] = normalize_contact_name(normalized_display_name)

        if contact_type is not None:
            updates.append("contact_type = :contact_type")
            params["contact_type"] = _normalize_contact_type(contact_type)

        if nickname is not None:
            updates.append("nickname = :nickname")
            params["nickname"] = (nickname or "").strip() or None

        if relationship_context is not None:
            guard_result = check_contact_context_fields_for_save(
                relationship_context=(relationship_context or "").strip() or None,
            )
            if not guard_result.allowed:
                raise ValueError(CONTACT_CONTEXT_SAVE_BLOCKED_MESSAGE)
            updates.append("relationship_context = :relationship_context")
            params["relationship_context"] = (relationship_context or "").strip() or None

        if source_context is not None:
            updates.append("source_context = :source_context")
            params["source_context"] = (source_context or "").strip() or "manuell"

        if user_approved_persistence is not None:
            updates.append("user_approved_persistence = :user_approved_persistence")
            params["user_approved_persistence"] = _to_int_bool(user_approved_persistence)

        if sensitivity_checked is not None:
            updates.append("sensitivity_checked = :sensitivity_checked")
            params["sensitivity_checked"] = _to_int_bool(sensitivity_checked)

        if not updates:
            return self.get_contact_context(normalized_contact_id)

        updates.append("updated_at = :updated_at")
        updates_sql = ", ".join(updates)

        with get_connection(self.db_path) as connection:
            if connection.execute(
                "SELECT 1 FROM contact_contexts WHERE contact_id = ? LIMIT 1",
                (normalized_contact_id,),
            ).fetchone() is None:
                return None

            connection.execute(
                f"UPDATE contact_contexts SET {updates_sql} WHERE contact_id = :contact_id",
                params,
            )

            row = connection.execute(
                """
                SELECT
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
                FROM contact_contexts
                WHERE contact_id = ?
                LIMIT 1
                """,
                (normalized_contact_id,),
            ).fetchone()
            return dict(row) if row is not None else None

    def delete_contact_context(self, contact_id: str) -> bool:
        """Delete one contact context."""
        normalized_contact_id = (contact_id or "").strip()
        if not normalized_contact_id:
            return False

        with get_connection(self.db_path) as connection:
            cursor = connection.execute(
                "DELETE FROM contact_contexts WHERE contact_id = ?",
                (normalized_contact_id,),
            )
            return cursor.rowcount > 0
