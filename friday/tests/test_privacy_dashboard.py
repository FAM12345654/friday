"""Tests for the read-only privacy dashboard model."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from friday.app.privacy_dashboard import (
    build_privacy_dashboard_summary,
    collect_privacy_dashboard_local_counts,
)
from friday.storage.database import initialize_database


def _write_count_rows(db_path: Path) -> None:
    initialize_database(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES ('Task 1', 'work', 'open', NULL, '', 'normal')
            """
        )
        connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES ('Task 2', 'home', 'done', NULL, '', 'low')
            """
        )
        connection.execute(
            """
            INSERT INTO contacts (name, contact_type, notes)
            VALUES ('Ada', 'work', '')
            """
        )
        connection.execute(
            """
            INSERT INTO contact_contexts (
                contact_id,
                display_name,
                normalized_name,
                contact_type,
                source_context,
                created_at,
                updated_at
            )
            VALUES (
                'ada',
                'Ada',
                'ada',
                'work',
                'test',
                '2026-07-08T10:00:00+00:00',
                '2026-07-08T10:00:00+00:00'
            )
            """
        )
        connection.execute(
            """
            INSERT INTO message_suggestions (message_id, draft_text, status)
            VALUES (1, 'Draft', 'pending')
            """
        )
        connection.execute(
            """
            INSERT INTO task_suggestions (message_id, title, status)
            VALUES (1, 'Review Task', 'pending')
            """
        )
        connection.execute(
            """
            INSERT INTO calendar_suggestions (message_id, slot_date, start, end, status)
            VALUES (1, '2026-07-08', '10:00', '11:00', 'pending')
            """
        )


def test_privacy_dashboard_collects_local_counts_read_only(tmp_path) -> None:
    local_data = tmp_path / "local_data"
    db_path = local_data / "friday.db"
    (local_data / "backups" / "friday_backup_1").mkdir(parents=True)
    (local_data / "restores" / "friday_restore_1").mkdir(parents=True)
    _write_count_rows(db_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    counts = collect_privacy_dashboard_local_counts(
        local_data_dir=local_data,
        database_path=db_path,
    )

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert counts.database_available is True
    assert counts.database_readable is True
    assert counts.task_count == 2
    assert counts.contact_count == 1
    assert counts.contact_context_count == 1
    assert counts.review_suggestion_count == 3
    assert counts.backup_count == 1
    assert counts.restore_copy_count == 1
    assert before == after


def test_privacy_dashboard_missing_database_count_does_not_create_paths(tmp_path) -> None:
    local_data = tmp_path / "local_data"
    db_path = local_data / "friday.db"

    counts = collect_privacy_dashboard_local_counts(
        local_data_dir=local_data,
        database_path=db_path,
    )

    assert counts.database_available is False
    assert counts.database_readable is False
    assert counts.task_count is None
    assert counts.contact_count is None
    assert counts.contact_context_count is None
    assert counts.review_suggestion_count is None
    assert counts.backup_count == 0
    assert counts.restore_copy_count == 0
    assert not local_data.exists()


def test_privacy_dashboard_summary_is_local_and_read_only(tmp_path) -> None:
    summary = build_privacy_dashboard_summary(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
        database_path=tmp_path / "local_data" / "friday.db",
    )

    assert summary.app_name == "Friday"
    assert summary.local_mode is True
    assert summary.sqlite_storage is True
    assert summary.writes_performed is False
    assert summary.external_lookup_used is False


def test_privacy_dashboard_does_not_create_local_paths(tmp_path) -> None:
    local_data_dir = tmp_path / "local_data"
    database_path = local_data_dir / "friday.db"

    build_privacy_dashboard_summary(
        project_root=tmp_path,
        local_data_dir=local_data_dir,
        database_path=database_path,
    )

    assert not local_data_dir.exists()
    assert not database_path.exists()


def test_privacy_dashboard_contains_expected_safety_flags(tmp_path) -> None:
    summary = build_privacy_dashboard_summary(project_root=tmp_path)
    flags = {flag.name: flag for flag in summary.safety_flags}

    assert flags["ENABLE_REAL_EMAIL"].value is False
    assert flags["ENABLE_REAL_WHATSAPP"].value is False
    assert flags["ENABLE_REAL_SMS"].value is False
    assert flags["ENABLE_REAL_CALENDAR"].value is True
    assert flags["ENABLE_REAL_CALENDAR"].status == "intended"
    assert flags["ENABLE_REAL_WEATHER"].value is False
    assert flags["ENABLE_REAL_MUSIC"].value is False
    assert flags["REQUIRE_USER_APPROVAL"].value is True
    assert flags["USE_SQLITE_STORAGE"].value is True
    assert all(
        flag.status == "safe"
        for flag in flags.values()
        if flag.name != "ENABLE_REAL_CALENDAR"
    )


def test_privacy_dashboard_external_actions_are_disabled(tmp_path) -> None:
    summary = build_privacy_dashboard_summary(project_root=tmp_path)
    actions = {action.name: action for action in summary.external_actions}

    assert summary.external_actions
    assert actions["Kalender"].enabled is True
    assert actions["Kalender"].status == "aktiviert, pro Termin hart gegatet"
    assert all(
        action.enabled is False
        for action in summary.external_actions
        if action.name != "Kalender"
    )


def test_privacy_dashboard_data_areas_hide_sensitive_details(tmp_path) -> None:
    summary = build_privacy_dashboard_summary(project_root=tmp_path)

    assert summary.data_areas
    assert all(area.sensitive_details_hidden is True for area in summary.data_areas)
    assert {area.name for area in summary.data_areas} == {
        "Aufgaben",
        "Kontakte",
        "Kontakt-Kontexte",
        "Review-Vorschlaege",
        "Backups",
        "Restore-Kopien",
    }


def test_privacy_dashboard_accepts_summarized_counts(tmp_path) -> None:
    summary = build_privacy_dashboard_summary(
        project_root=tmp_path,
        task_count=3,
        contact_count=2,
        review_suggestion_count=4,
        backup_count=1,
        restore_copy_count=0,
    )
    counts = {area.name: area.count_label for area in summary.data_areas}

    assert counts["Aufgaben"] == "3"
    assert counts["Kontakte"] == "2"
    assert counts["Kontakt-Kontexte"] == "2"
    assert counts["Review-Vorschlaege"] == "4"
    assert counts["Backups"] == "1"
    assert counts["Restore-Kopien"] == "0"


def test_privacy_dashboard_lists_hard_gated_actions(tmp_path) -> None:
    summary = build_privacy_dashboard_summary(project_root=tmp_path)
    tokens = {action.name: action.token for action in summary.gated_actions}

    assert tokens["Kontakt-Kontext sichern"] == "SPEICHERN"
    assert tokens["Kontakt-Kontext entfernen"] == "KONTAKT LÖSCHEN"
    assert tokens["Person vergessen"] == "PERSON VERGESSEN"
    assert tokens["Obsidian-Notiz"] == "OBSIDIAN SCHREIBEN"
    assert tokens["Backup erstellen"] == "BACKUP ERSTELLEN"
    assert tokens["Restore-Kopie erstellen"] == "RESTORE AUSFUEHREN"
    assert all(action.status == "hart gegatet" for action in summary.gated_actions)


def test_privacy_dashboard_paths_can_be_overridden(tmp_path) -> None:
    project_root = tmp_path / "project"
    local_data_dir = tmp_path / "custom_data"
    database_path = local_data_dir / "custom.db"

    summary = build_privacy_dashboard_summary(
        project_root=project_root,
        local_data_dir=local_data_dir,
        database_path=database_path,
    )

    assert summary.project_root == str(project_root)
    assert summary.local_data_dir == str(local_data_dir)
    assert summary.database_path == str(database_path)
    assert str(local_data_dir / "backups") in {
        area.path for area in summary.data_areas
    }
