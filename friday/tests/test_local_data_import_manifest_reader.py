"""Tests for the read-only local data import manifest reader."""

from __future__ import annotations

import json
from pathlib import Path

from friday.app.local_data_export_preview import LOCAL_DATA_EXPORT_APPROVAL_TOKEN
from friday.app.local_data_export_writer import LocalDataExportPayload, write_local_data_export
from friday.app.local_data_import_manifest_reader import read_local_data_import_manifest
from friday.app.local_data_export_preview import build_local_data_export_preview


def _payload() -> LocalDataExportPayload:
    return LocalDataExportPayload(
        tasks=(
            {
                "id": 1,
                "title": "Import Review Aufgabe",
                "status": "open",
            },
        ),
        contact_contexts=(),
        review_suggestions=(),
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
        timestamp="20260707_230000",
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
    return Path(result.target_path) / "manifest.json"


def _manifest_data(tmp_path: Path) -> dict[str, object]:
    return {
        "export_type": "local_data_export",
        "target_root": str(tmp_path / "local_data" / "exports" / "friday_data_export_test"),
        "scanner_smoke_passed": True,
        "sections": ["Aufgaben", "Kontakt-Kontexte", "Review-Vorschlaege", "Safety-Status"],
        "excluded_items": [
            ".env",
            "api_keys",
            "tokens",
            "cache_files",
            "obsidian_vault",
            "full_private_messages",
            "sensitive_contact_free_text",
            "raw_active_database",
        ],
        "counts": {
            "tasks": 1,
            "contact_contexts": 0,
            "review_suggestions": 0,
        },
        "written_files": ["tasks/tasks.json", "manifest.json"],
        "preview_only": False,
        "persisted": True,
        "external_lookup_used": False,
    }


def _write_manifest(tmp_path: Path, data: dict[str, object]) -> Path:
    manifest = tmp_path / "local_data" / "exports" / "manual_export" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps(data), encoding="utf-8")
    return manifest


def test_read_local_data_import_manifest_allows_writer_manifest(tmp_path: Path) -> None:
    manifest = _write_export(tmp_path)

    result = read_local_data_import_manifest(
        manifest_path=manifest,
        project_root=tmp_path,
    )

    assert result.allowed is True
    assert result.summary is not None
    assert result.summary.export_type == "local_data_export"
    assert result.summary.counts["tasks"] == 1
    assert result.preview_only is True
    assert result.persisted is False
    assert result.external_lookup_used is False


def test_read_local_data_import_manifest_blocks_missing_manifest(tmp_path: Path) -> None:
    result = read_local_data_import_manifest(
        manifest_path=tmp_path / "local_data" / "exports" / "missing" / "manifest.json",
        project_root=tmp_path,
    )

    assert result.allowed is False
    assert result.blocked_reasons == ("manifest_missing",)


def test_read_local_data_import_manifest_blocks_manifest_outside_exports(tmp_path: Path) -> None:
    outside = tmp_path / "outside" / "manifest.json"
    outside.parent.mkdir()
    outside.write_text("{}", encoding="utf-8")

    result = read_local_data_import_manifest(manifest_path=outside, project_root=tmp_path)

    assert result.allowed is False
    assert result.blocked_reasons == ("manifest_outside_exports",)


def test_read_local_data_import_manifest_blocks_invalid_json(tmp_path: Path) -> None:
    manifest = tmp_path / "local_data" / "exports" / "bad" / "manifest.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text("{bad", encoding="utf-8")

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "manifest_invalid_json" in result.blocked_reasons


def test_read_local_data_import_manifest_blocks_missing_required_field(tmp_path: Path) -> None:
    data = _manifest_data(tmp_path)
    del data["sections"]
    manifest = _write_manifest(tmp_path, data)

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "missing_required_field" in result.blocked_reasons
    assert "sections" in result.missing_fields


def test_read_local_data_import_manifest_blocks_wrong_export_type(tmp_path: Path) -> None:
    data = _manifest_data(tmp_path)
    data["export_type"] = "cloud_export"
    manifest = _write_manifest(tmp_path, data)

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "invalid_export_type" in result.blocked_reasons


def test_read_local_data_import_manifest_blocks_target_root_outside_exports(tmp_path: Path) -> None:
    data = _manifest_data(tmp_path)
    data["target_root"] = str(tmp_path / "outside_export")
    manifest = _write_manifest(tmp_path, data)

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "target_root_outside_exports" in result.blocked_reasons


def test_read_local_data_import_manifest_blocks_failed_safety_smoke(tmp_path: Path) -> None:
    data = _manifest_data(tmp_path)
    data["scanner_smoke_passed"] = False
    manifest = _write_manifest(tmp_path, data)

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "scanner_smoke_not_passed" in result.blocked_reasons


def test_read_local_data_import_manifest_blocks_missing_exclusions(tmp_path: Path) -> None:
    data = _manifest_data(tmp_path)
    data["excluded_items"] = ["raw_active_database"]
    manifest = _write_manifest(tmp_path, data)

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "missing_exclusions" in result.blocked_reasons
    assert "api_keys" in result.missing_exclusions


def test_read_local_data_import_manifest_blocks_sensitive_manifest_content(tmp_path: Path) -> None:
    data = _manifest_data(tmp_path)
    data["api_key"] = "secret"
    manifest = _write_manifest(tmp_path, data)

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "forbidden_manifest_content" in result.blocked_reasons


def test_read_local_data_import_manifest_blocks_external_lookup_used(tmp_path: Path) -> None:
    data = _manifest_data(tmp_path)
    data["external_lookup_used"] = True
    manifest = _write_manifest(tmp_path, data)

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    assert result.allowed is False
    assert "external_lookup_used" in result.blocked_reasons


def test_read_local_data_import_manifest_does_not_write_files(tmp_path: Path) -> None:
    manifest = _write_export(tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = read_local_data_import_manifest(manifest_path=manifest, project_root=tmp_path)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert result.allowed is True
    assert before == after
