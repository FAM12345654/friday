"""Tests for Friday local SQLite setup and seeding."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from friday.config import (
    DATA_DIR,
    DATABASE_NAME,
    DATABASE_PATH,
    DEMO_DATABASE_NAME,
    DEMO_DATABASE_PATH,
    DEMO_DATE,
    LOCAL_DATA_DIR,
)
from friday.storage import database


def _write_json(file_path: Path, payload: list[dict]) -> None:
    file_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return {row[0] for row in rows}


def _row_count(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def _columns(connection: sqlite3.Connection, table: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def test_database_path_separation() -> None:
    """Storage and seed paths should stay separated."""
    assert DATABASE_PATH == LOCAL_DATA_DIR / DATABASE_NAME
    assert DEMO_DATABASE_PATH == LOCAL_DATA_DIR / DEMO_DATABASE_NAME
    assert DATABASE_PATH != DEMO_DATABASE_PATH
    assert DATABASE_PATH != DATA_DIR / DATABASE_NAME
    assert LOCAL_DATA_DIR.name == "local_data"
    assert DATA_DIR.name == "data"


def test_get_connection_context_manager_closes_handle(tmp_path) -> None:
    """Project DB connections should close after context-manager use on Windows."""
    db_file = tmp_path / "friday.db"
    connection = database.get_connection(db_file)

    with connection as active:
        assert active.execute("SELECT 1").fetchone()[0] == 1

    with pytest.raises(sqlite3.ProgrammingError):
        connection.execute("SELECT 1")


def test_initialize_database_creates_required_tables(tmp_path) -> None:
    """Setup must create all required tables."""
    db_file = tmp_path / "friday.db"
    database.initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        tables = _table_names(connection)
        assert "tasks" in tables
        assert "messages" in tables
        assert "calendar_items" in tables
        assert "calendar_view_prefs" in tables
        assert "contacts" in tables
        assert "priority" in _columns(connection, "tasks")
        assert "recurrence" in _columns(connection, "tasks")


def test_initialize_database_creates_message_suggestions_table(tmp_path) -> None:
    """Setup must create the suggestion table needed for local review."""
    db_file = tmp_path / "friday.db"
    database.initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        tables = _table_names(connection)
        assert "message_suggestions" in tables


def test_initialize_database_creates_calendar_suggestions_table(tmp_path) -> None:
    """Setup must create the calendar suggestion table for local previews."""
    db_file = tmp_path / "friday.db"
    database.initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        tables = _table_names(connection)
        assert "calendar_suggestions" in tables


def test_initialize_database_creates_task_suggestions_table(tmp_path) -> None:
    """Setup must create the task suggestion table for local task conversion."""
    db_file = tmp_path / "friday.db"
    database.initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        tables = _table_names(connection)
        assert "task_suggestions" in tables


def test_seed_database_from_json_inserts_demo_data(tmp_path) -> None:
    """Seeding reads friday/data JSON and should be idempotent."""
    db_file = tmp_path / "friday.db"
    database.initialize_database(db_file)
    database.seed_database_from_json(db_file)
    with sqlite3.connect(db_file) as connection:
        first_counts = {
            "tasks": _row_count(connection, "tasks"),
            "messages": _row_count(connection, "messages"),
            "calendar_items": _row_count(connection, "calendar_items"),
            "contacts": _row_count(connection, "contacts"),
        }
        for count in first_counts.values():
            assert count >= 1

    # Seed again must not duplicate the same demo data.
    database.seed_database_from_json(db_file)
    with sqlite3.connect(db_file) as connection:
        assert _row_count(connection, "tasks") == first_counts["tasks"]
        assert _row_count(connection, "messages") == first_counts["messages"]
        assert _row_count(connection, "calendar_items") == first_counts["calendar_items"]
        assert _row_count(connection, "contacts") == first_counts["contacts"]


def test_initialize_database_adds_priority_column_to_existing_schema(tmp_path) -> None:
    """Legacy tables without priority must be migrated in-place."""
    db_file = tmp_path / "legacy.db"
    with sqlite3.connect(db_file) as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                status TEXT,
                due_date TEXT,
                notes TEXT
            );
            """
        )
        connection.execute(
            "INSERT INTO tasks (title, category, status, due_date, notes) VALUES (?, ?, ?, ?, ?)",
            ("Alte Aufgabe", "arbeit", "open", "2026-07-05", "alt"),
        )

    database.initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        assert "priority" in _columns(connection, "tasks")
        assert connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 1
        assert connection.execute("SELECT priority FROM tasks").fetchone()[0] is None
        assert "recurrence" in _columns(connection, "tasks")


def test_initialize_database_is_idempotent_for_recurrence_column(tmp_path) -> None:
    """Running setup twice must not add duplicate recurrence columns."""
    db_file = tmp_path / "recurrence.db"

    database.initialize_database(db_file)
    database.initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        columns = [row[1] for row in connection.execute("PRAGMA table_info(tasks)").fetchall()]
        assert columns.count("recurrence") == 1


def test_seed_database_from_json_writes_priority_if_present(tmp_path, monkeypatch) -> None:
    """Seeding must keep priority values from sample json when they are provided."""
    seed_dir = tmp_path / "seed"
    seed_dir.mkdir()
    _write_json(
        seed_dir / "sample_tasks.json",
        [{"id": 1, "title": "Mit Priorität", "priority": "urgent", "due_date": "2026-07-05"}],
    )
    _write_json(seed_dir / "sample_messages.json", [{"id": 1, "sender": "Test", "text": "Hi"}])
    _write_json(seed_dir / "sample_calendar.json", [])
    _write_json(seed_dir / "sample_contacts.json", [])

    monkeypatch.setattr(database, "DATA_DIR", seed_dir, raising=False)

    db_file = tmp_path / "priority.db"
    database.initialize_database(db_file)
    database.seed_database_from_json(db_file)

    with sqlite3.connect(db_file) as connection:
        assert connection.execute("SELECT priority FROM tasks").fetchone()[0] == "urgent"


def test_seed_database_from_json_handles_missing_optional_fields(
    tmp_path,
    monkeypatch,
) -> None:
    """Missing optional fields in seed JSON must not break seeding."""
    seed_dir = tmp_path / "seed"
    seed_dir.mkdir()

    _write_json(seed_dir / "sample_tasks.json", [{"id": 1, "title": "Minimal Task"}])
    _write_json(
        seed_dir / "sample_messages.json",
        [{"id": 1, "sender": "Minimal Sender", "text": "Hast du Zeit?"}],
    )
    _write_json(
        seed_dir / "sample_calendar.json",
        [
            {
                "id": 1,
                "title": "Minimal Calendar",
                "start": "10:00",
                "end": "11:00",
                "date": "2026-07-05",
            }
        ],
    )
    _write_json(
        seed_dir / "sample_contacts.json",
        [{"id": 1, "name": "Minimal Contact", "category": "friend"}],
    )

    monkeypatch.setattr(database, "DATA_DIR", seed_dir, raising=False)

    db_file = tmp_path / "custom.db"
    database.initialize_database(db_file)
    database.seed_database_from_json(db_file)

    with sqlite3.connect(db_file) as connection:
        assert _row_count(connection, "tasks") == 1
        assert _row_count(connection, "messages") == 1
        assert _row_count(connection, "calendar_items") == 1
        assert _row_count(connection, "contacts") == 1
        assert connection.execute("SELECT status FROM tasks").fetchone()[0] == "open"
        assert connection.execute("SELECT priority FROM tasks").fetchone()[0] is None
        assert (
            connection.execute("SELECT item_type FROM calendar_items").fetchone()[0]
            == "busy"
        )
        assert (
            connection.execute("SELECT contact_type FROM contacts").fetchone()[0]
            == "friend"
        )


def test_setup_local_database_uses_temporary_path(tmp_path) -> None:
    """The full setup function should run through init and seed for any path."""
    db_file = tmp_path / "custom" / "friday.db"
    database.setup_local_database(db_file)

    with sqlite3.connect(db_file) as connection:
        assert _row_count(connection, "tasks") >= 1
        assert _row_count(connection, "calendar_items") >= 1
        # Ensure setup created a day-usable dataset.
        assert (
            connection.execute(
                "SELECT COUNT(*) FROM tasks WHERE due_date = ?",
                (DEMO_DATE,),
            ).fetchone()[0]
            > 0
        )


def test_setup_default_database_without_demo_mode_does_not_seed(tmp_path, monkeypatch) -> None:
    """Real default setup creates tables but leaves user data empty."""
    db_file = tmp_path / "local_data" / "friday.db"
    monkeypatch.setattr(database.config, "LOCAL_DATA_DIR", tmp_path / "local_data")
    monkeypatch.setattr(database.config, "DATABASE_PATH", db_file)
    monkeypatch.setattr(database.config, "DEMO_MODE", False)

    database.setup_local_database()

    with sqlite3.connect(db_file) as connection:
        assert "tasks" in _table_names(connection)
        assert _row_count(connection, "tasks") == 0
        assert _row_count(connection, "messages") == 0
        assert _row_count(connection, "calendar_items") == 0
        assert _row_count(connection, "contacts") == 0


def test_demo_mode_uses_demo_database_and_keeps_work_database_untouched(
    tmp_path,
    monkeypatch,
) -> None:
    """Demo mode writes seed data only into the isolated demo database."""
    local_data = tmp_path / "local_data"
    work_db = local_data / "friday.db"
    demo_db = local_data / "friday_demo.db"
    monkeypatch.setattr(database.config, "LOCAL_DATA_DIR", local_data)
    monkeypatch.setattr(database.config, "DATABASE_PATH", work_db)
    monkeypatch.setattr(database.config, "DEMO_DATABASE_PATH", demo_db)
    monkeypatch.setattr(database.config, "DEMO_MODE", True)

    database.setup_local_database()

    assert demo_db.exists()
    assert not work_db.exists()
    with sqlite3.connect(demo_db) as connection:
        assert _row_count(connection, "tasks") >= 1
        assert _row_count(connection, "messages") >= 1
