"""Tests for the read-only local data import dry-run model."""

from __future__ import annotations

import json
from pathlib import Path

from friday.app.local_data_export_preview import (
    LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
    build_local_data_export_preview,
)
from friday.app.local_data_export_writer import LocalDataExportPayload, write_local_data_export
from friday.app.local_data_import_dry_run import build_local_data_import_dry_run
from friday.app.local_data_import_manifest_reader import read_local_data_import_manifest


def _payload() -> LocalDataExportPayload:
    return LocalDataExportPayload(
        tasks=(
            {
                "id": 1,
                "title": "Dry Run Aufgabe",
                "status": "open",
                "category": "arbeit",
                "due_date": "2026-07-07",
                "priority": "high",
            },
        ),
        contact_contexts=(
            {
                "contact_id": "contact-1",
                "display_name": "Max Mustermann",
                "normalized_name": "max mustermann",
                "contact_type": "kunde",
                "source_context": "test",
                "updated_at": "2026-07-07T20:00:00",
            },
        ),
        review_suggestions=(
            {
                "suggestion_id": 1,
                "type": "message",
                "status": "approved",
                "title": "Antwort vorbereiten",
            },
        ),
        safety_status={
            "ENABLE_REAL_EMAIL": False,
            "ENABLE_REAL_WHATSAPP": False,
            "ENABLE_REAL_SMS": False,
            "ENABLE_REAL_CALENDAR": False,
            "ENABLE_REAL_WEATHER": False,
            "ENABLE_REAL_MUSIC": False,
            "REQUIRE_USER_APPROVAL": True,
            "USE_SQLITE_STORAGE": True,
        },
    )


def _write_export(tmp_path: Path) -> Path:
    preview = build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
        timestamp="20260707_233000",
    )
    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )
    assert result.persisted is True
    assert result.target_path is not None
    return Path(result.target_path)


def _manifest_result(export_root: Path, project_root: Path):
    return read_local_data_import_manifest(
        manifest_path=export_root / "manifest.json",
        project_root=project_root,
    )


def test_local_data_import_dry_run_allows_valid_export_without_writing(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    manifest_result = _manifest_result(export_root, tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    checked = {section.relative_path for section in result.sections_checked}
    assert result.allowed is True
    assert result.manifest_valid is True
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False
    assert "tasks/tasks.json" in checked
    assert "safety/safety_status.json" in checked
    assert before == after


def test_local_data_import_dry_run_blocks_blocked_manifest(tmp_path: Path) -> None:
    export_root = tmp_path / "local_data" / "exports" / "missing"
    manifest_result = read_local_data_import_manifest(
        manifest_path=export_root / "manifest.json",
        project_root=tmp_path,
    )

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "manifest_blocked" in result.blocked_reasons


def test_local_data_import_dry_run_blocks_export_root_outside_exports(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    manifest_result = _manifest_result(export_root, tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()

    result = build_local_data_import_dry_run(
        export_root=outside,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "export_root_outside_exports" in result.blocked_reasons


def test_local_data_import_dry_run_blocks_missing_expected_file(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    (export_root / "tasks" / "tasks.json").unlink()
    manifest_result = _manifest_result(export_root, tmp_path)

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "expected_file_missing" in result.blocked_reasons
    assert "tasks/tasks.json" in result.missing_files


def test_local_data_import_dry_run_blocks_invalid_json_file(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    (export_root / "tasks" / "tasks.json").write_text("{bad", encoding="utf-8")
    manifest_result = _manifest_result(export_root, tmp_path)

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "invalid_json_file" in result.blocked_reasons
    assert "tasks/tasks.json" in result.invalid_files


def test_local_data_import_dry_run_blocks_sensitive_contact_fields(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    contact_file = export_root / "contacts" / "contact_contexts.json"
    contacts = json.loads(contact_file.read_text(encoding="utf-8"))
    contacts[0]["private_health_data"] = "nicht importieren"
    contact_file.write_text(json.dumps(contacts), encoding="utf-8")
    manifest_result = _manifest_result(export_root, tmp_path)

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "forbidden_export_content" in result.blocked_reasons


def test_local_data_import_dry_run_blocks_raw_review_message_text(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    review_file = export_root / "review" / "review_suggestions.json"
    suggestions = json.loads(review_file.read_text(encoding="utf-8"))
    suggestions[0]["message_text"] = "roher privater Nachrichtentext"
    review_file.write_text(json.dumps(suggestions), encoding="utf-8")
    manifest_result = _manifest_result(export_root, tmp_path)

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "forbidden_export_content" in result.blocked_reasons


def test_local_data_import_dry_run_blocks_enabled_safety_flag(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    safety_file = export_root / "safety" / "safety_status.json"
    safety = json.loads(safety_file.read_text(encoding="utf-8"))
    safety["ENABLE_REAL_EMAIL"] = True
    safety_file.write_text(json.dumps(safety), encoding="utf-8")
    manifest_result = _manifest_result(export_root, tmp_path)

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "safety_flags_enabled" in result.blocked_reasons


def test_local_data_import_dry_run_blocks_external_lookup_marker(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    tasks_file = export_root / "tasks" / "tasks.json"
    tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
    tasks[0]["external_lookup_used"] = True
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")
    manifest_result = _manifest_result(export_root, tmp_path)

    result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert "external_lookup_used" in result.blocked_reasons
