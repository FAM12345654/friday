"""Preview model for guarded local review exports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


REVIEW_EXPORT_APPROVAL_TOKEN = "REVIEW EXPORTIEREN"

REVIEW_EXPORT_REQUIRED_EXCLUSIONS = (
    "raw_private_messages",
    "full_message_text",
    "sensitive_contact_contexts",
    "external_provider_data",
    "raw_active_database",
)


@dataclass(frozen=True)
class ReviewExportSection:
    """One planned section in a local review export."""

    name: str
    file_format: str
    planned: bool
    sensitive_details_excluded: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class ReviewExportPreview:
    """Side-effect-free preview for a local review export."""

    target_root: str
    sections: tuple[ReviewExportSection, ...]
    excluded_items: tuple[str, ...]
    approval_token: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _default_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_review_export_preview(
    project_root: str | Path,
    timestamp: str | None = None,
) -> ReviewExportPreview:
    """Build a local review export preview without reading or writing data."""

    root = Path(project_root)
    export_root = (
        root
        / "local_data"
        / "exports"
        / f"friday_review_export_{timestamp or _default_timestamp()}"
    )

    return ReviewExportPreview(
        target_root=str(export_root),
        sections=(
            ReviewExportSection(
                name="Nachrichten-Vorschlaege",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("status", "sender", "suggestion_id"),
            ),
            ReviewExportSection(
                name="Aufgaben-Vorschlaege",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("status", "title", "created_task_id"),
            ),
            ReviewExportSection(
                name="Review-Aktivitaet",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("counts", "local_status_only"),
            ),
        ),
        excluded_items=REVIEW_EXPORT_REQUIRED_EXCLUSIONS,
        approval_token=REVIEW_EXPORT_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
