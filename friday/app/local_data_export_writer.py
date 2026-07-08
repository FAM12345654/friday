"""Guarded writer for local Friday data export."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Literal, Mapping

from friday.app.local_data_export_guard import (
    LocalDataExportBlockReason,
    check_local_data_export_allowed,
)
from friday.app.local_data_export_preview import LocalDataExportPreview
from friday.app.task_markdown_export import format_tasks_as_markdown


LocalDataExportWriterBlockReason = LocalDataExportBlockReason | Literal["target_exists"]

ALLOWED_CONTACT_EXPORT_FIELDS = (
    "contact_id",
    "display_name",
    "normalized_name",
    "contact_type",
    "nickname",
    "relationship_context",
    "source_context",
    "updated_at",
)

ALLOWED_REVIEW_EXPORT_FIELDS = (
    "suggestion_id",
    "id",
    "type",
    "status",
    "created_task_id",
    "source",
    "title",
)

EXPORT_NOTES_TEXT = """# Friday Local Data Export

Dieser Export wurde lokal von Friday erstellt.

- Keine Cloud
- Keine externen Provider
- Keine rohe aktive Datenbankkopie
- Keine privaten Roh-Nachrichtentexte
- Kein Obsidian Vault
"""


@dataclass(frozen=True)
class LocalDataExportPayload:
    """Explicit data payload for a guarded local data export."""

    tasks: tuple[Mapping[str, Any], ...]
    contact_contexts: tuple[Mapping[str, Any], ...]
    review_suggestions: tuple[Mapping[str, Any], ...]
    safety_status: Mapping[str, Any]


@dataclass(frozen=True)
class LocalDataExportWrittenFile:
    """One file created by the local data export writer."""

    relative_path: str
    bytes_written: int


@dataclass(frozen=True)
class LocalDataExportWriteResult:
    """Result of a guarded local data export attempt."""

    allowed: bool
    persisted: bool
    target_path: str | None
    written_files: tuple[LocalDataExportWrittenFile, ...]
    blocked_reasons: tuple[LocalDataExportWriterBlockReason, ...]
    message: str
    preview_only: bool
    external_lookup_used: bool


def _write_text_file(target_root: Path, relative_path: str, text: str) -> LocalDataExportWrittenFile:
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return LocalDataExportWrittenFile(
        relative_path=relative_path,
        bytes_written=target.stat().st_size,
    )


def _write_json_file(
    target_root: Path,
    relative_path: str,
    payload: Mapping[str, Any] | list[Mapping[str, Any]],
) -> LocalDataExportWrittenFile:
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    return _write_text_file(target_root, relative_path, text + "\n")


def _filter_mapping(
    item: Mapping[str, Any],
    allowed_fields: tuple[str, ...],
) -> dict[str, Any]:
    return {key: item[key] for key in allowed_fields if key in item}


def _build_manifest(
    preview: LocalDataExportPreview,
    payload: LocalDataExportPayload,
    written_files: tuple[LocalDataExportWrittenFile, ...],
    scanner_smoke_passed: bool,
) -> dict[str, Any]:
    return {
        "export_type": "local_data_export",
        "target_root": preview.target_root,
        "scanner_smoke_passed": scanner_smoke_passed,
        "sections": [section.name for section in preview.sections],
        "excluded_items": list(preview.excluded_items),
        "counts": {
            "tasks": len(payload.tasks),
            "contact_contexts": len(payload.contact_contexts),
            "review_suggestions": len(payload.review_suggestions),
        },
        "written_files": [file.relative_path for file in written_files],
        "preview_only": False,
        "persisted": True,
        "external_lookup_used": False,
    }


def write_local_data_export(
    *,
    preview: LocalDataExportPreview | None,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    project_root: str | Path,
    payload: LocalDataExportPayload,
) -> LocalDataExportWriteResult:
    """Create a guarded local data export from explicit payload data."""

    guard = check_local_data_export_allowed(
        preview=preview,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        project_root=project_root,
    )

    if not guard.allowed or preview is None or guard.target_root is None:
        return LocalDataExportWriteResult(
            allowed=False,
            persisted=False,
            target_path=guard.target_root,
            written_files=(),
            blocked_reasons=guard.blocked_reasons,
            message=guard.message or "Datenexport wurde nicht freigegeben.",
            preview_only=True,
            external_lookup_used=False,
        )

    target_root = Path(guard.target_root)
    if target_root.exists():
        return LocalDataExportWriteResult(
            allowed=False,
            persisted=False,
            target_path=str(target_root),
            written_files=(),
            blocked_reasons=("target_exists",),
            message="Datenexport wurde nicht erstellt, weil der Zielordner bereits existiert.",
            preview_only=True,
            external_lookup_used=False,
        )

    target_root.mkdir(parents=True, exist_ok=False)

    contact_contexts = [
        _filter_mapping(item, ALLOWED_CONTACT_EXPORT_FIELDS)
        for item in payload.contact_contexts
    ]
    review_suggestions = [
        _filter_mapping(item, ALLOWED_REVIEW_EXPORT_FIELDS)
        for item in payload.review_suggestions
    ]

    written: list[LocalDataExportWrittenFile] = [
        _write_json_file(target_root, "tasks/tasks.json", list(payload.tasks)),
        _write_text_file(target_root, "tasks/tasks.md", format_tasks_as_markdown(payload.tasks)),
        _write_json_file(target_root, "contacts/contact_contexts.json", contact_contexts),
        _write_json_file(target_root, "review/review_suggestions.json", review_suggestions),
        _write_json_file(target_root, "safety/safety_status.json", dict(payload.safety_status)),
        _write_text_file(target_root, "docs/export_notes.md", EXPORT_NOTES_TEXT),
    ]

    manifest = _build_manifest(
        preview=preview,
        payload=payload,
        written_files=tuple(written),
        scanner_smoke_passed=scanner_smoke_passed,
    )
    written.insert(0, _write_json_file(target_root, "manifest.json", manifest))

    return LocalDataExportWriteResult(
        allowed=True,
        persisted=True,
        target_path=str(target_root),
        written_files=tuple(written),
        blocked_reasons=(),
        message="Datenexport wurde lokal erstellt.",
        preview_only=False,
        external_lookup_used=False,
    )
