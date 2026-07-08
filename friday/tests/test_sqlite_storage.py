"""Compatibility tests for the old sqlite_storage module."""

from __future__ import annotations

import sqlite3

from friday.storage.sqlite_storage import ensure_database


def _count_rows(connection: sqlite3.Connection, table: str) -> int:
    return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def test_sqlite_storage_wrapper_creates_database(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    ensure_database(db_file)

    with sqlite3.connect(db_file) as connection:
        assert _count_rows(connection, "tasks") >= 1
        assert _count_rows(connection, "messages") >= 1
        assert _count_rows(connection, "calendar_items") >= 1
        assert _count_rows(connection, "contacts") >= 1
