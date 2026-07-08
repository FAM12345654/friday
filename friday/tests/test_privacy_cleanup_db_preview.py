"""Tests for the read-only SQLite privacy cleanup preview model."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from friday.app.privacy_cleanup_db_preview import (
    CONTACT_DB_CLEANUP_TOKEN,
    REVIEW_DB_CLEANUP_TOKEN,
    build_privacy_cleanup_db_preview,
)
from friday.storage.database import setup_local_database


def _db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path)
    return db_path


def _insert_review_candidates(db_path: Path) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO message_suggestions (
                message_id,
                suggestion_type,
                draft_text,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (1001, "reply", "Nicht ausgeben", "rejected"),
        )
        connection.execute(
            """
            INSERT INTO message_suggestions (
                message_id,
                suggestion_type,
                draft_text,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (1002, "reply", "Pending bleibt gesperrt", "pending"),
        )
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("Konvertierte Aufgabe", "arbeit", "open", None, "", "medium"),
        )
        created_task_id = int(cursor.lastrowid)
        connection.execute(
            """
            INSERT INTO task_suggestions (
                message_id,
                title,
                status,
                created_task_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (1003, "Nicht ausgeben", "converted", created_task_id),
        )
        connection.execute(
            """
            INSERT INTO task_suggestions (
                message_id,
                title,
                status,
                created_task_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (1004, "Pending bleibt gesperrt", "pending", None),
        )


def _insert_contact_context(db_path: Path, contact_id: str = "contact-01") -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO contact_contexts (
                contact_id,
                display_name,
                normalized_name,
                contact_type,
                source_context,
                user_approved_persistence,
                sensitivity_checked,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contact_id,
                "Max Mustermann",
                "max mustermann",
                "kunde",
                "test",
                1,
                1,
                "2026-07-08T10:00:00",
                "2026-07-08T10:00:00",
            ),
        )


def _table_count(db_path: Path, table_name: str) -> int:
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    return int(row[0])


def test_db_preview_is_read_only(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_review_candidates(db_path)
    _insert_contact_context(db_path)
    before_messages = _table_count(db_path, "message_suggestions")
    before_tasks = _table_count(db_path, "task_suggestions")
    before_contacts = _table_count(db_path, "contact_contexts")

    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        contact_id="contact-01",
    )

    assert preview.writes_performed is False
    assert preview.deletes_performed is False
    assert preview.schema_changed is False
    assert preview.external_lookup_used is False
    assert _table_count(db_path, "message_suggestions") == before_messages
    assert _table_count(db_path, "task_suggestions") == before_tasks
    assert _table_count(db_path, "contact_contexts") == before_contacts


def test_db_preview_counts_only_safe_review_candidates(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_review_candidates(db_path)

    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Review-History",),
    )
    item = preview.items[0]

    assert item.area_name == "Review-History"
    assert item.allowed is True
    assert item.preview_status == "preview_only"
    assert item.candidate_count == 2
    assert item.requires_token == REVIEW_DB_CLEANUP_TOKEN
    assert item.sensitive_content_hidden is True


def test_db_preview_contact_context_requires_exact_selection(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)
    _insert_contact_context(db_path, "contact-01")

    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Kontakt-Kontext",),
        contact_id="contact-01",
    )
    item = preview.items[0]

    assert item.area_name == "Kontakt-Kontext"
    assert item.allowed is True
    assert item.candidate_count == 1
    assert item.requires_token == CONTACT_DB_CLEANUP_TOKEN
    assert item.status_filter == "contact_id = <ausgewaehlt>"


def test_db_preview_blocks_contact_context_without_selection(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Kontakt-Kontext",),
    )
    item = preview.items[0]

    assert item.allowed is False
    assert item.preview_status == "blocked"
    assert item.candidate_count == 0
    assert item.blocked_reasons == ("missing_contact_selection",)
    assert "missing_contact_selection" in preview.blocked_actions


def test_db_preview_blocks_active_tasks_and_schema(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Aufgaben", "Datenbankschema"),
    )
    items = {item.area_name: item for item in preview.items}

    assert items["Aufgaben"].allowed is False
    assert items["Aufgaben"].blocked_reasons == ("task_cleanup_requires_separate_gate",)
    assert items["Datenbankschema"].allowed is False
    assert items["Datenbankschema"].blocked_reasons == ("schema_cleanup_blocked",)


def test_db_preview_blocks_unknown_area_without_future_gate(tmp_path: Path) -> None:
    db_path = _db_path(tmp_path)

    preview = build_privacy_cleanup_db_preview(
        db_path=db_path,
        requested_areas=("Unbekannter Bereich",),
    )
    item = preview.items[0]

    assert item.allowed is False
    assert item.blocked_reasons == ("missing_future_gate",)
    assert item.requires_token == "nicht freigegeben"


def test_db_preview_uses_read_only_sqlite_connection(tmp_path: Path) -> None:
    missing_db_path = tmp_path / "missing.db"

    with pytest.raises(sqlite3.OperationalError):
        build_privacy_cleanup_db_preview(db_path=missing_db_path)
