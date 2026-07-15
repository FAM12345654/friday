"""Repository layer for Friday local SQLite data."""

from __future__ import annotations

from pathlib import Path
from datetime import date, datetime, timedelta, timezone
import calendar
import hashlib
import json
import re
import sqlite3
from typing import Callable, List, Mapping

from friday.config import get_database_path
from friday.app.todo_relevance import determine_mail_relevance
from friday.storage.database import get_connection


VALID_PRIORITIES = {"low", "normal", "high", "urgent"}
VALID_RECURRENCES = {"taeglich", "woechentlich", "monatlich"}
VALID_SUGGESTION_STATUSES = {"pending", "approved", "rejected", "edited"}
VALID_TASK_SUGGESTION_STATUSES = {"pending", "approved", "rejected", "edited", "converted"}
VALID_CALENDAR_SUGGESTION_STATUSES = {"pending", "selected", "rejected"}
VALID_BLOCKED_SENDER_SOURCES = {"message", "ms_mail", "imap_mail", "whatsapp"}


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite row to a plain dictionary."""
    return dict(row)


def _to_minutes(time_iso: str) -> int:
    """Convert HH:MM into total minutes."""
    if ":" not in time_iso:
        return 0
    hours, minutes = map(int, time_iso.split(":"))
    return hours * 60 + minutes


def _to_time_string(minutes: int) -> str:
    """Format total minutes back to HH:MM."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _validate_priority(priority: str | None, default: str | None = None) -> str | None:
    """Validate and normalize optional task priority values."""
    if priority is None:
        return default
    normalized_priority = priority.strip().lower()
    if not normalized_priority:
        return default
    if normalized_priority not in VALID_PRIORITIES:
        raise ValueError("Ungültige Priorität. Erlaubt: low, normal, high, urgent.")
    return normalized_priority


def _validate_recurrence(recurrence: str | None, default: str | None = None) -> str | None:
    """Validate and normalize optional task recurrence values."""
    if recurrence is None:
        return default
    normalized_recurrence = recurrence.strip().lower()
    if not normalized_recurrence:
        return default
    if normalized_recurrence not in VALID_RECURRENCES:
        raise ValueError("Ungültige Wiederholung. Erlaubt: taeglich, woechentlich, monatlich.")
    return normalized_recurrence


def _add_month_clamped(date_iso: str) -> str:
    source = date.fromisoformat(date_iso)
    month = source.month + 1
    year = source.year
    if month > 12:
        month = 1
        year += 1
    last_day = calendar.monthrange(year, month)[1]
    return source.replace(year=year, month=month, day=min(source.day, last_day)).isoformat()


def _next_due_date(date_iso: str, recurrence: str) -> str:
    source = date.fromisoformat(date_iso)
    if recurrence == "taeglich":
        return (source + timedelta(days=1)).isoformat()
    if recurrence == "woechentlich":
        return (source + timedelta(days=7)).isoformat()
    return _add_month_clamped(date_iso)


def calculate_next_recurrence_due_date(date_iso: str, recurrence: str) -> str:
    """Return the next due date for a validated recurrence value."""
    normalized_recurrence = _validate_recurrence(recurrence)
    if normalized_recurrence is None:
        raise ValueError("Ungültige Wiederholung.")
    return _next_due_date(date_iso, normalized_recurrence)


def _validate_suggestion_status(status: str | None) -> str:
    """Validate suggestion status and normalize to lower case."""
    if status is None:
        raise ValueError("Ungültiger Vorschlagsstatus.")
    normalized = status.strip().lower()
    if not normalized or normalized not in VALID_SUGGESTION_STATUSES:
        raise ValueError("Ungültiger Vorschlagsstatus.")
    return normalized


def _validate_calendar_suggestion_status(status: str | None) -> str:
    """Validate calendar suggestion status and normalize to lower case."""
    if status is None:
        raise ValueError("Ungültiger Kalender-Vorschlagsstatus.")
    normalized = status.strip().lower()
    if not normalized or normalized not in VALID_CALENDAR_SUGGESTION_STATUSES:
        raise ValueError("Ungültiger Kalender-Vorschlagsstatus.")
    return normalized


def _validate_task_suggestion_status(status: str | None) -> str:
    """Validate task suggestion status and normalize to lower case."""
    if status is None:
        raise ValueError("Ungültiger Aufgaben-Vorschlagsstatus.")
    normalized = status.strip().lower()
    if not normalized or normalized not in VALID_TASK_SUGGESTION_STATUSES:
        raise ValueError("Ungültiger Aufgaben-Vorschlagsstatus.")
    return normalized


def _now_iso_timestamp() -> str:
    """Return a compact timestamp for local audit fields."""
    return datetime.now(timezone.utc).isoformat()


def _normalize_blocked_sender_source(source: str | None) -> str:
    """Normalize and validate a local message source name."""
    normalized_source = str(source or "").strip().lower()
    if normalized_source not in VALID_BLOCKED_SENDER_SOURCES:
        raise ValueError("Ungültige Nachrichtenquelle.")
    return normalized_source


def normalize_blocked_sender_key(source: str | None, sender: str | None) -> str:
    """Return a stable local key for one sender without contacting providers."""
    normalized_source = _normalize_blocked_sender_source(source)
    raw_sender = str(sender or "").strip()
    if normalized_source == "whatsapp":
        cleaned = raw_sender.lower()
        if re.fullmatch(r"[0-9a-f]{64}", cleaned):
            return cleaned
        if cleaned.startswith("hash:") and len(cleaned) > 5:
            return cleaned[5:]
        return hashlib.sha256((cleaned or "unknown").encode("utf-8")).hexdigest()

    if normalized_source in {"ms_mail", "imap_mail"}:
        match = re.search(r"[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+", raw_sender)
        if match:
            return match.group(0).strip().lower()

    return " ".join(raw_sender.casefold().split())


def _blocked_sender_label(source: str, sender: str | None) -> str:
    """Return a display-safe local label for a blocked sender."""
    text = str(sender or "").strip()
    if not text:
        return "Unbekannter Absender"
    if source == "whatsapp" and re.fullmatch(r"[0-9a-f]{64}", text.lower()):
        return f"hash:{text[:12]}"
    return text[:120]


def _task_order_expression() -> str:
    """Return SQL expression for priority sorting."""
    return """
        CASE LOWER(COALESCE(priority, 'normal'))
            WHEN 'urgent' THEN 4
            WHEN 'high' THEN 3
            WHEN 'normal' THEN 2
            WHEN 'low' THEN 1
            ELSE 2
        END
    """


def _ordered_task_query() -> str:
    """Return a reusable ORDER BY expression for sorted task queries."""
    return f"""
            ORDER BY (due_date IS NULL) ASC,
                     due_date ASC,
                     ({_task_order_expression()}) DESC,
                     id ASC
            """


def _task_select_sql() -> str:
    """Return selected task columns."""
    return """
            SELECT id, title, category, notes, status, due_date, priority, recurrence, snoozed_until
            FROM tasks
            """


class TaskRepository:
    """Reads and writes local tasks in SQLite."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def get_task_by_id(self, task_id: int) -> dict | None:
        """Return one task by id, or None if it does not exist."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE id = ?
                LIMIT 1
                """,
                (task_id,),
            ).fetchone()
            return row_to_dict(row) if row is not None else None

    def get_open_tasks(self, *, include_snoozed: bool = False) -> List[dict]:
        """Return all tasks that are not marked as done.

        Tasks snoozed into the future are hidden unless include_snoozed is set.
        """
        snooze_filter = (
            ""
            if include_snoozed
            else " AND (snoozed_until IS NULL OR snoozed_until <= :today)"
        )
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE (status IS NULL
                    OR (LOWER(status) != 'done' AND LOWER(status) != 'archived'))
                    {snooze_filter}
                {_ordered_task_query()}
                """,
                {"today": date.today().isoformat()} if not include_snoozed else {},
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def get_tasks_by_status(self, status: str) -> List[dict]:
        """Return tasks that match a status value."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE LOWER(status) = LOWER(:status)
                {_ordered_task_query()}
                """,
                {"status": status},
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def search_tasks(
        self,
        query: str,
        status: str | None = None,
        category: str | None = None,
    ) -> List[dict]:
        """Search title and notes with optional status and category filters."""
        search_value = query.strip().lower()
        if not search_value:
            return []

        conditions = ["(LOWER(title) LIKE :query OR LOWER(notes) LIKE :query)"]
        params: dict[str, object] = {"query": f"%{search_value}%"}

        if status is not None:
            conditions.append("LOWER(status) = LOWER(:status)")
            params["status"] = status
        if category is not None:
            conditions.append("LOWER(category) = LOWER(:category)")
            params["category"] = category

        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE {' AND '.join(conditions)}
                {_ordered_task_query()}
                """,
                params,
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def filter_tasks(
        self,
        status: str | None = None,
        category: str | None = None,
        due_date: str | None = None,
    ) -> List[dict]:
        """Filter tasks by optional status, category and due_date."""
        conditions: list[str] = []
        params: dict[str, object] = {}

        if status is not None:
            conditions.append("LOWER(status) = LOWER(:status)")
            params["status"] = status
        if category is not None:
            conditions.append("LOWER(category) = LOWER(:category)")
            params["category"] = category
        if due_date is not None:
            conditions.append("due_date = :due_date")
            params["due_date"] = due_date

        query = f"""
            {_task_select_sql()}
            """
        if conditions:
            query += f" WHERE {' AND '.join(conditions)}"
        query += _ordered_task_query()

        with get_connection(self.db_path) as connection:
            rows = connection.execute(query, params).fetchall()
            return [row_to_dict(row) for row in rows]

    def create_task(
        self,
        title: str,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        status: str = "open",
        priority: str | None = "normal",
        recurrence: str | None = None,
    ) -> dict:
        """Create one local task and return it as a dict."""
        normalized_title = title.strip()
        if not normalized_title:
            raise ValueError("Eine Aufgabe braucht einen Titel.")
        normalized_category = (category or "").strip() or "other"
        normalized_status = (status or "").strip() or "open"
        normalized_notes = "" if notes is None else notes
        normalized_priority = _validate_priority(priority, default="normal")
        normalized_recurrence = _validate_recurrence(recurrence)

        with get_connection(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (title, category, status, due_date, notes, priority, recurrence)
                VALUES (:title, :category, :status, :due_date, :notes, :priority, :recurrence)
                """,
                {
                    "title": normalized_title,
                    "category": normalized_category,
                    "status": normalized_status,
                    "due_date": due_date,
                    "notes": normalized_notes,
                    "priority": normalized_priority,
                    "recurrence": normalized_recurrence,
                },
            )
            task_id = cursor.lastrowid
            row = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
            return row_to_dict(row)

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        recurrence: str | None = None,
    ) -> dict | None:
        """Update selected task fields and return the updated task."""
        updates: list[str] = []
        params: dict[str, object] = {}

        if title is not None:
            normalized_title = title.strip()
            if not normalized_title:
                raise ValueError("Eine Aufgabe braucht einen Titel.")
            updates.append("title = :title")
            params["title"] = normalized_title
        if category is not None:
            updates.append("category = :category")
            params["category"] = category.strip() or "other"
        if due_date is not None:
            updates.append("due_date = :due_date")
            params["due_date"] = due_date.strip() or None
        if notes is not None:
            updates.append("notes = :notes")
            params["notes"] = notes
        if status is not None:
            updates.append("status = :status")
            params["status"] = status
        if priority is not None:
            updates.append("priority = :priority")
            params["priority"] = _validate_priority(priority, default="normal")
        if recurrence is not None:
            updates.append("recurrence = :recurrence")
            params["recurrence"] = _validate_recurrence(recurrence)

        if not updates:
            return self.get_task_by_id(task_id)

        updates_sql = ", ".join(updates)
        params["task_id"] = task_id

        with get_connection(self.db_path) as connection:
            result = connection.execute(
                f"UPDATE tasks SET {updates_sql} WHERE id = :task_id",
                params,
            )
            if result.rowcount == 0:
                return None

            updated_row = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
            return row_to_dict(updated_row)

    def snooze_task(self, task_id: int, until_date: str) -> dict | None:
        """Hide one open task from day views until the given ISO date."""
        normalized = str(until_date or "").strip()
        try:
            parsed = date.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError("Snooze-Datum muss im Format YYYY-MM-DD sein.") from exc
        if parsed <= date.today():
            raise ValueError("Snooze-Datum muss in der Zukunft liegen.")

        with get_connection(self.db_path) as connection:
            result = connection.execute(
                "UPDATE tasks SET snoozed_until = :until WHERE id = :task_id",
                {"until": parsed.isoformat(), "task_id": task_id},
            )
            if result.rowcount == 0:
                return None
        return self.get_task_by_id(task_id)

    def unsnooze_task(self, task_id: int) -> dict | None:
        """Clear a task's snooze so it shows up again immediately."""
        with get_connection(self.db_path) as connection:
            result = connection.execute(
                "UPDATE tasks SET snoozed_until = NULL WHERE id = :task_id",
                {"task_id": task_id},
            )
            if result.rowcount == 0:
                return None
        return self.get_task_by_id(task_id)

    def mark_task_done(self, task_id: int) -> dict | None:
        """Atomically complete one task and create at most one recurrence."""
        with get_connection(self.db_path) as connection:
            # Acquire the SQLite write lock before reading the status. Concurrent
            # callers therefore cannot both observe the recurring task as open.
            connection.execute("BEGIN IMMEDIATE")
            task_row = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
            if task_row is None:
                return None

            task = row_to_dict(task_row)
            if str(task.get("status", "")).lower() == "done":
                return task

            updated = connection.execute(
                """
                UPDATE tasks
                SET status = 'done'
                WHERE id = :task_id
                    AND (status IS NULL OR LOWER(status) != 'done')
                """,
                {"task_id": task_id},
            )
            if updated.rowcount != 1:
                current_row = connection.execute(
                    f"""
                    {_task_select_sql()}
                    WHERE id = ?
                    """,
                    (task_id,),
                ).fetchone()
                return row_to_dict(current_row) if current_row is not None else None

            recurrence = task.get("recurrence")
            due_date = task.get("due_date")
            if recurrence and due_date:
                next_due_date = calculate_next_recurrence_due_date(due_date, recurrence)
                connection.execute(
                    """
                    INSERT INTO tasks (
                        title, category, status, due_date, notes, priority, recurrence
                    )
                    VALUES (
                        :title, :category, 'open', :due_date, :notes, :priority, :recurrence
                    )
                    """,
                    {
                        "title": str(task.get("title") or ""),
                        "category": task.get("category"),
                        "due_date": next_due_date,
                        "notes": task.get("notes"),
                        "priority": task.get("priority"),
                        "recurrence": recurrence,
                    },
                )

            done_row = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
            return row_to_dict(done_row)

    def archive_task(self, task_id: int) -> dict | None:
        """Set one task status to archived."""
        return self.update_task(task_id, status="archived")

    def delete_task(self, task_id: int) -> bool:
        """Delete one task row from SQLite."""
        with get_connection(self.db_path) as connection:
            result = connection.execute(
                """
                DELETE FROM tasks
                WHERE id = :task_id
                """,
                {"task_id": task_id},
            )
            return result.rowcount == 1

    def get_tasks_for_date(self, date_iso: str) -> List[dict]:
        """Return open tasks for a specific date."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE (status IS NULL OR (LOWER(status) != 'done' AND LOWER(status) != 'archived'))
                    AND due_date = ?
                    AND (snoozed_until IS NULL OR snoozed_until <= ?)
                {_ordered_task_query()}
                """,
                (date_iso, date_iso),
            ).fetchall()
            return [row_to_dict(row) for row in rows]


class MessageRepository:
    """Reads message samples from local SQLite."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def get_messages(self, *, include_spam: bool = False) -> List[dict]:
        """Return all stored sample messages."""
        with get_connection(self.db_path) as connection:
            where = "" if include_spam else "WHERE is_spam = 0"
            rows = connection.execute(
                f"""
                SELECT id, sender, text, received_at, contact_type, is_spam
                FROM messages
                {where}
                ORDER BY id
                """,
            ).fetchall()
            return [row_to_dict(row) for row in rows]


class BlockedSenderRepository:
    """Manage Friday's local-only blocked sender list."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def block_sender(
        self,
        *,
        source: str,
        sender: str | None,
        label: str | None = None,
    ) -> dict:
        """Add or refresh one blocked sender and return the local row."""
        normalized_source = _normalize_blocked_sender_source(source)
        sender_key = normalize_blocked_sender_key(normalized_source, sender)
        if not sender_key:
            raise ValueError("Absender kann nicht blockiert werden.")
        display_label = _blocked_sender_label(normalized_source, label or sender)
        now = _now_iso_timestamp()

        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT INTO blocked_senders (source, sender_key, label, created_at)
                VALUES (:source, :sender_key, :label, :created_at)
                ON CONFLICT(source, sender_key) DO UPDATE SET
                    label = excluded.label
                """,
                {
                    "source": normalized_source,
                    "sender_key": sender_key,
                    "label": display_label,
                    "created_at": now,
                },
            )
            row = connection.execute(
                """
                SELECT id, source, sender_key, label, created_at
                FROM blocked_senders
                WHERE source = ? AND sender_key = ?
                LIMIT 1
                """,
                (normalized_source, sender_key),
            ).fetchone()
        return row_to_dict(row)

    def is_sender_blocked(self, *, source: str, sender: str | None) -> bool:
        """Return whether a sender is hidden by the local block list."""
        normalized_source = _normalize_blocked_sender_source(source)
        sender_key = normalize_blocked_sender_key(normalized_source, sender)
        if not sender_key:
            return False
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM blocked_senders
                WHERE source = ? AND sender_key = ?
                LIMIT 1
                """,
                (normalized_source, sender_key),
            ).fetchone()
        return row is not None

    def list_blocked_senders(self) -> list[dict]:
        """Return all blocked senders for the local spam view."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, source, sender_key, label, created_at
                FROM blocked_senders
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        return [row_to_dict(row) for row in rows]

    def unblock_sender(self, blocked_sender_id: int) -> dict | None:
        """Remove one local sender block and restore matching spam previews."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT id, source, sender_key, label, created_at
                FROM blocked_senders
                WHERE id = ?
                LIMIT 1
                """,
                (int(blocked_sender_id),),
            ).fetchone()
            if row is None:
                return None
            item = row_to_dict(row)
            connection.execute("DELETE FROM blocked_senders WHERE id = ?", (int(blocked_sender_id),))
            self._restore_messages_for_sender(connection, item["source"], item["sender_key"])
        return item

    def mark_source_message_spam(self, *, source: str, message_id: str | int) -> dict | None:
        """Mark one local message preview as spam and block its sender."""
        normalized_source = _normalize_blocked_sender_source(source)
        with get_connection(self.db_path) as connection:
            if normalized_source == "ms_mail":
                row = self._find_ms_mail_row(connection, message_id)
                if row is None:
                    return None
                sender = str(row["sender"] or "")
                blocked = self.block_sender(source=normalized_source, sender=sender, label=sender)
                connection.execute(
                    "UPDATE ms_mail_messages SET is_spam = 1 WHERE id = ?",
                    (int(row["id"]),),
                )
                return {"message": row_to_dict(row), "blocked_sender": blocked}

            if normalized_source == "imap_mail":
                row = self._find_ms_mail_row(connection, message_id)
                if row is None:
                    return None
                sender = str(row["sender"] or "")
                blocked = self.block_sender(source=normalized_source, sender=sender, label=sender)
                connection.execute(
                    "UPDATE ms_mail_messages SET is_spam = 1 WHERE id = ?",
                    (int(row["id"]),),
                )
                return {"message": row_to_dict(row), "blocked_sender": blocked}

            if normalized_source == "whatsapp":
                row = self._find_whatsapp_row(connection, message_id)
                if row is None:
                    return None
                sender_hash = str(row["sender_number_hash"] or "")
                label = str(row["sender_name"] or "WhatsApp")
                blocked = self.block_sender(
                    source=normalized_source,
                    sender=sender_hash,
                    label=label,
                )
                connection.execute(
                    "UPDATE whatsapp_messages SET is_spam = 1 WHERE id = ?",
                    (int(row["id"]),),
                )
                return {"message": row_to_dict(row), "blocked_sender": blocked}

            row = self._find_local_message_row(connection, message_id)
            if row is None:
                return None
            sender = str(row["sender"] or "")
            blocked = self.block_sender(source=normalized_source, sender=sender, label=sender)
            connection.execute(
                "UPDATE messages SET is_spam = 1 WHERE id = ?",
                (int(row["id"]),),
            )
            return {"message": row_to_dict(row), "blocked_sender": blocked}

    def _restore_messages_for_sender(
        self,
        connection: sqlite3.Connection,
        source: str,
        sender_key: str,
    ) -> None:
        if source == "whatsapp":
            connection.execute(
                "UPDATE whatsapp_messages SET is_spam = 0 WHERE sender_number_hash = ?",
                (sender_key,),
            )
            return

        if source in {"ms_mail", "imap_mail"}:
            rows = connection.execute("SELECT id, sender FROM ms_mail_messages").fetchall()
            matching_ids = [
                int(row["id"])
                for row in rows
                if normalize_blocked_sender_key(source, row["sender"]) == sender_key
            ]
            for local_id in matching_ids:
                connection.execute("UPDATE ms_mail_messages SET is_spam = 0 WHERE id = ?", (local_id,))
            return

        rows = connection.execute("SELECT id, sender FROM messages").fetchall()
        matching_ids = [
            int(row["id"])
            for row in rows
            if normalize_blocked_sender_key("message", row["sender"]) == sender_key
        ]
        for local_id in matching_ids:
            connection.execute("UPDATE messages SET is_spam = 0 WHERE id = ?", (local_id,))

    @staticmethod
    def _find_ms_mail_row(connection: sqlite3.Connection, message_id: str | int) -> sqlite3.Row | None:
        text = str(message_id)
        if text.isdigit():
            row = connection.execute(
                """
                SELECT id, source, account_id, account_username, message_id, provider_message_id,
                       sender, subject, received_at, snippet, processed, suggestion_created, is_spam
                FROM ms_mail_messages
                WHERE id = ?
                LIMIT 1
                """,
                (int(text),),
            ).fetchone()
            if row is not None:
                return row
        return connection.execute(
            """
            SELECT id, source, account_id, account_username, message_id, provider_message_id,
                   sender, subject, received_at, snippet, processed, suggestion_created, is_spam
            FROM ms_mail_messages
            WHERE message_id = ? OR provider_message_id = ?
            LIMIT 1
            """,
            (text, text),
        ).fetchone()

    @staticmethod
    def _find_whatsapp_row(connection: sqlite3.Connection, message_id: str | int) -> sqlite3.Row | None:
        text = str(message_id)
        if not text.isdigit():
            return None
        return connection.execute(
            """
            SELECT id, chat_id, sender_name, sender_number_hash, body, received_at,
                   processed, suggestion_created, is_spam
            FROM whatsapp_messages
            WHERE id = ?
            LIMIT 1
            """,
            (int(text),),
        ).fetchone()

    @staticmethod
    def _find_local_message_row(connection: sqlite3.Connection, message_id: str | int) -> sqlite3.Row | None:
        text = str(message_id)
        if not text.isdigit():
            return None
        return connection.execute(
            """
            SELECT id, sender, text, received_at, contact_type, is_spam
            FROM messages
            WHERE id = ?
            LIMIT 1
            """,
            (int(text),),
        ).fetchone()


class MsMailMessageRepository:
    """Stores read-only Microsoft Graph mail previews locally."""

    SNIPPET_LIMIT = 500

    def __init__(
        self,
        db_path: Path | str | None = None,
        *,
        ai_relevance_decider: Callable[[str, Mapping[str, object]], Mapping[str, object]] | None = None,
    ) -> None:
        self.db_path = db_path or get_database_path()
        self.ai_relevance_decider = ai_relevance_decider

    @staticmethod
    def _clean(value: object) -> str:
        return " ".join(str(value or "").strip().split())

    @staticmethod
    def _stored_message_id(account_id: str, provider_message_id: str) -> str:
        if account_id == "default":
            return provider_message_id
        return f"{account_id}:{provider_message_id}"

    def upsert_messages(
        self,
        messages: list[dict] | tuple[dict, ...],
        *,
        account_id: str = "default",
        account_username: str | None = None,
    ) -> tuple[dict, ...]:
        """Insert or update read-only messages including full local body text."""
        normalized: list[dict[str, object]] = []
        normalized_account_id = self._clean(account_id) or "default"
        normalized_account_username = self._clean(account_username)
        blocked_senders = BlockedSenderRepository(self.db_path)
        contacts = ContactRepository(self.db_path)
        for item in messages:
            item_source = _normalize_blocked_sender_source(item.get("source") or "ms_mail")
            provider_message_id = self._clean(item.get("provider_message_id") or item.get("message_id"))
            if not provider_message_id:
                continue
            item_account_id = self._clean(item.get("account_id")) or normalized_account_id
            item_account_username = self._clean(item.get("account_username")) or normalized_account_username
            sender = self._clean(item.get("sender"))
            subject = self._clean(item.get("subject"))
            body_full = str(item.get("body_full") or item.get("body") or "").strip()
            snippet = str(item.get("snippet") or "")[: self.SNIPPET_LIMIT]
            if not snippet and body_full:
                snippet = body_full[: self.SNIPPET_LIMIT]
            recipients = item.get("recipients") if isinstance(item.get("recipients"), list) else []
            recipients_json = json.dumps(recipients, ensure_ascii=False, sort_keys=True)
            relevance = determine_mail_relevance(
                account=item_account_username or item_account_id,
                subject=subject,
                snippet=snippet,
                sender=sender,
                recipients=recipients,
                sender_contact=contacts.find_contact_for_sender(sender),
                body_full=body_full,
                ai_decider=self.ai_relevance_decider,
                allow_ai=self.ai_relevance_decider is not None,
            )
            normalized.append(
                {
                    "account_id": item_account_id,
                    "source": item_source,
                    "account_username": item_account_username,
                    "message_id": self._stored_message_id(item_account_id, provider_message_id),
                    "provider_message_id": provider_message_id,
                    "sender": sender,
                    "subject": subject,
                    "received_at": self._clean(item.get("received_at")),
                    "snippet": snippet,
                    "body_full": body_full,
                    "body_fetched_at": _now_iso_timestamp() if body_full else None,
                    "is_spam": 1 if blocked_senders.is_sender_blocked(source=item_source, sender=sender) else 0,
                    "recipients": recipients_json,
                    "recipients_json": recipients_json,
                    "relevant_for_user": 1 if relevance["relevant"] else 0,
                    "relevance_reason": str(relevance["reason"]),
                    "relevance_method": str(relevance.get("method") or "deterministic"),
                }
            )

        if not normalized:
            return ()

        with get_connection(self.db_path) as connection:
            connection.executemany(
                """
                INSERT INTO ms_mail_messages (
                    source, account_id, account_username, message_id, provider_message_id,
                    sender, subject, received_at, snippet, processed, suggestion_created,
                    is_spam, recipients, recipients_json, body_full, body_fetched_at,
                    relevant_for_user, relevance_reason, relevance_method
                )
                VALUES (
                    :source, :account_id, :account_username, :message_id, :provider_message_id,
                    :sender, :subject, :received_at, :snippet, 0, 0,
                    :is_spam, :recipients, :recipients_json, :body_full, :body_fetched_at,
                    :relevant_for_user, :relevance_reason, :relevance_method
                )
                ON CONFLICT(message_id) DO UPDATE SET
                    source = excluded.source,
                    account_id = excluded.account_id,
                    account_username = excluded.account_username,
                    provider_message_id = excluded.provider_message_id,
                    sender = excluded.sender,
                    subject = excluded.subject,
                    received_at = excluded.received_at,
                    snippet = excluded.snippet,
                    is_spam = CASE
                        WHEN excluded.is_spam = 1 THEN 1
                        ELSE ms_mail_messages.is_spam
                    END,
                    body_full = excluded.body_full,
                    body_fetched_at = excluded.body_fetched_at,
                    recipients = excluded.recipients,
                    recipients_json = excluded.recipients_json,
                    relevant_for_user = excluded.relevant_for_user,
                    relevance_reason = excluded.relevance_reason,
                    relevance_method = excluded.relevance_method
                """,
                normalized,
            )
            ids = [item["message_id"] for item in normalized]
            placeholders = ", ".join("?" for _ in ids)
            rows = connection.execute(
                f"""
                SELECT
                    id, source, account_id, account_username, message_id, provider_message_id,
                    sender, subject, received_at, snippet, processed, suggestion_created,
                    is_spam, recipients, recipients_json, body_fetched_at,
                    relevant_for_user, relevance_reason, relevance_method
                FROM ms_mail_messages
                WHERE message_id IN ({placeholders})
                ORDER BY received_at DESC, id DESC
                """,
                ids,
            ).fetchall()
        return tuple(row_to_dict(row) for row in rows)

    def list_messages(
        self,
        limit: int = 25,
        *,
        account_id: str | None = None,
        include_spam: bool = False,
        include_all: bool = False,
    ) -> list[dict]:
        """Return recent read-only Microsoft mail previews."""
        safe_limit = max(1, min(int(limit), 100))
        normalized_account_id = self._clean(account_id)
        with get_connection(self.db_path) as connection:
            params: tuple[object, ...]
            where_parts: list[str] = []
            if normalized_account_id:
                where_parts.append("account_id = ?")
            if not include_spam:
                where_parts.append("is_spam = 0")
            if not include_all and not include_spam:
                where_parts.append("relevant_for_user = 1")
            where = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""
            if normalized_account_id:
                params = (normalized_account_id, safe_limit)
            else:
                params = (safe_limit,)
            rows = connection.execute(
                f"""
                SELECT
                    id, source, account_id, account_username, message_id, provider_message_id,
                    sender, subject, received_at, snippet, processed, suggestion_created,
                    is_spam, recipients, recipients_json, body_fetched_at,
                    relevant_for_user, relevance_reason, relevance_method
                FROM ms_mail_messages
                {where}
                ORDER BY received_at DESC, id DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [row_to_dict(row) for row in rows]

    def get_message_by_id(self, local_id: int) -> dict | None:
        """Return one locally stored Microsoft mail with full body text."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT
                    id, source, account_id, account_username, message_id, provider_message_id,
                    sender, subject, received_at, snippet, body_full, body_fetched_at,
                    processed, suggestion_created, is_spam, recipients, recipients_json,
                    relevant_for_user, relevance_reason, relevance_method
                FROM ms_mail_messages
                WHERE id = ?
                LIMIT 1
                """,
                (int(local_id),),
            ).fetchone()
        return row_to_dict(row) if row is not None else None

    def get_unprocessed_messages(self, limit: int = 50, *, account_id: str | None = None) -> list[dict]:
        """Return MS mail previews not yet processed into review suggestions."""
        safe_limit = max(1, min(int(limit), 100))
        normalized_account_id = self._clean(account_id)
        with get_connection(self.db_path) as connection:
            params: tuple[object, ...]
            where = "WHERE processed = 0 AND is_spam = 0 AND relevant_for_user = 1"
            if normalized_account_id:
                where += " AND account_id = ?"
                params = (normalized_account_id, safe_limit)
            else:
                params = (safe_limit,)
            rows = connection.execute(
                f"""
                SELECT
                    id, source, account_id, account_username, message_id, provider_message_id,
                    sender, subject, received_at, snippet, body_full, processed, suggestion_created,
                    is_spam, recipients, recipients_json, relevant_for_user, relevance_reason, relevance_method
                FROM ms_mail_messages
                {where}
                ORDER BY received_at DESC, id DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [row_to_dict(row) for row in rows]

    def mark_processed(self, local_id: int, *, suggestion_created: bool) -> None:
        """Mark one locally stored MS mail preview as processed."""
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                UPDATE ms_mail_messages
                SET processed = 1,
                    suggestion_created = :suggestion_created
                WHERE id = :local_id
                """,
                {
                    "local_id": local_id,
                    "suggestion_created": 1 if suggestion_created else 0,
                },
            )


class MailboxCleanupLogRepository:
    """Audit reversible Gmail inbox cleanup moves."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def create_entry(
        self,
        *,
        account_id: str,
        provider_message_id: str,
        sender: str | None,
        subject: str | None,
        from_folder: str = "INBOX",
        to_label: str = "Friday/Aussortiert",
        source: str = "imap_mail",
    ) -> dict:
        """Create one local audit entry for a reversible mailbox move."""
        normalized_source = _normalize_blocked_sender_source(source)
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO mailbox_cleanup_log (
                    account_id, provider_message_id, sender, subject,
                    from_folder, to_label, moved_at, undone, source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    str(account_id or "").strip(),
                    str(provider_message_id or "").strip(),
                    str(sender or "").strip(),
                    str(subject or "").strip(),
                    str(from_folder or "INBOX").strip() or "INBOX",
                    str(to_label or "Friday/Aussortiert").strip() or "Friday/Aussortiert",
                    now,
                    normalized_source,
                ),
            )
            row = connection.execute(
                """
                SELECT id, account_id, provider_message_id, sender, subject,
                    from_folder, to_label, moved_at, undone, undone_at, source
                FROM mailbox_cleanup_log
                WHERE id = ?
                LIMIT 1
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return row_to_dict(row)

    def list_entries(self, limit: int = 50, *, include_undone: bool = False) -> list[dict]:
        """Return recent mailbox cleanup audit entries."""
        safe_limit = max(1, min(int(limit), 200))
        where = "" if include_undone else "WHERE undone = 0"
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"""
                SELECT id, account_id, provider_message_id, sender, subject,
                    from_folder, to_label, moved_at, undone, undone_at, source
                FROM mailbox_cleanup_log
                {where}
                ORDER BY moved_at DESC, id DESC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [row_to_dict(row) for row in rows]

    def get_entry_by_id(self, log_id: int) -> dict | None:
        """Return one cleanup audit entry."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT id, account_id, provider_message_id, sender, subject,
                    from_folder, to_label, moved_at, undone, undone_at, source
                FROM mailbox_cleanup_log
                WHERE id = ?
                LIMIT 1
                """,
                (int(log_id),),
            ).fetchone()
        return row_to_dict(row) if row is not None else None

    def mark_undone(self, log_id: int) -> dict | None:
        """Mark one cleanup move as reverted in the local audit log."""
        existing = self.get_entry_by_id(log_id)
        if existing is None:
            return None
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                UPDATE mailbox_cleanup_log
                SET undone = 1,
                    undone_at = ?
                WHERE id = ?
                """,
                (now, int(log_id)),
            )
        return self.get_entry_by_id(log_id)


class CalendarRepository:
    """Reads calendar blocks and computes local free slots."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def get_items_for_date(self, date_iso: str) -> List[dict]:
        """Return all calendar items for one day."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, title, start, end, item_type, date
                FROM calendar_items
                WHERE date = ?
                ORDER BY start
                """,
                (date_iso,),
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def record_calendar_entry(
        self,
        *,
        provider: str,
        provider_event_id: str | None,
        policy_id: int | None,
        title: str,
        start: str,
        end: str,
        location: str | None = None,
        notes: str | None = None,
    ) -> dict:
        """Store a local reference to one provider-created calendar event."""
        created_at = datetime.now(timezone.utc).isoformat()
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO calendar_entries
                (provider, provider_event_id, policy_id, title, start, end, location, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider,
                    provider_event_id,
                    policy_id,
                    title,
                    start,
                    end,
                    location,
                    notes,
                    created_at,
                ),
            )
            row = connection.execute(
                """
                SELECT id, provider, provider_event_id, policy_id, title, start, end, location, notes, created_at
                FROM calendar_entries
                WHERE id = ?
                """,
                (int(cursor.lastrowid),),
            ).fetchone()
        return row_to_dict(row)

    def get_calendar_entry_by_provider_event_id(
        self,
        *,
        provider: str,
        provider_event_id: str,
    ) -> dict | None:
        """Return one local calendar entry reference by provider event id."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT id, provider, provider_event_id, policy_id, title, start, end, location, notes, created_at
                FROM calendar_entries
                WHERE provider = ? AND provider_event_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (provider, provider_event_id),
            ).fetchone()
        return None if row is None else row_to_dict(row)

    def delete_calendar_entry_by_provider_event_id(
        self,
        *,
        provider: str,
        provider_event_id: str,
    ) -> dict | None:
        """Delete and return one local calendar entry reference by provider event id."""
        existing = self.get_calendar_entry_by_provider_event_id(
            provider=provider,
            provider_event_id=provider_event_id,
        )
        if existing is None:
            return None
        with get_connection(self.db_path) as connection:
            connection.execute(
                """
                DELETE FROM calendar_entries
                WHERE id = ?
                """,
                (existing["id"],),
            )
        return existing

    def get_free_slots_for_date(self, date_iso: str, duration_minutes: int = 60) -> List[dict]:
        """Return explicit free slots if present; otherwise compute from busy blocks."""
        items = self.get_items_for_date(date_iso)
        free_slots = [item for item in items if str(item.get("item_type", "")).lower() == "free"]
        if free_slots:
            result: List[dict] = []
            for item in free_slots:
                start = item.get("start", "00:00")
                end = item.get("end", "00:00")
                if _to_minutes(end) - _to_minutes(start) >= duration_minutes:
                    result.append({"start": start, "end": end})
            return result

        busy_slots = [
            (_to_minutes(item["start"]), _to_minutes(item["end"]))
            for item in items
            if str(item.get("item_type", "busy")).lower() != "free"
        ]
        busy_slots.sort()

        start_of_day = 9 * 60
        end_of_day = 18 * 60
        free_slots_for_day: List[dict] = []

        candidate_start = start_of_day
        while candidate_start + duration_minutes <= end_of_day:
            candidate_end = candidate_start + duration_minutes
            overlap = any(
                not (candidate_end <= busy_start or candidate_start >= busy_end)
                for busy_start, busy_end in busy_slots
            )
            if not overlap:
                free_slots_for_day.append({"start": _to_time_string(candidate_start), "end": _to_time_string(candidate_end)})
            candidate_start += 60

        return free_slots_for_day


class ContactRepository:
    """Reads contact types from local SQLite."""

    VALID_TYPES = {
        "customer",
        "friend",
        "family",
        "work",
        "other",
        "familie",
        "arbeit",
        "freund",
        "kunde",
        "dienstleister",
        "sonstiges",
        "unbekannt",
    }
    TYPE_ALIASES = {
        "family": "familie",
        "friend": "freund",
        "work": "arbeit",
        "customer": "kunde",
        "other": "sonstiges",
    }
    VALID_BETREUER = {"flo", "philip", "alex"}
    CONTACT_COLUMNS = "id, name, contact_type, notes, email_address, whatsapp_target, betreuer"

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def _normalize_contact_type(self, contact_type: str | None) -> str:
        normalized_type = (contact_type or "work").strip().lower() or "work"
        return self.TYPE_ALIASES.get(normalized_type, normalized_type)

    def _normalize_betreuer(
        self,
        betreuer: str | None,
        contact_type: str | None,
    ) -> str | None:
        if self._normalize_contact_type(contact_type) != "kunde":
            return None
        normalized = (betreuer or "").strip().lower()
        if not normalized:
            return None
        if normalized not in self.VALID_BETREUER:
            allowed = ", ".join(sorted(self.VALID_BETREUER))
            raise ValueError(f"Betreuer must be one of: {allowed}.")
        return normalized

    @staticmethod
    def _normalize_lookup_value(value: str | None) -> str:
        return " ".join(str(value or "").strip().casefold().split())

    @staticmethod
    def _normalize_phone_value(value: str | None) -> str:
        digits = re.sub(r"\D+", "", str(value or ""))
        return digits if len(digits) >= 5 else ""

    def get_contact_by_id(self, contact_id: int) -> dict | None:
        """Return one stored contact by id."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT id, name, contact_type, notes, email_address, whatsapp_target, betreuer
                FROM contacts
                WHERE id = ?
                LIMIT 1
                """,
                (contact_id,),
            ).fetchone()
        return row_to_dict(row) if row is not None else None

    def get_contacts(self) -> List[dict]:
        """Return stored contacts."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, name, contact_type, notes, email_address, whatsapp_target, betreuer
                FROM contacts
                ORDER BY name
                """,
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def create_contact(
        self,
        name: str,
        contact_type: str | None = "work",
        notes: str | None = "",
        email_address: str | None = None,
        whatsapp_target: str | None = None,
        betreuer: str | None = None,
    ) -> dict:
        """Create a local contact entry."""
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Contact name must not be empty.")
        normalized_type = self._normalize_contact_type(contact_type)
        normalized_betreuer = self._normalize_betreuer(betreuer, normalized_type)
        normalized_notes = "" if notes is None else notes
        normalized_email = (email_address or "").strip() or None
        normalized_whatsapp = (whatsapp_target or "").strip() or None
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO contacts (name, contact_type, notes, email_address, whatsapp_target, betreuer)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized_name,
                    normalized_type,
                    normalized_notes,
                    normalized_email,
                    normalized_whatsapp,
                    normalized_betreuer,
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, contact_type, notes, email_address, whatsapp_target, betreuer
                FROM contacts
                WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
            connection.commit()
        return row_to_dict(row)

    def update_contact(
        self,
        contact_id: int,
        *,
        name: str | None = None,
        contact_type: str | None = None,
        notes: str | None = None,
        email_address: str | None = None,
        whatsapp_target: str | None = None,
        betreuer: str | None = None,
    ) -> dict | None:
        """Update selected local contact fields and return the updated contact."""
        current = self.get_contact_by_id(contact_id)
        if current is None:
            return None

        updates: list[str] = []
        params: dict[str, object] = {"id": contact_id}
        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("Contact name must not be empty.")
            updates.append("name = :name")
            params["name"] = normalized_name
        if contact_type is not None:
            updates.append("contact_type = :contact_type")
            params["contact_type"] = self._normalize_contact_type(contact_type)
        if notes is not None:
            updates.append("notes = :notes")
            params["notes"] = notes
        if email_address is not None:
            updates.append("email_address = :email_address")
            params["email_address"] = email_address.strip() or None
        if whatsapp_target is not None:
            updates.append("whatsapp_target = :whatsapp_target")
            params["whatsapp_target"] = whatsapp_target.strip() or None
        final_contact_type = str(params.get("contact_type", current.get("contact_type")))
        if betreuer is not None:
            updates.append("betreuer = :betreuer")
            params["betreuer"] = self._normalize_betreuer(betreuer, final_contact_type)
        elif contact_type is not None and final_contact_type != "kunde":
            updates.append("betreuer = :betreuer")
            params["betreuer"] = None

        if not updates:
            return current

        with get_connection(self.db_path) as connection:
            connection.execute(
                f"UPDATE contacts SET {', '.join(updates)} WHERE id = :id",
                params,
            )
            connection.commit()
        return self.get_contact_by_id(contact_id)

    def get_contact_type_by_name(self, name: str) -> str:
        """Return a known contact type, fallback to other."""
        contact = self.find_contact_for_sender(name)
        if contact is not None:
            return self._normalize_contact_type(contact.get("contact_type"))
        return "sonstiges"

    def find_contact_for_sender(self, sender: str | None) -> dict | None:
        """Find a contact by displayed sender, email address, or WhatsApp target."""
        normalized_sender = self._normalize_lookup_value(sender)
        email_match = re.search(r"[\w.!#$%&'*+/=?^`{|}~-]+@[\w.-]+", str(sender or ""))
        normalized_sender_values = {normalized_sender}
        if email_match:
            normalized_sender_values.add(self._normalize_lookup_value(email_match.group(0)))
        phone_sender = self._normalize_phone_value(sender)
        if not normalized_sender and not phone_sender:
            return None

        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"SELECT {self.CONTACT_COLUMNS} FROM contacts ORDER BY id"
            ).fetchall()

        for row in rows:
            contact = row_to_dict(row)
            lookup_values = {
                self._normalize_lookup_value(contact.get("name")),
                self._normalize_lookup_value(contact.get("email_address")),
                self._normalize_lookup_value(contact.get("whatsapp_target")),
            }
            phone_values = {
                self._normalize_phone_value(contact.get("email_address")),
                self._normalize_phone_value(contact.get("whatsapp_target")),
            }
            if lookup_values.intersection(normalized_sender_values):
                return contact
            if phone_sender and phone_sender in phone_values:
                return contact
        return None


class MessageSuggestionRepository:
    """Create and review local message suggestion drafts."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def _row_to_dict(self, row: sqlite3.Row | None) -> dict | None:
        """Convert row only when it exists."""
        return row_to_dict(row) if row is not None else None

    def create_suggestion(
        self,
        message_id: int,
        draft_text: str,
        suggestion_type: str = "reply",
        status: str = "pending",
        notes: str | None = None,
    ) -> dict:
        """Create a local suggestion unless it already exists."""
        normalized_draft = (draft_text or "").strip()
        if not normalized_draft:
            raise ValueError("Ein Vorschlag braucht Text.")

        normalized_type = (suggestion_type or "").strip() or "reply"
        normalized_status = _validate_suggestion_status(status)

        now = _now_iso_timestamp()

        with get_connection(self.db_path) as connection:
            existing = connection.execute(
                """
                SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                FROM message_suggestions
                WHERE message_id = ? AND suggestion_type = ?
                LIMIT 1
                """,
                (message_id, normalized_type),
            ).fetchone()
            if existing is not None:
                return row_to_dict(existing)

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO message_suggestions (
                        message_id,
                        suggestion_type,
                        draft_text,
                        status,
                        notes,
                        created_at,
                        updated_at
                    )
                    VALUES (:message_id, :suggestion_type, :draft_text, :status, :notes, :created_at, :updated_at)
                    """,
                    {
                        "message_id": message_id,
                        "suggestion_type": normalized_type,
                        "draft_text": normalized_draft,
                        "status": normalized_status,
                        "notes": notes,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
            except sqlite3.IntegrityError:
                existing = connection.execute(
                    """
                    SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                    FROM message_suggestions
                    WHERE message_id = ? AND suggestion_type = ?
                    LIMIT 1
                    """,
                    (message_id, normalized_type),
                ).fetchone()
                if existing is not None:
                    return row_to_dict(existing)
                raise

            suggestion_id = cursor.lastrowid
            return row_to_dict(
                connection.execute(
                    """
                    SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                    FROM message_suggestions
                    WHERE id = ?
                    """,
                    (suggestion_id,),
                ).fetchone(),
            )

    def get_suggestion_by_id(self, suggestion_id: int) -> dict | None:
        """Return one suggestion by id."""
        with get_connection(self.db_path) as connection:
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                    FROM message_suggestions
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (suggestion_id,),
                ).fetchone(),
            )

    def get_suggestion_for_message(
        self,
        message_id: int,
        suggestion_type: str = "reply",
    ) -> dict | None:
        """Return one suggestion for a message/type pair."""
        normalized_type = (suggestion_type or "").strip() or "reply"
        with get_connection(self.db_path) as connection:
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                    FROM message_suggestions
                    WHERE message_id = ? AND suggestion_type = ?
                    LIMIT 1
                    """,
                    (message_id, normalized_type),
                ).fetchone(),
            )

    def get_pending_suggestions(self) -> list[dict]:
        """Return local reviewable message suggestions."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                FROM message_suggestions
                WHERE LOWER(status) IN ('pending', 'edited')
                ORDER BY id
                """
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def get_all_suggestions(self) -> list[dict]:
        """Return all local suggestion records."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                FROM message_suggestions
                ORDER BY id
                """
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def update_suggestion_status(
        self,
        suggestion_id: int,
        status: str,
        notes: str | None = None,
    ) -> dict | None:
        """Set the status of a local message suggestion."""
        normalized_status = _validate_suggestion_status(status)
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM message_suggestions WHERE id = ? LIMIT 1",
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None

            connection.execute(
                """
                UPDATE message_suggestions
                SET status = :status,
                    updated_at = :updated_at,
                    notes = COALESCE(:notes, notes)
                WHERE id = :suggestion_id
                """,
                {"status": normalized_status, "updated_at": now, "notes": notes, "suggestion_id": suggestion_id},
            )

            return row_to_dict(
                connection.execute(
                    """
                    SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                    FROM message_suggestions
                    WHERE id = ?
                    """,
                    (suggestion_id,),
                ).fetchone(),
                    )

    def edit_suggestion_draft(
        self,
        suggestion_id: int,
        draft_text: str,
    ) -> dict | None:
        """Update draft text and mark the suggestion as edited."""
        normalized_draft = (draft_text or "").strip()
        if not normalized_draft:
            raise ValueError("Ein Vorschlag braucht Text.")

        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM message_suggestions WHERE id = ? LIMIT 1",
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                """
                UPDATE message_suggestions
                SET draft_text = :draft_text,
                    status = 'edited',
                    updated_at = :updated_at
                WHERE id = :suggestion_id
                """,
                {
                    "draft_text": normalized_draft,
                    "updated_at": now,
                    "suggestion_id": suggestion_id,
                },
            )
            return row_to_dict(
                connection.execute(
                    """
                    SELECT id, message_id, suggestion_type, draft_text, status, notes, created_at, updated_at
                    FROM message_suggestions
                    WHERE id = ?
                    """,
                    (suggestion_id,),
                ).fetchone(),
            )


class TaskSuggestionRepository:
    """Create and review local task suggestions."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def _row_to_dict(self, row: sqlite3.Row | None) -> dict | None:
        """Convert row only when it exists."""
        return row_to_dict(row) if row is not None else None

    def create_task_suggestion(
        self,
        message_id: int,
        title: str,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        priority: str | None = "normal",
        status: str = "pending",
    ) -> dict:
        """Create a local task suggestion unless one already exists."""
        normalized_title = (title or "").strip()
        if not normalized_title:
            raise ValueError("Ein Aufgaben-Vorschlag braucht einen Titel.")

        normalized_category = (category or "").strip() or "other"
        normalized_due_date = (due_date or "").strip() or None
        normalized_notes = notes if notes is None else notes
        normalized_priority = _validate_priority(priority, default="normal")
        normalized_status = _validate_task_suggestion_status(status)

        now = _now_iso_timestamp()

        with get_connection(self.db_path) as connection:
            existing = connection.execute(
                """
                SELECT
                    id, message_id, title, category, due_date, notes, priority,
                    status, created_task_id, created_at, updated_at
                FROM task_suggestions
                WHERE message_id = ?
                LIMIT 1
                """,
                (message_id,),
            ).fetchone()
            if existing is not None:
                return row_to_dict(existing)

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO task_suggestions (
                        message_id,
                        title,
                        category,
                        due_date,
                        notes,
                        priority,
                        status,
                        created_task_id,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        :message_id,
                        :title,
                        :category,
                        :due_date,
                        :notes,
                        :priority,
                        :status,
                        NULL,
                        :created_at,
                        :updated_at
                    )
                    """,
                    {
                        "message_id": message_id,
                        "title": normalized_title,
                        "category": normalized_category,
                        "due_date": normalized_due_date,
                        "notes": normalized_notes,
                        "priority": normalized_priority,
                        "status": normalized_status,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
            except sqlite3.IntegrityError:
                existing = connection.execute(
                    """
                    SELECT
                        id, message_id, title, category, due_date, notes, priority,
                        status, created_task_id, created_at, updated_at
                    FROM task_suggestions
                    WHERE message_id = ?
                    LIMIT 1
                    """,
                    (message_id,),
                ).fetchone()
                if existing is not None:
                    return row_to_dict(existing)
                raise

            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT
                        id, message_id, title, category, due_date, notes, priority,
                        status, created_task_id, created_at, updated_at
                    FROM task_suggestions
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (cursor.lastrowid,),
                ).fetchone(),
            )

    def get_task_suggestion_by_id(self, suggestion_id: int) -> dict | None:
        """Return one task suggestion by id."""
        with get_connection(self.db_path) as connection:
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT
                        id, message_id, title, category, due_date, notes, priority,
                        status, created_task_id, created_at, updated_at
                    FROM task_suggestions
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (suggestion_id,),
                ).fetchone(),
            )

    def get_task_suggestion_for_message(self, message_id: int) -> dict | None:
        """Return task suggestion for a message."""
        with get_connection(self.db_path) as connection:
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT
                        id, message_id, title, category, due_date, notes, priority,
                        status, created_task_id, created_at, updated_at
                    FROM task_suggestions
                    WHERE message_id = ?
                    LIMIT 1
                    """,
                    (message_id,),
                ).fetchone(),
            )

    def get_pending_task_suggestions(self) -> list[dict]:
        """Return open reviewable task suggestions."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    id, message_id, title, category, due_date, notes, priority,
                    status, created_task_id, created_at, updated_at
                FROM task_suggestions
                WHERE LOWER(status) IN ('pending', 'edited')
                ORDER BY id
                """
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def get_all_task_suggestions(self) -> list[dict]:
        """Return all local task suggestions."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT
                    id, message_id, title, category, due_date, notes, priority,
                    status, created_task_id, created_at, updated_at
                FROM task_suggestions
                ORDER BY id
                """
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def update_task_suggestion_status(
        self,
        suggestion_id: int,
        status: str,
    ) -> dict | None:
        """Set a task suggestion status."""
        normalized_status = _validate_task_suggestion_status(status)
        now = _now_iso_timestamp()

        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM task_suggestions WHERE id = ? LIMIT 1",
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None

            connection.execute(
                """
                UPDATE task_suggestions
                SET status = :status,
                    updated_at = :updated_at
                WHERE id = :suggestion_id
                """,
                {
                    "status": normalized_status,
                    "updated_at": now,
                    "suggestion_id": suggestion_id,
                },
            )
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT
                        id, message_id, title, category, due_date, notes, priority,
                        status, created_task_id, created_at, updated_at
                    FROM task_suggestions
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (suggestion_id,),
                ).fetchone(),
            )

    def edit_task_suggestion(
        self,
        suggestion_id: int,
        title: str | None = None,
        category: str | None = None,
        due_date: str | None = None,
        notes: str | None = None,
        priority: str | None = None,
    ) -> dict | None:
        """Update a local task suggestion."""
        updates: list[str] = []
        params: dict[str, object] = {}

        if title is not None:
            normalized_title = title.strip()
            if not normalized_title:
                raise ValueError("Ein Aufgaben-Vorschlag braucht einen Titel.")
            updates.append("title = :title")
            params["title"] = normalized_title

        if category is not None:
            updates.append("category = :category")
            params["category"] = category.strip() or "other"

        if due_date is not None:
            updates.append("due_date = :due_date")
            params["due_date"] = (due_date or "").strip() or None

        if notes is not None:
            updates.append("notes = :notes")
            params["notes"] = notes

        if priority is not None:
            updates.append("priority = :priority")
            params["priority"] = _validate_priority(priority, default="normal")

        if not updates:
            return self.get_task_suggestion_by_id(suggestion_id)

        updates.append("status = 'edited'")
        updates.append("updated_at = :updated_at")
        params["updated_at"] = _now_iso_timestamp()
        params["suggestion_id"] = suggestion_id
        updates_sql = ", ".join(updates)

        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM task_suggestions WHERE id = ? LIMIT 1",
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None

            connection.execute(
                f"UPDATE task_suggestions SET {updates_sql} WHERE id = :suggestion_id",
                params,
            )
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT
                        id, message_id, title, category, due_date, notes, priority,
                        status, created_task_id, created_at, updated_at
                    FROM task_suggestions
                    WHERE id = :suggestion_id
                    LIMIT 1
                    """,
                    {"suggestion_id": suggestion_id},
                ).fetchone(),
            )

    def mark_task_suggestion_converted(self, suggestion_id: int, created_task_id: int) -> dict | None:
        """Set converted status and link the created task."""
        now = _now_iso_timestamp()
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM task_suggestions WHERE id = ? LIMIT 1",
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None
            connection.execute(
                """
                UPDATE task_suggestions
                SET status = 'converted',
                    created_task_id = :created_task_id,
                    updated_at = :updated_at
                WHERE id = :suggestion_id
                """,
                {
                    "created_task_id": created_task_id,
                    "updated_at": now,
                    "suggestion_id": suggestion_id,
                },
            )
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT
                        id, message_id, title, category, due_date, notes, priority,
                        status, created_task_id, created_at, updated_at
                    FROM task_suggestions
                    WHERE id = :suggestion_id
                    LIMIT 1
                    """,
                    {"suggestion_id": suggestion_id},
                ).fetchone(),
            )


class CalendarSuggestionRepository:
    """Create and review local calendar slot suggestions."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def _row_to_dict(self, row: sqlite3.Row | None) -> dict | None:
        """Convert row only when it exists."""
        return row_to_dict(row) if row is not None else None

    def create_calendar_suggestion(
        self,
        message_id: int,
        slot_date: str,
        start: str,
        end: str,
        status: str = "pending",
        notes: str | None = None,
    ) -> dict:
        """Create a local calendar suggestion unless it already exists."""
        normalized_slot_date = (slot_date or "").strip()
        normalized_start = (start or "").strip()
        normalized_end = (end or "").strip()
        if not normalized_slot_date or not normalized_start or not normalized_end:
            raise ValueError("Ein Kalender-Vorschlag braucht Datum, Start und Ende.")

        normalized_status = _validate_calendar_suggestion_status(status)
        now = _now_iso_timestamp()

        with get_connection(self.db_path) as connection:
            existing = connection.execute(
                """
                SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                FROM calendar_suggestions
                WHERE message_id = ? AND slot_date = ? AND start = ? AND end = ?
                LIMIT 1
                """,
                (message_id, normalized_slot_date, normalized_start, normalized_end),
            ).fetchone()
            if existing is not None:
                return row_to_dict(existing)

            try:
                cursor = connection.execute(
                    """
                    INSERT INTO calendar_suggestions (
                        message_id,
                        slot_date,
                        start,
                        end,
                        status,
                        notes,
                        created_at,
                        updated_at
                    )
                    VALUES (:message_id, :slot_date, :start, :end, :status, :notes, :created_at, :updated_at)
                    """,
                    {
                        "message_id": message_id,
                        "slot_date": normalized_slot_date,
                        "start": normalized_start,
                        "end": normalized_end,
                        "status": normalized_status,
                        "notes": notes,
                        "created_at": now,
                        "updated_at": now,
                    },
                )
            except sqlite3.IntegrityError:
                existing = connection.execute(
                    """
                    SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                    FROM calendar_suggestions
                    WHERE message_id = ? AND slot_date = ? AND start = ? AND end = ?
                    LIMIT 1
                    """,
                    (message_id, normalized_slot_date, normalized_start, normalized_end),
                ).fetchone()
                if existing is not None:
                    return row_to_dict(existing)
                raise

            suggestion_id = cursor.lastrowid
            return row_to_dict(
                connection.execute(
                    """
                    SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                    FROM calendar_suggestions
                    WHERE id = ?
                    """,
                    (suggestion_id,),
                ).fetchone(),
            )

    def get_calendar_suggestion_by_id(self, suggestion_id: int) -> dict | None:
        """Return one calendar suggestion by id."""
        with get_connection(self.db_path) as connection:
            return self._row_to_dict(
                connection.execute(
                    """
                    SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                    FROM calendar_suggestions
                    WHERE id = ?
                    LIMIT 1
                    """,
                    (suggestion_id,),
                ).fetchone(),
            )

    def get_calendar_suggestions_for_message(self, message_id: int) -> list[dict]:
        """Return all calendar suggestions for one message."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                FROM calendar_suggestions
                WHERE message_id = ?
                ORDER BY id
                """,
                (message_id,),
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def get_pending_calendar_suggestions_for_message(self, message_id: int) -> list[dict]:
        """Return pending local calendar suggestions for one message."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                FROM calendar_suggestions
                WHERE message_id = ? AND LOWER(status) = 'pending'
                ORDER BY id
                """,
                (message_id,),
            ).fetchall()
            return [row_to_dict(row) for row in rows]

    def select_calendar_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark one calendar suggestion as selected."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM calendar_suggestions WHERE id = ? LIMIT 1",
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None

            now = _now_iso_timestamp()
            connection.execute(
                """
                UPDATE calendar_suggestions
                SET status = :status,
                    updated_at = :updated_at
                WHERE id = :suggestion_id
                """,
                {"status": "selected", "updated_at": now, "suggestion_id": suggestion_id},
            )
            updated_row = connection.execute(
                """
                SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                FROM calendar_suggestions
                WHERE id = ?
                """,
                (suggestion_id,),
            ).fetchone()
            return self._row_to_dict(updated_row)

    def reject_calendar_suggestion(self, suggestion_id: int) -> dict | None:
        """Mark one calendar suggestion as rejected."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM calendar_suggestions WHERE id = ? LIMIT 1",
                (suggestion_id,),
            ).fetchone()
            if row is None:
                return None

            now = _now_iso_timestamp()
            connection.execute(
                """
                UPDATE calendar_suggestions
                SET status = :status,
                    updated_at = :updated_at
                WHERE id = :suggestion_id
                """,
                {"status": "rejected", "updated_at": now, "suggestion_id": suggestion_id},
            )
            updated_row = connection.execute(
                """
                SELECT id, message_id, slot_date, start, end, status, notes, created_at, updated_at
                FROM calendar_suggestions
                WHERE id = ?
                """,
                (suggestion_id,),
            ).fetchone()
            return self._row_to_dict(updated_row)
