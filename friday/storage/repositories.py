"""Repository layer for Friday local SQLite data."""

from __future__ import annotations

from pathlib import Path
from datetime import date, datetime, timedelta, timezone
import calendar
import sqlite3
from typing import List

from friday.config import get_database_path
from friday.storage.database import get_connection


VALID_PRIORITIES = {"low", "normal", "high", "urgent"}
VALID_RECURRENCES = {"taeglich", "woechentlich", "monatlich"}
VALID_SUGGESTION_STATUSES = {"pending", "approved", "rejected", "edited"}
VALID_TASK_SUGGESTION_STATUSES = {"pending", "approved", "rejected", "edited", "converted"}
VALID_CALENDAR_SUGGESTION_STATUSES = {"pending", "selected", "rejected"}


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
            SELECT id, title, category, notes, status, due_date, priority, recurrence
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

    def get_open_tasks(self) -> List[dict]:
        """Return all tasks that are not marked as done."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                f"""
                {_task_select_sql()}
                WHERE status IS NULL
                    OR (LOWER(status) != 'done' AND LOWER(status) != 'archived')
                {_ordered_task_query()}
                """,
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

    def mark_task_done(self, task_id: int) -> dict | None:
        """Set one task status to done."""
        task = self.get_task_by_id(task_id)
        if task is not None and str(task.get("status", "")).lower() == "done":
            return task

        done = self.update_task(task_id, status="done")
        if done is None or task is None:
            return done

        recurrence = task.get("recurrence")
        due_date = task.get("due_date")
        if recurrence and due_date:
            next_due_date = calculate_next_recurrence_due_date(due_date, recurrence)
            self.create_task(
                title=str(task.get("title") or ""),
                category=task.get("category"),
                due_date=next_due_date,
                notes=task.get("notes"),
                priority=task.get("priority"),
                recurrence=recurrence,
            )
        return done

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
                {_ordered_task_query()}
                """,
                (date_iso,),
            ).fetchall()
            return [row_to_dict(row) for row in rows]


class MessageRepository:
    """Reads message samples from local SQLite."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def get_messages(self) -> List[dict]:
        """Return all stored sample messages."""
        with get_connection(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, sender, text, received_at, contact_type
                FROM messages
                ORDER BY id
                """,
            ).fetchall()
            return [row_to_dict(row) for row in rows]


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

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path or get_database_path()

    def _normalize_contact_type(self, contact_type: str | None) -> str:
        normalized_type = (contact_type or "work").strip().lower() or "work"
        normalized_type = self.TYPE_ALIASES.get(normalized_type, normalized_type)
        return normalized_type if normalized_type in self.VALID_TYPES else "sonstiges"

    def get_contact_by_id(self, contact_id: int) -> dict | None:
        """Return one stored contact by id."""
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT id, name, contact_type, notes, email_address, whatsapp_target
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
                SELECT id, name, contact_type, notes, email_address, whatsapp_target
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
    ) -> dict:
        """Create a local contact entry."""
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Contact name must not be empty.")
        normalized_type = self._normalize_contact_type(contact_type)
        normalized_notes = "" if notes is None else notes
        normalized_email = (email_address or "").strip() or None
        normalized_whatsapp = (whatsapp_target or "").strip() or None
        with get_connection(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO contacts (name, contact_type, notes, email_address, whatsapp_target)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    normalized_name,
                    normalized_type,
                    normalized_notes,
                    normalized_email,
                    normalized_whatsapp,
                ),
            )
            row = connection.execute(
                """
                SELECT id, name, contact_type, notes, email_address, whatsapp_target
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
        with get_connection(self.db_path) as connection:
            row = connection.execute(
                "SELECT contact_type FROM contacts WHERE name = ? LIMIT 1",
                (name,),
            ).fetchone()
        if row is None:
            return "sonstiges"
        contact_type = str(row[0] or "other").lower()
        contact_type = self.TYPE_ALIASES.get(contact_type, contact_type)
        return contact_type if contact_type in self.VALID_TYPES else "sonstiges"


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
