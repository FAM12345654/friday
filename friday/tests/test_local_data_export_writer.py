"""Tests for the guarded local data export writer."""

from __future__ import annotations

import json
from pathlib import Path

from friday.app.local_data_export_guard import REQUIRED_LOCAL_DATA_EXPORT_EXCLUSIONS
from friday.app.local_data_export_preview import (
    LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
    LocalDataExportPreview,
    LocalDataExportSection,
    build_local_data_export_preview,
)
from friday.app.local_data_export_writer import (
    LocalDataExportPayload,
    write_local_data_export,
)


def _payload() -> LocalDataExportPayload:
    return LocalDataExportPayload(
        tasks=(
            {
                "id": 1,
                "title": "Export Aufgabe",
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
                "relationship_context": "Projektkontakt",
                "private_health_data": "nicht exportieren",
            },
        ),
        review_suggestions=(
            {
                "suggestion_id": 10,
                "type": "message",
                "status": "approved",
                "title": "Termin bestaetigen",
                "message_text": "roher privater Text",
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


def _preview(tmp_path: Path, timestamp: str = "20260707_220000") -> LocalDataExportPreview:
    return build_local_data_export_preview(
        project_root=tmp_path,
        local_data_dir=tmp_path / "local_data",
        timestamp=timestamp,
    )


def _fake_preview(target_root: Path) -> LocalDataExportPreview:
    return LocalDataExportPreview(
        target_root=str(target_root),
        sections=(
            LocalDataExportSection(
                name="Aufgaben",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("test",),
            ),
        ),
        excluded_items=REQUIRED_LOCAL_DATA_EXPORT_EXCLUSIONS,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def test_write_local_data_export_writes_expected_files(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    target = Path(result.target_path)
    written_paths = {file.relative_path for file in result.written_files}

    assert result.allowed is True
    assert result.persisted is True
    assert target.exists()
    assert "manifest.json" in written_paths
    assert "tasks/tasks.json" in written_paths
    assert "tasks/tasks.md" in written_paths
    assert "contacts/contact_contexts.json" in written_paths
    assert "review/review_suggestions.json" in written_paths
    assert "safety/safety_status.json" in written_paths
    assert "docs/export_notes.md" in written_paths


def test_write_local_data_export_blocks_wrong_token_without_writing(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token="JA",
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.persisted is False
    assert "invalid_token" in result.blocked_reasons
    assert Path(preview.target_root).exists() is False


def test_write_local_data_export_blocks_smoke_failure_without_writing(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.persisted is False
    assert "scanner_smoke_failed" in result.blocked_reasons
    assert Path(preview.target_root).exists() is False


def test_write_local_data_export_blocks_target_outside_exports(tmp_path: Path) -> None:
    preview = _fake_preview(tmp_path / "outside" / "export")

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.persisted is False
    assert "target_outside_exports" in result.blocked_reasons
    assert (tmp_path / "outside").exists() is False


def test_write_local_data_export_blocks_existing_target_without_overwrite(
    tmp_path: Path,
) -> None:
    preview = _preview(tmp_path)
    target = Path(preview.target_root)
    target.mkdir(parents=True)
    marker = target / "marker.txt"
    marker.write_text("keep", encoding="utf-8")

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.persisted is False
    assert result.blocked_reasons == ("target_exists",)
    assert marker.read_text(encoding="utf-8") == "keep"


def test_write_local_data_export_writes_manifest_with_counts(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    manifest = json.loads((Path(result.target_path) / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["export_type"] == "local_data_export"
    assert manifest["scanner_smoke_passed"] is True
    assert manifest["counts"]["tasks"] == 1
    assert manifest["counts"]["contact_contexts"] == 1
    assert manifest["counts"]["review_suggestions"] == 1
    assert "raw_active_database" in manifest["excluded_items"]


def test_write_local_data_export_filters_sensitive_contact_fields(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    contacts = json.loads(
        (Path(result.target_path) / "contacts" / "contact_contexts.json").read_text(
            encoding="utf-8"
        )
    )
    assert contacts[0]["display_name"] == "Max Mustermann"
    assert "private_health_data" not in contacts[0]


def test_write_local_data_export_filters_raw_review_message_text(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    suggestions = json.loads(
        (Path(result.target_path) / "review" / "review_suggestions.json").read_text(
            encoding="utf-8"
        )
    )
    assert suggestions[0]["title"] == "Termin bestaetigen"
    assert "message_text" not in suggestions[0]


def test_write_local_data_export_writes_tasks_markdown(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    content = (Path(result.target_path) / "tasks" / "tasks.md").read_text(encoding="utf-8")
    assert "# Friday Aufgabenexport" in content
    assert "Export Aufgabe" in content


def test_write_local_data_export_does_not_create_zip_or_secret_files(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    target = Path(result.target_path)
    assert list(target.rglob("*.zip")) == []
    assert (target / ".env").exists() is False
    assert (target / "obsidian_vault").exists() is False


def test_write_local_data_export_has_safe_flags(tmp_path: Path) -> None:
    preview = _preview(tmp_path)

    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.preview_only is False
    assert result.persisted is True
    assert result.external_lookup_used is False
