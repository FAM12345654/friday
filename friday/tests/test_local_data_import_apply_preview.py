"""Tests for the side-effect-free local data import apply preview model."""

from __future__ import annotations

import json
from pathlib import Path

from friday.app.local_data_export_preview import (
    LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
    build_local_data_export_preview,
)
from friday.app.local_data_export_writer import LocalDataExportPayload, write_local_data_export
from friday.app.local_data_import_apply_preview import (
    LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
    build_local_data_import_apply_preview,
)
from friday.app.local_data_import_dry_run import build_local_data_import_dry_run
from friday.app.local_data_import_manifest_reader import read_local_data_import_manifest


def _payload() -> LocalDataExportPayload:
    return LocalDataExportPayload(
        tasks=(
            {
                "id": 1,
                "title": "Apply Preview Aufgabe",
                "status": "open",
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
        timestamp="20260707_234500",
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


def _import_inputs(export_root: Path, project_root: Path):
    manifest_result = read_local_data_import_manifest(
        manifest_path=export_root / "manifest.json",
        project_root=project_root,
    )
    dry_run_result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=project_root,
    )
    return manifest_result, dry_run_result


def test_local_data_import_apply_preview_ready_with_backup_without_writing(
    tmp_path: Path,
) -> None:
    export_root = _write_export(tmp_path)
    manifest_result, dry_run_result = _import_inputs(export_root, tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = build_local_data_import_apply_preview(
        manifest_result=manifest_result,
        dry_run_result=dry_run_result,
        backup_ready=True,
    )

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert result.status == "preview_ready"
    assert result.allowed_to_request_token is True
    assert result.approval_token_required == LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False
    assert {section.name for section in result.sections} == {
        "tasks",
        "contact_contexts",
        "review_suggestions",
    }
    assert before == after


def test_local_data_import_apply_preview_blocks_without_backup(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    manifest_result, dry_run_result = _import_inputs(export_root, tmp_path)

    result = build_local_data_import_apply_preview(
        manifest_result=manifest_result,
        dry_run_result=dry_run_result,
        backup_ready=False,
    )

    assert result.status == "blocked"
    assert result.allowed_to_request_token is False
    assert "backup_required" in result.blocked_reasons


def test_local_data_import_apply_preview_blocks_dry_run_failures(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    (export_root / "tasks" / "tasks.json").unlink()
    manifest_result, dry_run_result = _import_inputs(export_root, tmp_path)

    result = build_local_data_import_apply_preview(
        manifest_result=manifest_result,
        dry_run_result=dry_run_result,
        backup_ready=True,
    )

    assert result.status == "blocked"
    assert result.allowed_to_request_token is False
    assert "dry_run_blocked" in result.blocked_reasons


def test_local_data_import_apply_preview_invalid_when_manifest_blocked(tmp_path: Path) -> None:
    export_root = tmp_path / "local_data" / "exports" / "missing"
    manifest_result = read_local_data_import_manifest(
        manifest_path=export_root / "manifest.json",
        project_root=tmp_path,
    )
    dry_run_result = build_local_data_import_dry_run(
        export_root=export_root,
        manifest_result=manifest_result,
        project_root=tmp_path,
    )

    result = build_local_data_import_apply_preview(
        manifest_result=manifest_result,
        dry_run_result=dry_run_result,
        backup_ready=True,
    )

    assert result.status == "invalid"
    assert "manifest_blocked" in result.blocked_reasons
    assert result.sections == ()


def test_local_data_import_apply_preview_blocks_conflicts(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    manifest_result, dry_run_result = _import_inputs(export_root, tmp_path)

    result = build_local_data_import_apply_preview(
        manifest_result=manifest_result,
        dry_run_result=dry_run_result,
        backup_ready=True,
        conflict_warnings=("Task-ID 1 existiert bereits.",),
    )

    assert result.status == "blocked"
    assert "conflicts_present" in result.blocked_reasons
    assert "Task-ID 1 existiert bereits." in result.warnings


def test_local_data_import_apply_preview_blocks_external_lookup_marker(tmp_path: Path) -> None:
    export_root = _write_export(tmp_path)
    tasks_file = export_root / "tasks" / "tasks.json"
    tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
    tasks[0]["external_lookup_used"] = True
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")
    manifest_result, dry_run_result = _import_inputs(export_root, tmp_path)

    result = build_local_data_import_apply_preview(
        manifest_result=manifest_result,
        dry_run_result=dry_run_result,
        backup_ready=True,
    )

    assert result.status == "blocked"
    assert "dry_run_blocked" in result.blocked_reasons
    assert result.external_lookup_used is False
