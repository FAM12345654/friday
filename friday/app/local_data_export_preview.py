"""Preview model for local Friday data export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from friday.config import LOCAL_DATA_DIR, PROJECT_ROOT


LOCAL_DATA_EXPORT_APPROVAL_TOKEN = "DATEN EXPORTIEREN"
DEFAULT_EXPORT_TIMESTAMP = "YYYYMMDD_HHMMSS"


@dataclass(frozen=True)
class LocalDataExportSection:
    """One planned section in a local data export preview."""

    name: str
    file_format: str
    planned: bool
    sensitive_details_excluded: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class LocalDataExportPreview:
    """Side-effect-free preview for a future local data export."""

    target_root: str
    sections: tuple[LocalDataExportSection, ...]
    excluded_items: tuple[str, ...]
    approval_token: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def build_local_data_export_preview(
    *,
    project_root: Path | None = None,
    local_data_dir: Path | None = None,
    timestamp: str = DEFAULT_EXPORT_TIMESTAMP,
) -> LocalDataExportPreview:
    """Build a side-effect-free local data export preview."""

    resolved_project_root = Path(project_root or PROJECT_ROOT)
    resolved_local_data_dir = Path(local_data_dir or LOCAL_DATA_DIR)
    if not resolved_local_data_dir.is_absolute():
        resolved_local_data_dir = resolved_project_root / resolved_local_data_dir

    target_root = resolved_local_data_dir / "exports" / f"friday_data_export_{timestamp}"

    return LocalDataExportPreview(
        target_root=str(target_root),
        sections=(
            LocalDataExportSection(
                name="Aufgaben",
                file_format="markdown_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("local_task_fields_only", "active_database_not_copied_raw"),
            ),
            LocalDataExportSection(
                name="Kontakt-Kontexte",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("consent_summary_only", "restricted_context_fields"),
            ),
            LocalDataExportSection(
                name="Review-Vorschlaege",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("status_and_ids_only", "message_body_not_exported_raw"),
            ),
            LocalDataExportSection(
                name="Backup-Restore-Status",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("paths_and_status_only", "backup_payload_not_nested"),
            ),
            LocalDataExportSection(
                name="Privacy Dashboard Summary",
                file_format="summary_json",
                planned=True,
                sensitive_details_excluded=True,
                notes=("read_only_status_summary", "local_flags_only"),
            ),
            LocalDataExportSection(
                name="Safety Matrix",
                file_format="markdown_summary",
                planned=True,
                sensitive_details_excluded=True,
                notes=("documentation_snapshot_only", "no_runtime_secret_values"),
            ),
        ),
        excluded_items=(
            ".env",
            "api_keys",
            "tokens",
            "cache_files",
            "obsidian_vault",
            "full_private_messages",
            "sensitive_contact_free_text",
            "private_health_data",
            "private_financial_details",
            "raw_active_database",
        ),
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
