"""Side-effect-free preview model for a possible local data import apply step."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday.app.local_data_import_dry_run import LocalDataImportDryRunResult
from friday.app.local_data_import_manifest_reader import LocalDataImportManifestReadResult


LocalDataImportApplyPreviewStatus = Literal[
    "blocked",
    "preview_ready",
    "warnings",
    "invalid",
]

LocalDataImportApplyPreviewBlockReason = Literal[
    "manifest_blocked",
    "dry_run_blocked",
    "backup_required",
    "conflicts_present",
    "external_lookup_used",
]


@dataclass(frozen=True)
class LocalDataImportApplyPreviewSection:
    """One planned local import section shown in the apply preview."""

    name: str
    planned_count: int
    action: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class LocalDataImportApplyPreviewResult:
    """Structured preview for a future local import apply step."""

    status: LocalDataImportApplyPreviewStatus
    allowed_to_request_token: bool
    export_root: str
    sections: tuple[LocalDataImportApplyPreviewSection, ...]
    blocked_reasons: tuple[LocalDataImportApplyPreviewBlockReason, ...]
    warnings: tuple[str, ...]
    message: str
    backup_required: bool
    backup_ready: bool
    approval_token_required: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN = "IMPORT ANWENDEN"


def _section(name: str, planned_count: int, action: str) -> LocalDataImportApplyPreviewSection:
    return LocalDataImportApplyPreviewSection(
        name=name,
        planned_count=max(planned_count, 0),
        action=action,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _planned_sections(
    manifest_result: LocalDataImportManifestReadResult,
) -> tuple[LocalDataImportApplyPreviewSection, ...]:
    if manifest_result.summary is None:
        return ()

    counts = manifest_result.summary.counts
    return (
        _section("tasks", counts.get("tasks", 0), "preview_import_or_update"),
        _section(
            "contact_contexts",
            counts.get("contact_contexts", 0),
            "preview_import_or_update",
        ),
        _section(
            "review_suggestions",
            counts.get("review_suggestions", 0),
            "preview_status_import",
        ),
    )


def build_local_data_import_apply_preview(
    *,
    manifest_result: LocalDataImportManifestReadResult,
    dry_run_result: LocalDataImportDryRunResult,
    backup_ready: bool,
    conflict_warnings: tuple[str, ...] = (),
) -> LocalDataImportApplyPreviewResult:
    """Build a read-only preview for a future local data import apply step."""

    blocked_reasons: list[LocalDataImportApplyPreviewBlockReason] = []
    warnings: list[str] = list(dry_run_result.warnings)

    if not manifest_result.allowed:
        blocked_reasons.append("manifest_blocked")

    if not dry_run_result.allowed:
        blocked_reasons.append("dry_run_blocked")

    if manifest_result.external_lookup_used or dry_run_result.external_lookup_used:
        blocked_reasons.append("external_lookup_used")

    if not backup_ready:
        blocked_reasons.append("backup_required")

    if conflict_warnings:
        blocked_reasons.append("conflicts_present")
        warnings.extend(conflict_warnings)

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    sections = _planned_sections(manifest_result)

    if not manifest_result.allowed or manifest_result.summary is None:
        status: LocalDataImportApplyPreviewStatus = "invalid"
    elif unique_blocked_reasons:
        status = "blocked"
    elif warnings:
        status = "warnings"
    else:
        status = "preview_ready"

    allowed_to_request_token = status in ("preview_ready", "warnings")

    return LocalDataImportApplyPreviewResult(
        status=status,
        allowed_to_request_token=allowed_to_request_token,
        export_root=dry_run_result.export_root,
        sections=sections,
        blocked_reasons=unique_blocked_reasons,
        warnings=tuple(warnings),
        message=(
            "Import-Apply-Vorschau ist bereit. Es wurde nichts importiert."
            if allowed_to_request_token
            else "Import-Apply-Vorschau wurde blockiert. Es wurde nichts importiert."
        ),
        backup_required=True,
        backup_ready=backup_ready,
        approval_token_required=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
