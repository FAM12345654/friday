"""Side-effect-free guard for possible future SQLite privacy cleanup writes."""

from __future__ import annotations

from dataclasses import dataclass

from friday.app.privacy_cleanup_db_preview import (
    CONTACT_DB_CLEANUP_TOKEN,
    REVIEW_DB_CLEANUP_TOKEN,
    PrivacyCleanupDBPreview,
    PrivacyCleanupDBPreviewItem,
)


DB_CLEANUP_TOKENS: dict[str, str] = {
    "Review-History": REVIEW_DB_CLEANUP_TOKEN,
    "Kontakt-Kontext": CONTACT_DB_CLEANUP_TOKEN,
}

SAFE_REVIEW_STATUS_FILTER = (
    "message_suggestions.status = rejected; task_suggestions.status = converted"
)
SAFE_CONTACT_STATUS_FILTER = "contact_id = <ausgewaehlt>"

SAFE_DB_PREVIEW_FILTERS: dict[str, str] = {
    "Review-History": SAFE_REVIEW_STATUS_FILTER,
    "Kontakt-Kontext": SAFE_CONTACT_STATUS_FILTER,
}

SAFE_DB_TABLES: dict[str, str] = {
    "Review-History": "message_suggestions, task_suggestions",
    "Kontakt-Kontext": "contact_contexts",
}


@dataclass(frozen=True)
class PrivacyCleanupDBGuardResult:
    """Guard result for a possible future SQLite cleanup write."""

    allowed: bool
    cleanup_area: str
    required_token: str | None
    candidate_count: int
    blocked_reasons: tuple[str, ...]
    message: str | None
    preview_required: bool
    backup_required: bool
    transaction_required: bool
    rollback_required: bool
    token_required: bool
    preview_only: bool
    persisted: bool
    external_action_used: bool
    write_performed: bool
    delete_performed: bool
    schema_changed: bool


def _find_preview_item(
    preview: PrivacyCleanupDBPreview | None,
    cleanup_area: str,
) -> PrivacyCleanupDBPreviewItem | None:
    if preview is None:
        return None

    for item in preview.items:
        if item.area_name == cleanup_area:
            return item

    return None


def check_privacy_cleanup_db_write_allowed(
    *,
    cleanup_area: str,
    preview: PrivacyCleanupDBPreview | None,
    approval_token: str | None,
    backup_available: bool,
    transaction_available: bool,
    rollback_available: bool,
    scanner_smoke_passed: bool,
    external_actions_enabled: bool = False,
) -> PrivacyCleanupDBGuardResult:
    """Check whether a possible future SQLite cleanup write would be allowed.

    The guard is intentionally side-effect-free. It does not open SQLite,
    delete rows, write files, prompt the user, print output, or call external
    services.
    """

    blocked_reasons: list[str] = []
    required_token = DB_CLEANUP_TOKENS.get(cleanup_area)

    if required_token is None:
        blocked_reasons.append("unknown_cleanup_area")

    if preview is None:
        blocked_reasons.append("missing_preview")

    item = _find_preview_item(preview, cleanup_area)
    candidate_count = item.candidate_count if item is not None else 0

    if preview is not None and item is None:
        blocked_reasons.append("preview_item_not_found")

    if item is not None:
        if not item.allowed or item.preview_status != "preview_only":
            blocked_reasons.append("preview_item_blocked")

        if item.table_name != SAFE_DB_TABLES.get(cleanup_area):
            blocked_reasons.append("unsafe_table_scope")

        if item.status_filter != SAFE_DB_PREVIEW_FILTERS.get(cleanup_area):
            blocked_reasons.append("unsafe_status_filter")

        if not item.sensitive_content_hidden:
            blocked_reasons.append("sensitive_content_not_hidden")

        if not item.backup_required:
            blocked_reasons.append("backup_not_required_by_preview")

        if not item.transaction_required:
            blocked_reasons.append("transaction_not_required_by_preview")

        if not item.rollback_required:
            blocked_reasons.append("rollback_not_required_by_preview")

        if item.candidate_count <= 0:
            blocked_reasons.append("no_cleanup_candidates")

    if approval_token != required_token:
        blocked_reasons.append("invalid_token")

    if not backup_available:
        blocked_reasons.append("missing_backup")

    if not transaction_available:
        blocked_reasons.append("transaction_unavailable")

    if not rollback_available:
        blocked_reasons.append("rollback_unavailable")

    if not scanner_smoke_passed:
        blocked_reasons.append("scanner_smoke_failed")

    if external_actions_enabled:
        blocked_reasons.append("external_actions_enabled")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return PrivacyCleanupDBGuardResult(
        allowed=allowed,
        cleanup_area=cleanup_area,
        required_token=required_token,
        candidate_count=candidate_count,
        blocked_reasons=unique_blocked_reasons,
        message=None if allowed else "SQLite Privacy Cleanup wurde nicht freigegeben.",
        preview_required=True,
        backup_required=True,
        transaction_required=True,
        rollback_required=True,
        token_required=True,
        preview_only=True,
        persisted=False,
        external_action_used=False,
        write_performed=False,
        delete_performed=False,
        schema_changed=False,
    )
