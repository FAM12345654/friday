"""Tests for the guarded local review export writer."""

from __future__ import annotations

import json
from pathlib import Path

from friday.app.review_export_preview import (
    REVIEW_EXPORT_APPROVAL_TOKEN,
    build_review_export_preview,
)
from friday.app.review_export_writer import (
    ReviewExportPayload,
    write_review_export,
)


def _payload() -> ReviewExportPayload:
    return ReviewExportPayload(
        message_suggestions=(
            {
                "id": 1,
                "suggestion_id": 1,
                "status": "approved",
                "sender": "Chef",
                "source": "message_review",
                "message_text": "privater Rohtext darf nicht exportiert werden",
            },
        ),
        task_suggestions=(
            {
                "id": 2,
                "suggestion_id": 2,
                "status": "converted",
                "title": "Rechnung pruefen",
                "created_task_id": 42,
                "raw_message": "nicht exportieren",
            },
        ),
    )


def test_write_review_export_writes_expected_files(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path, timestamp="20260708_120000")

    result = write_review_export(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
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
    assert "review/message_suggestions.json" in written_paths
    assert "review/task_suggestions.json" in written_paths
    assert "review/review_activity_summary.json" in written_paths
    assert "docs/review_export_notes.md" in written_paths


def test_write_review_export_blocks_wrong_token_without_writing(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = write_review_export(
        preview=preview,
        approval_token="JA",
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.persisted is False
    assert "invalid_token" in result.blocked_reasons
    assert Path(preview.target_root).exists() is False


def test_write_review_export_blocks_smoke_failure_without_writing(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = write_review_export(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=False,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.persisted is False
    assert "scanner_smoke_failed" in result.blocked_reasons
    assert Path(preview.target_root).exists() is False


def test_write_review_export_blocks_existing_target_without_overwrite(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)
    target = Path(preview.target_root)
    target.mkdir(parents=True)
    marker = target / "marker.txt"
    marker.write_text("keep", encoding="utf-8")

    result = write_review_export(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.persisted is False
    assert result.blocked_reasons == ("target_exists",)
    assert marker.read_text(encoding="utf-8") == "keep"


def test_write_review_export_filters_raw_message_text(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = write_review_export(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    messages = json.loads(
        (Path(result.target_path) / "review" / "message_suggestions.json").read_text(
            encoding="utf-8"
        )
    )
    assert messages[0]["sender"] == "Chef"
    assert "message_text" not in messages[0]


def test_write_review_export_filters_raw_task_message(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = write_review_export(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    tasks = json.loads(
        (Path(result.target_path) / "review" / "task_suggestions.json").read_text(
            encoding="utf-8"
        )
    )
    assert tasks[0]["title"] == "Rechnung pruefen"
    assert "raw_message" not in tasks[0]


def test_write_review_export_writes_summary_counts(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = write_review_export(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    summary = json.loads(
        (Path(result.target_path) / "review" / "review_activity_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["message_suggestions"]["by_status"]["approved"] == 1
    assert summary["task_suggestions"]["converted_with_task_id"] == 1


def test_write_review_export_has_safe_flags(tmp_path: Path) -> None:
    preview = build_review_export_preview(tmp_path)

    result = write_review_export(
        preview=preview,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=tmp_path,
        payload=_payload(),
    )

    assert result.preview_only is False
    assert result.persisted is True
    assert result.external_lookup_used is False
