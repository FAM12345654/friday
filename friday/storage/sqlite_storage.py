"""Compatibility wrapper for older import paths.

Friday moved storage logic to `database.py` and `repositories.py`.
This keeps old imports alive with the same behaviour.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence
import sqlite3

from friday.storage.database import get_connection
from friday.storage.database import setup_local_database as ensure_database


def query_all(connection: sqlite3.Connection, sql: str, params: Sequence[Any] = ()) -> list[Dict[str, Any]]:
    """Run a query and return rows as simple dictionaries."""
    cursor = connection.execute(sql, params)
    return [dict(row) for row in cursor.fetchall()]
