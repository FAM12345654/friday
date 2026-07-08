"""Tests for the guarded local data import apply writer prototype."""

from __future__ import annotations

import json
from pathlib import Path

from friday.app.local_data_import_apply_preview import (
    LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
    LocalDataImportApplyPreviewResult,
    LocalDataImportApplyPreviewSection,
)
from friday.app.local_data_import_apply_write_guard import (
    check_local_data_import_apply_write_allowed,
)
from friday.app.local_data_import_apply_writer import apply_local_data_import
from friday.storage.database import get_connection, initialize_database


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _export_root(tmp_path: Path) -> Path:
    root = tmp_path / "local_data" / "exports" / "friday_export_test"
    _write_json(
        root / "tasks" / "tasks.json",
        [
            {
                "title": "Import Aufgabe",
                "category": "arbeit",
                "status": "open",
                "due_date": "2026-07-08",
                "notes": "Aus Export",
                "priority": "high",
            }
        ],
    )
    _write_json(
        root / "contacts" / "contact_contexts.json",
        [
            {
                "contact_id": "contact-import-1",
                "display_name": "Max Import",
                "contact_type": "kunde",
                "source_context": "local_data_export",
                "updated_at": "2026-07-08T10:00:00+00:00",
            }
        ],
    )
    _write_json(
        root / "review" / "review_suggestions.json",
        [
            {
                "suggestion_id": 1001,
                "type": "reply",
                "status": "approved",
                "title": "Importierter Vorschlag",
                "source": "local_data_export",
            }
        ],
    )
    return root


def _section(name: str) -> LocalDataImportApplyPreviewSection:
    return LocalDataImportApplyPreviewSection(
        name=name,
        planned_count=1,
        action="preview_import_or_update",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _preview() -> LocalDataImportApplyPreviewResult:
    return LocalDataImportApplyPreviewResult(
        status="preview_ready",
        allowed_to_request_token=True,
        export_root="local_data/exports/friday_export_test",
        sections=(
            _section("tasks"),
            _section("contact_contexts"),
            _section("review_suggestions"),
        ),
        blocked_reasons=(),
        warnings=(),
        message="Import-Apply-Vorschau ist bereit. Es wurde nichts importiert.",
        backup_required=True,
        backup_ready=True,
        approval_token_required=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _allowed_guard():
    return check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
    )


def _db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "local_data" / "friday.db"
    initialize_database(db_path)
    return db_path


def _count(db_path: Path, table: str) -> int:
    with get_connection(db_path) as connection:
        return int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def test_import_apply_writer_blocks_when_guard_blocks(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)
    guard = check_local_data_import_apply_write_allowed(
        preview=_preview(),
        approval_token="JA",
        scanner_smoke_passed=True,
    )

    result = apply_local_data_import(
        guard_result=guard,
        export_root=root,
        db_path=db_path,
    )

    assert result.applied is False
    assert result.status == "blocked"
    assert "guard_blocked" in result.blocked_reasons
    assert _count(db_path, "tasks") == 0


def test_import_apply_writer_applies_allowed_local_sections(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)

    result = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )

    assert result.applied is True
    assert result.status == "applied"
    assert result.created_counts.tasks == 1
    assert result.created_counts.contact_contexts == 1
    assert result.created_counts.review_suggestions == 1
    assert _count(db_path, "tasks") == 1
    assert _count(db_path, "contact_contexts") == 1
    assert _count(db_path, "message_suggestions") == 1


def test_import_apply_writer_skips_identical_tasks_on_second_apply(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)

    first = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )
    second = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )

    assert first.applied is True
    assert second.applied is True
    assert second.created_counts.tasks == 0
    assert second.skipped_counts.tasks == 1
    assert second.skipped_counts.contact_contexts == 1
    assert second.skipped_counts.review_suggestions == 1
    assert _count(db_path, "tasks") == 1


def test_import_apply_writer_rolls_back_on_task_conflict(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("Import Aufgabe", "anders", "done", None, "Konflikt", "low"),
        )

    result = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )

    assert result.applied is False
    assert result.status == "rolled_back"
    assert result.rollback_used is True
    assert "task_conflict" in result.blocked_reasons
    assert _count(db_path, "tasks") == 1
    assert _count(db_path, "contact_contexts") == 0


def test_import_apply_writer_blocks_sensitive_contact_context_and_rolls_back(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)
    contacts_file = root / "contacts" / "contact_contexts.json"
    contacts = json.loads(contacts_file.read_text(encoding="utf-8"))
    contacts[0]["relationship_context"] = "Diagnose: vertraulich"
    contacts_file.write_text(json.dumps(contacts), encoding="utf-8")

    result = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )

    assert result.applied is False
    assert result.rollback_used is True
    assert "sensitive_contact_context" in result.blocked_reasons
    assert _count(db_path, "tasks") == 0
    assert _count(db_path, "contact_contexts") == 0


def test_import_apply_writer_blocks_missing_export_file(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)
    (root / "tasks" / "tasks.json").unlink()

    result = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )

    assert result.applied is False
    assert result.status == "invalid"
    assert "missing_export_file" in result.blocked_reasons
    assert _count(db_path, "tasks") == 0


def test_import_apply_writer_blocks_invalid_export_payload(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)
    (root / "tasks" / "tasks.json").write_text("{not json", encoding="utf-8")

    result = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )

    assert result.applied is False
    assert result.status == "invalid"
    assert "invalid_export_payload" in result.blocked_reasons
    assert _count(db_path, "tasks") == 0


def test_import_apply_writer_has_safe_flags(tmp_path: Path) -> None:
    root = _export_root(tmp_path)
    db_path = _db_path(tmp_path)

    result = apply_local_data_import(
        guard_result=_allowed_guard(),
        export_root=root,
        db_path=db_path,
    )

    assert result.preview_only is False
    assert result.persisted is True
    assert result.external_action_used is False
    assert result.database_schema_changed is False
