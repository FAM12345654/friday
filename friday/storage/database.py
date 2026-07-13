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
                recurrence TEXT,
                snoozed_until TEXT
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                sender TEXT NOT NULL,
                text TEXT NOT NULL,
                received_at TEXT,
                contact_type TEXT,
                is_spam INTEGER NOT NULL DEFAULT 0
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
                whatsapp_target TEXT,
                betreuer TEXT
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

            CREATE TABLE IF NOT EXISTS account_policies (
                id INTEGER PRIMARY KEY,
                provider TEXT NOT NULL,
                label TEXT NOT NULL,
                role TEXT NOT NULL,
                access TEXT NOT NULL,
                include_filters TEXT NOT NULL,
                exclude_filters TEXT NOT NULL,
                transform TEXT NOT NULL DEFAULT '{}',
                notes TEXT,
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS calendar_entries (
                id INTEGER PRIMARY KEY,
                provider TEXT NOT NULL,
                provider_event_id TEXT,
                policy_id INTEGER,
                title TEXT NOT NULL,
                start TEXT NOT NULL,
                end TEXT NOT NULL,
                location TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS calendar_cache (
                id INTEGER PRIMARY KEY,
                policy_id INTEGER,
                provider TEXT NOT NULL,
                range_start TEXT NOT NULL,
                range_end TEXT NOT NULL,
                payload TEXT NOT NULL,
                cached_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS calendar_view_prefs (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                range_preset TEXT NOT NULL DEFAULT 'heute',
                custom_from TEXT,
                custom_to TEXT,
                day_start TEXT NOT NULL DEFAULT '00:00',
                day_end TEXT NOT NULL DEFAULT '23:59',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS email_send_log (
                id INTEGER PRIMARY KEY,
                sent_at TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                message_id TEXT,
                status TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS whatsapp_messages (
                id INTEGER PRIMARY KEY,
                chat_id TEXT NOT NULL,
                sender_name TEXT,
                sender_number_hash TEXT,
                body TEXT NOT NULL,
                received_at TEXT NOT NULL,
                processed INTEGER NOT NULL DEFAULT 0,
                suggestion_created INTEGER NOT NULL DEFAULT 0,
                is_spam INTEGER NOT NULL DEFAULT 0,
                UNIQUE (chat_id, received_at)
            );

            CREATE TABLE IF NOT EXISTS ms_mail_messages (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL DEFAULT 'ms_mail',
                account_id TEXT NOT NULL DEFAULT 'default',
                account_username TEXT,
                message_id TEXT NOT NULL UNIQUE,
                provider_message_id TEXT,
                sender TEXT,
                subject TEXT,
                received_at TEXT,
                snippet TEXT,
                body_full TEXT,
                body_fetched_at TEXT,
                processed INTEGER NOT NULL DEFAULT 0,
                suggestion_created INTEGER NOT NULL DEFAULT 0,
                is_spam INTEGER NOT NULL DEFAULT 0,
                recipients TEXT,
                recipients_json TEXT,
                relevant_for_user INTEGER NOT NULL DEFAULT 1,
                relevance_reason TEXT,
                relevance_method TEXT NOT NULL DEFAULT 'deterministic'
            );

            CREATE TABLE IF NOT EXISTS blocked_senders (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                sender_key TEXT NOT NULL,
                label TEXT,
                created_at TEXT NOT NULL,
                UNIQUE (source, sender_key)
            );

            CREATE TABLE IF NOT EXISTS mailbox_cleanup_log (
                id INTEGER PRIMARY KEY,
                account_id TEXT NOT NULL,
                provider_message_id TEXT NOT NULL,
                sender TEXT NOT NULL DEFAULT '',
                subject TEXT NOT NULL DEFAULT '',
                from_folder TEXT NOT NULL DEFAULT 'INBOX',
                to_label TEXT NOT NULL,
                moved_at TEXT NOT NULL,
                undone INTEGER NOT NULL DEFAULT 0,
                undone_at TEXT,
                source TEXT NOT NULL DEFAULT 'imap_mail'
            );

            CREATE TABLE IF NOT EXISTS learning_questions (
                id INTEGER PRIMARY KEY,
                kind TEXT NOT NULL,
                subject_ref TEXT NOT NULL,
                question_text TEXT NOT NULL,
                options_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                answered_at TEXT,
                UNIQUE (kind, subject_ref)
            );

            CREATE TABLE IF NOT EXISTS learned_rules (
                id INTEGER PRIMARY KEY,
                kind TEXT NOT NULL,
                key TEXT NOT NULL,
                value_json TEXT NOT NULL,
                source_question_id INTEGER,
                created_at TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                UNIQUE (kind, key)
            );

            CREATE TABLE IF NOT EXISTS semantic_index (
                id INTEGER PRIMARY KEY,
                source TEXT NOT NULL,
                source_id TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                text TEXT NOT NULL,
                embedding_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE (source, source_id)
            );
            """
        )
        _ensure_task_priority_column(connection)
        _ensure_task_recurrence_column(connection)
        _ensure_task_snooze_column(connection)
        _ensure_contact_target_columns(connection)
        _ensure_account_policy_transform_column(connection)
        _ensure_message_spam_columns(connection)
        _ensure_ms_mail_message_account_columns(connection)


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


def _ensure_task_snooze_column(connection: sqlite3.Connection) -> None:
    """Add snoozed_until column for local task snoozing."""
    columns = connection.execute("PRAGMA table_info(tasks)").fetchall()
    if not any(column[1] == "snoozed_until" for column in columns):
        connection.execute("ALTER TABLE tasks ADD COLUMN snoozed_until TEXT")


def _ensure_contact_target_columns(connection: sqlite3.Connection) -> None:
    """Add optional local contact target fields for draft routing."""
    columns = connection.execute("PRAGMA table_info(contacts)").fetchall()
    existing = {column[1] for column in columns}
    if "email_address" not in existing:
        connection.execute("ALTER TABLE contacts ADD COLUMN email_address TEXT")
    if "whatsapp_target" not in existing:
        connection.execute("ALTER TABLE contacts ADD COLUMN whatsapp_target TEXT")
    if "betreuer" not in existing:
        connection.execute("ALTER TABLE contacts ADD COLUMN betreuer TEXT")


def _ensure_account_policy_transform_column(connection: sqlite3.Connection) -> None:
    """Add optional per-policy transform JSON for older local databases."""
    columns = connection.execute("PRAGMA table_info(account_policies)").fetchall()
    existing = {column[1] for column in columns}
    if "transform" not in existing:
        connection.execute(
            "ALTER TABLE account_policies ADD COLUMN transform TEXT NOT NULL DEFAULT '{}'"
        )


def _ensure_message_spam_columns(connection: sqlite3.Connection) -> None:
    """Add local spam-status columns for older message preview databases."""
    for table_name in ("messages", "whatsapp_messages", "ms_mail_messages"):
        columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        existing = {column[1] for column in columns}
        if "is_spam" not in existing:
            connection.execute(
                f"ALTER TABLE {table_name} ADD COLUMN is_spam INTEGER NOT NULL DEFAULT 0"
            )


def _ensure_ms_mail_message_account_columns(connection: sqlite3.Connection) -> None:
    """Add mailbox metadata for older Microsoft mail preview databases."""
    columns = connection.execute("PRAGMA table_info(ms_mail_messages)").fetchall()
    existing = {column[1] for column in columns}
    if "source" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN source TEXT NOT NULL DEFAULT 'ms_mail'")
    if "account_id" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN account_id TEXT NOT NULL DEFAULT 'default'")
    if "account_username" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN account_username TEXT")
    if "provider_message_id" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN provider_message_id TEXT")
        connection.execute(
            """
            UPDATE ms_mail_messages
            SET provider_message_id = message_id
            WHERE provider_message_id IS NULL OR provider_message_id = ''
            """
        )
    if "recipients_json" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN recipients_json TEXT")
    if "recipients" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN recipients TEXT")
        connection.execute(
            """
            UPDATE ms_mail_messages
            SET recipients = recipients_json
            WHERE recipients IS NULL AND recipients_json IS NOT NULL
            """
        )
    if "body_full" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN body_full TEXT")
    if "body_fetched_at" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN body_fetched_at TEXT")
    if "relevant_for_user" not in existing:
        connection.execute(
            "ALTER TABLE ms_mail_messages ADD COLUMN relevant_for_user INTEGER NOT NULL DEFAULT 1"
        )
    if "relevance_reason" not in existing:
        connection.execute("ALTER TABLE ms_mail_messages ADD COLUMN relevance_reason TEXT")
    if "relevance_method" not in existing:
        connection.execute(
            "ALTER TABLE ms_mail_messages ADD COLUMN relevance_method TEXT NOT NULL DEFAULT 'deterministic'"
        )


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
                        "betreuer": item.get("betreuer"),
                    }
                )
            connection.executemany(
                """
                INSERT INTO contacts (id, name, contact_type, notes, email_address, whatsapp_target, betreuer)
                VALUES (:id, :name, :contact_type, :notes, :email_address, :whatsapp_target, :betreuer)
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
