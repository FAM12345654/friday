"""Guarded writer for local review exports."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Literal, Mapping

from friday.app.review_export_guard import (
    ReviewExportBlockReason,
    check_review_export_allowed,
)
from friday.app.review_export_preview import ReviewExportPreview


ReviewExportWriterBlockReason = ReviewExportBlockReason | Literal["target_exists"]

ALLOWED_MESSAGE_REVIEW_EXPORT_FIELDS = (
    "id",
    "suggestion_id",
    "status",
    "sender",
    "source",
    "created_at",
    "updated_at",
)

ALLOWED_TASK_REVIEW_EXPORT_FIELDS = (
    "id",
    "suggestion_id",
    "status",
    "title",
    "category",
    "due_date",
    "priority",
    "created_task_id",
    "source",
    "created_at",
    "updated_at",
)

REVIEW_EXPORT_NOTES_TEXT = """# Friday Review Export

Dieser Export wurde lokal von Friday erstellt.

- Keine Cloud
- Keine externen Provider
- Keine privaten Roh-Nachrichten
- Keine sensible Kontakt-Kontext-Freitexte
- Keine rohe aktive SQLite-Datenbank
"""


@dataclass(frozen=True)
class ReviewExportPayload:
    """Explicit payload for a guarded local review export."""

    message_suggestions: tuple[Mapping[str, Any], ...]
    task_suggestions: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class ReviewExportWrittenFile:
    """One file created by the local review export writer."""

    relative_path: str
    bytes_written: int


@dataclass(frozen=True)
class ReviewExportWriteResult:
    """Result of a guarded local review export attempt."""

    allowed: bool
    persisted: bool
    target_path: str | None
    written_files: tuple[ReviewExportWrittenFile, ...]
    blocked_reasons: tuple[ReviewExportWriterBlockReason, ...]
    message: str
    preview_only: bool
    external_lookup_used: bool


def _write_text_file(target_root: Path, relative_path: str, text: str) -> ReviewExportWrittenFile:
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return ReviewExportWrittenFile(
        relative_path=relative_path,
        bytes_written=target.stat().st_size,
    )


def _write_json_file(
    target_root: Path,
    relative_path: str,
    payload: Mapping[str, Any] | list[Mapping[str, Any]],
) -> ReviewExportWrittenFile:
    text = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    return _write_text_file(target_root, relative_path, text + "\n")


def _filter_mapping(item: Mapping[str, Any], allowed_fields: tuple[str, ...]) -> dict[str, Any]:
    return {key: item[key] for key in allowed_fields if key in item}


def _count_by_status(items: tuple[Mapping[str, Any], ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        status = str(item.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _build_review_activity_summary(payload: ReviewExportPayload) -> dict[str, Any]:
    return {
        "message_suggestions": {
            "total": len(payload.message_suggestions),
            "by_status": _count_by_status(payload.message_suggestions),
        },
        "task_suggestions": {
            "total": len(payload.task_suggestions),
            "by_status": _count_by_status(payload.task_suggestions),
            "converted_with_task_id": sum(
                1 for item in payload.task_suggestions if item.get("created_task_id")
            ),
        },
        "preview_only": False,
        "persisted": True,
        "external_lookup_used": False,
    }


def _build_manifest(
    preview: ReviewExportPreview,
    payload: ReviewExportPayload,
    written_files: tuple[ReviewExportWrittenFile, ...],
    scanner_smoke_passed: bool,
) -> dict[str, Any]:
    return {
        "export_type": "review_export",
        "target_root": preview.target_root,
        "scanner_smoke_passed": scanner_smoke_passed,
        "sections": [section.name for section in preview.sections],
        "excluded_items": list(preview.excluded_items),
        "counts": {
            "message_suggestions": len(payload.message_suggestions),
            "task_suggestions": len(payload.task_suggestions),
        },
        "written_files": [file.relative_path for file in written_files],
        "preview_only": False,
        "persisted": True,
        "external_lookup_used": False,
    }


def write_review_export(
    *,
    preview: ReviewExportPreview | None,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    project_root: str | Path,
    payload: ReviewExportPayload,
) -> ReviewExportWriteResult:
    """Create a guarded local review export from explicit payload data."""

    guard = check_review_export_allowed(
        preview=preview,
        approval_token=approval_token,
        scanner_smoke_passed=scanner_smoke_passed,
        project_root=project_root,
    )

    if not guard.allowed or preview is None or guard.target_root is None:
        return ReviewExportWriteResult(
            allowed=False,
            persisted=False,
            target_path=guard.target_root,
            written_files=(),
            blocked_reasons=guard.blocked_reasons,
            message=guard.message or "Review-Export wurde nicht freigegeben.",
            preview_only=True,
            external_lookup_used=False,
        )

    target_root = Path(guard.target_root)
    if target_root.exists():
        return ReviewExportWriteResult(
            allowed=False,
            persisted=False,
            target_path=str(target_root),
            written_files=(),
            blocked_reasons=("target_exists",),
            message="Review-Export wurde nicht erstellt, weil der Zielordner bereits existiert.",
            preview_only=True,
            external_lookup_used=False,
        )

    target_root.mkdir(parents=True, exist_ok=False)

    message_suggestions = [
        _filter_mapping(item, ALLOWED_MESSAGE_REVIEW_EXPORT_FIELDS)
        for item in payload.message_suggestions
    ]
    task_suggestions = [
        _filter_mapping(item, ALLOWED_TASK_REVIEW_EXPORT_FIELDS)
        for item in payload.task_suggestions
    ]

    written: list[ReviewExportWrittenFile] = [
        _write_json_file(
            target_root,
            "review/message_suggestions.json",
            message_suggestions,
        ),
        _write_json_file(
            target_root,
            "review/task_suggestions.json",
            task_suggestions,
        ),
        _write_json_file(
            target_root,
            "review/review_activity_summary.json",
            _build_review_activity_summary(payload),
        ),
        _write_text_file(target_root, "docs/review_export_notes.md", REVIEW_EXPORT_NOTES_TEXT),
    ]

    manifest = _build_manifest(
        preview=preview,
        payload=payload,
        written_files=tuple(written),
        scanner_smoke_passed=scanner_smoke_passed,
    )
    written.insert(0, _write_json_file(target_root, "manifest.json", manifest))

    return ReviewExportWriteResult(
        allowed=True,
        persisted=True,
        target_path=str(target_root),
        written_files=tuple(written),
        blocked_reasons=(),
        message="Review-Export wurde lokal erstellt.",
        preview_only=False,
        external_lookup_used=False,
    )
