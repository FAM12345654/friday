"""Local SQLite database setup for Friday."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List

from friday import config


DATA_DIR = config.DATA_DIR


class FridayConnection(sqlite3.Connection):
    """SQLite connection that closes when used as a context manager."""

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        try:
            return bool(super().__exit__(exc_type, exc_value, traceback))
        finally:
            self.close()


def _resolve_db_path(db_path: Path | str | None = None) -> Path:
    """Return a concrete database path."""
    if db_path is None:
        return config.get_database_path()
    if isinstance(db_path, str):
        return Path(db_path)
    return db_path


def ensure_local_data_dir(db_path: Path | str | None = None) -> None:
    """Make sure the local_data folder for the database exists."""
    path = _resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a sqlite connection with dict-like row access."""
    path = _resolve_db_path(db_path)
    ensure_local_data_dir(path)
    connection = sqlite3.connect(path, factory=FridayConnection)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path: Path | str | None = None) -> None:
    """Create all required Friday tables when they are not present."""
    with get_connection(db_path) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                status TEXT,
                due_date TEXT,
                notes TEXT,
                priority TEXT,
                recurrence TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                received_at TEXT,
                contact_type TEXT
            );

            CREATE TABLE IF NOT EXISTS calendar_items (
                id INTEGER PRIMARY KEY,
                title TEXT,
                start TEXT,
                end TEXT,
                item_type TEXT,
                date TEXT
            );

            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                contact_type TEXT,
                notes TEXT,
                email_address TEXT,
                whatsapp_target TEXT
            );

            CREATE TABLE IF NOT EXISTS contact_contexts (
                contact_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                contact_type TEXT NOT NULL,
                nickname TEXT,
                relationship_context TEXT,
                source_context TEXT NOT NULL,
                user_approved_persistence INTEGER NOT NULL DEFAULT 0,
                sensitivity_checked INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS message_suggestions (
                id INTEGER PRIMARY KEY,
                message_id INTEGER NOT NULL,
                suggestion_type TEXT,
                draft_text TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE (message_id, suggestion_type)
            );

            CREATE TABLE IF NOT EXISTS task_suggestions (
                id INTEGER PRIMARY KEY,
                message_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT,
                due_date TEXT,
                notes TEXT,
                priority TEXT,
                status TEXT NOT NULL,
                created_task_id INTEGER,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE (message_id)
            );

            CREATE TABLE IF NOT EXISTS calendar_suggestions (
                id INTEGER PRIMARY KEY,
                message_id INTEGER NOT NULL,
                slot_date TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE (message_id, slot_date, start, end)
            );

            CREATE TABLE IF NOT EXISTS email_send_log (
                id INTEGER PRIMARY KEY,
                sent_at TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                message_id TEXT,
                status TEXT NOT NULL
            );
            """
        )
        _ensure_task_priority_column(connection)
        _ensure_task_recurrence_column(connection)
        _ensure_contact_target_columns(connection)


def _ensure_task_priority_column(connection: sqlite3.Connection) -> None:
    """Add priority column for older databases that were created before Build 6."""
    columns = connection.execute("PRAGMA table_info(tasks)").fetchall()
    if not any(column[1] == "priority" for column in columns):
        connection.execute("ALTER TABLE tasks ADD COLUMN priority TEXT")


def _ensure_task_recurrence_column(connection: sqlite3.Connection) -> None:
    """Add recurrence column for local recurring tasks."""
    columns = connection.execute("PRAGMA table_info(tasks)").fetchall()
    if not any(column[1] == "recurrence" for column in columns):
        connection.execute("ALTER TABLE tasks ADD COLUMN recurrence TEXT")


def _ensure_contact_target_columns(connection: sqlite3.Connection) -> None:
    """Add optional local contact target fields for draft routing."""
    columns = connection.execute("PRAGMA table_info(contacts)").fetchall()
    existing = {column[1] for column in columns}
    if "email_address" not in existing:
        connection.execute("ALTER TABLE contacts ADD COLUMN email_address TEXT")
    if "whatsapp_target" not in existing:
        connection.execute("ALTER TABLE contacts ADD COLUMN whatsapp_target TEXT")


def _read_json(file_name: str) -> List[Dict[str, Any]]:
    """Read a JSON list from `friday/data/`."""
    with (DATA_DIR / file_name).open("r", encoding="utf-8") as file:
        return json.load(file)


def _table_is_empty(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(f"SELECT 1 FROM {table_name} LIMIT 1").fetchone()
    return row is None


def seed_database_from_json(db_path: Path | str | None = None) -> None:
    """Seed local data once into empty tables."""
    with get_connection(db_path) as connection:
        if _table_is_empty(connection, "tasks"):
            tasks = _read_json("sample_tasks.json")
            prepared_tasks = []
            for item in tasks:
                if not isinstance(item, dict):
                    continue
                prepared_tasks.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("title", "Ohne Titel"),
                        "category": item.get("category"),
                        "status": item.get("status", "open"),
                        "due_date": item.get("due_date"),
                        "notes": item.get("notes", ""),
                        "priority": item.get("priority"),
                        "recurrence": item.get("recurrence"),
                    }
                )
            connection.executemany(
                """
                INSERT INTO tasks (id, title, category, status, due_date, notes, priority, recurrence)
                VALUES (:id, :title, :category, :status, :due_date, :notes, :priority, :recurrence)
                """,
                prepared_tasks,
            )

        if _table_is_empty(connection, "messages"):
            messages = _read_json("sample_messages.json")
            prepared_messages = []
            for item in messages:
                if not isinstance(item, dict):
                    continue
                prepared_messages.append(
                    {
                        "id": item.get("id"),
                        "sender": item.get("sender", "Unbekannt"),
                        "text": item.get("text", ""),
                        "received_at": item.get("received_at"),
                        "contact_type": item.get("contact_type"),
                    }
                )
            connection.executemany(
                """
                INSERT INTO messages (id, sender, text, received_at, contact_type)
                VALUES (:id, :sender, :text, :received_at, :contact_type)
                """,
                prepared_messages,
            )

        if _table_is_empty(connection, "calendar_items"):
            calendar_items = _read_json("sample_calendar.json")
            prepared_calendar = []
            for item in calendar_items:
                if not isinstance(item, dict):
                    continue
                prepared_calendar.append(
                    {
                        "id": item.get("id"),
                        "title": item.get("title", "Kalendereintrag"),
                        "start": item.get("start"),
                        "end": item.get("end"),
                        "item_type": item.get("item_type", item.get("type", "busy")),
                        "date": item.get("date"),
                    }
                )
            connection.executemany(
                """
                INSERT INTO calendar_items (id, title, start, end, item_type, date)
                VALUES (:id, :title, :start, :end, :item_type, :date)
                """,
                prepared_calendar,
            )

        if _table_is_empty(connection, "contacts"):
            contacts = _read_json("sample_contacts.json")
            prepared_contacts = []
            for item in contacts:
                if not isinstance(item, dict):
                    continue
                prepared_contacts.append(
                    {
                        "id": item.get("id"),
                        "name": item.get("name", "Unbekannt"),
                        "contact_type": item.get("contact_type", item.get("category", "other")),
                        "notes": item.get("notes", ""),
                        "email_address": item.get("email_address"),
                        "whatsapp_target": item.get("whatsapp_target"),
                    }
                )
            connection.executemany(
                """
                INSERT INTO contacts (id, name, contact_type, notes, email_address, whatsapp_target)
                VALUES (:id, :name, :contact_type, :notes, :email_address, :whatsapp_target)
                """,
                prepared_contacts,
            )


def setup_local_database(
    db_path: Path | str | None = None,
    seed_demo_data: bool | None = None,
) -> None:
    """Run local initialization in the correct order."""
    ensure_local_data_dir(db_path)
    initialize_database(db_path)
    should_seed = config.DEMO_MODE if seed_demo_data is None else seed_demo_data
    if db_path is not None and seed_demo_data is None:
        should_seed = True
    if should_seed:
        seed_database_from_json(db_path)
