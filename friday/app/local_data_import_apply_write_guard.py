"""Side-effect-free guard for a possible local data import apply write."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday.app.local_data_import_apply_preview import (
    LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
    LocalDataImportApplyPreviewResult,
)


LocalDataImportApplyWriteGuardStatus = Literal[
    "allowed",
    "blocked",
    "invalid",
    "warnings",
]

LocalDataImportApplyWriteBlockReason = Literal[
    "missing_preview",
    "preview_invalid",
    "preview_blocked",
    "token_not_requestable",
    "backup_required",
    "scanner_smoke_failed",
    "conflicts_present",
    "sensitive_data_present",
    "secrets_present",
    "private_raw_messages_present",
    "external_lookup_used",
    "forbidden_write_scope",
    "database_schema_change_required",
    "invalid_token",
]

ALLOWED_LOCAL_DATA_IMPORT_WRITE_SCOPES = (
    "tasks",
    "contact_contexts",
    "review_suggestions",
)

BLOCKED_LOCAL_DATA_IMPORT_WRITE_SCOPES = (
    "safety_status",
    "raw_active_database",
    "secrets",
    "env",
    "tokens",
    "obsidian_vault",
    "private_raw_messages",
)


@dataclass(frozen=True)
class LocalDataImportApplyWriteGuardResult:
    """Structured guard result for a possible future local import apply write."""

    allowed: bool
    status: LocalDataImportApplyWriteGuardStatus
    blocked_reasons: tuple[LocalDataImportApplyWriteBlockReason, ...]
    warnings: tuple[str, ...]
    required_token: str
    write_scope: tuple[str, ...]
    forbidden_write_scope: tuple[str, ...]
    message: str | None
    preview_only: bool
    persisted: bool
    external_action_used: bool
    database_schema_change_required: bool


def _preview_write_scope(
    preview: LocalDataImportApplyPreviewResult | None,
) -> tuple[str, ...]:
    if preview is None:
        return ()
    return tuple(section.name for section in preview.sections if section.planned_count > 0)


def check_local_data_import_apply_write_allowed(
    *,
    preview: LocalDataImportApplyPreviewResult | None,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    requested_write_scope: tuple[str, ...] | None = None,
    conflicts_present: bool = False,
    sensitive_data_present: bool = False,
    secrets_present: bool = False,
    private_raw_messages_present: bool = False,
    external_lookup_used: bool = False,
    database_schema_change_required: bool = False,
) -> LocalDataImportApplyWriteGuardResult:
    """Check whether a possible future import apply write would be allowed."""

    blocked_reasons: list[LocalDataImportApplyWriteBlockReason] = []
    warnings: list[str] = []

    if preview is None:
        blocked_reasons.append("missing_preview")
        write_scope: tuple[str, ...] = requested_write_scope or ()
    else:
        warnings.extend(preview.warnings)
        write_scope = requested_write_scope or _preview_write_scope(preview)

        if preview.status == "invalid":
            blocked_reasons.append("preview_invalid")
        elif preview.status == "blocked":
            blocked_reasons.append("preview_blocked")

        if not preview.allowed_to_request_token:
            blocked_reasons.append("token_not_requestable")

        if preview.backup_required and not preview.backup_ready:
            blocked_reasons.append("backup_required")

        if preview.external_lookup_used:
            blocked_reasons.append("external_lookup_used")

        if "conflicts_present" in preview.blocked_reasons:
            blocked_reasons.append("conflicts_present")

    if approval_token != LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN:
        blocked_reasons.append("invalid_token")

    if not scanner_smoke_passed:
        blocked_reasons.append("scanner_smoke_failed")

    if conflicts_present:
        blocked_reasons.append("conflicts_present")

    if sensitive_data_present:
        blocked_reasons.append("sensitive_data_present")

    if secrets_present:
        blocked_reasons.append("secrets_present")

    if private_raw_messages_present:
        blocked_reasons.append("private_raw_messages_present")

    if external_lookup_used:
        blocked_reasons.append("external_lookup_used")

    if database_schema_change_required:
        blocked_reasons.append("database_schema_change_required")

    allowed_scope = set(ALLOWED_LOCAL_DATA_IMPORT_WRITE_SCOPES)
    forbidden_scope = tuple(scope for scope in write_scope if scope not in allowed_scope)
    if forbidden_scope:
        blocked_reasons.append("forbidden_write_scope")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))

    if preview is None or "preview_invalid" in unique_blocked_reasons:
        status: LocalDataImportApplyWriteGuardStatus = "invalid"
    elif unique_blocked_reasons:
        status = "blocked"
    elif warnings:
        status = "warnings"
    else:
        status = "allowed"

    allowed = status in ("allowed", "warnings")

    return LocalDataImportApplyWriteGuardResult(
        allowed=allowed,
        status=status,
        blocked_reasons=unique_blocked_reasons,
        warnings=tuple(warnings),
        required_token=LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN,
        write_scope=write_scope,
        forbidden_write_scope=forbidden_scope,
        message=None if allowed else "Import-Apply wurde nicht freigegeben.",
        preview_only=True,
        persisted=False,
        external_action_used=False,
        database_schema_change_required=database_schema_change_required,
    )
