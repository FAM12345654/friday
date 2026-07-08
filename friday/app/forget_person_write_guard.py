"""Side-effect-free guard for Forget Person writes."""

from __future__ import annotations

from dataclasses import dataclass

from friday.app.forget_person_preview import (
    FORGET_PERSON_APPROVAL_TOKEN,
    ForgetPersonPreview,
)


@dataclass(frozen=True)
class ForgetPersonWriteGuardResult:
    """Guard result for a local Forget Person write."""

    allowed: bool
    required_token: str
    candidate_count: int
    target_contact_ids: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    message: str | None
    preview_required: bool
    backup_required: bool
    transaction_required: bool
    rollback_required: bool
    token_required: bool
    local_only: bool
    external_action_used: bool
    obsidian_write_performed: bool
    write_performed: bool
    delete_performed: bool
    schema_changed: bool


def check_forget_person_write_allowed(
    *,
    preview: ForgetPersonPreview | None,
    approval_token: str | None,
    backup_available: bool,
    transaction_available: bool,
    rollback_available: bool,
    scanner_smoke_passed: bool,
    external_actions_enabled: bool = False,
    obsidian_write_requested: bool = False,
) -> ForgetPersonWriteGuardResult:
    """Check whether a local Forget Person write is allowed.

    The guard never opens SQLite, writes files, deletes rows, prompts, prints,
    touches Obsidian, or calls external services.
    """

    blocked_reasons: list[str] = []
    target_contact_ids: tuple[str, ...] = ()
    candidate_count = 0

    if preview is None:
        blocked_reasons.append("missing_preview")
    else:
        target_contact_ids = tuple(contact.contact_id for contact in preview.matched_contacts)
        candidate_count = preview.candidate_count

        if not preview.allowed:
            blocked_reasons.append("preview_blocked")
            blocked_reasons.extend(preview.blocked_reasons)

        if preview.target_table != "contact_contexts":
            blocked_reasons.append("unsafe_table_scope")

        if not preview.sensitive_content_hidden:
            blocked_reasons.append("sensitive_content_not_hidden")

        if not preview.backup_required:
            blocked_reasons.append("backup_not_required_by_preview")

        if not preview.transaction_required:
            blocked_reasons.append("transaction_not_required_by_preview")

        if not preview.rollback_required:
            blocked_reasons.append("rollback_not_required_by_preview")

        if preview.writes_performed or preview.deletes_performed:
            blocked_reasons.append("preview_had_side_effects")

        if preview.schema_changed:
            blocked_reasons.append("schema_changed_by_preview")

        if preview.external_lookup_used:
            blocked_reasons.append("external_lookup_used_by_preview")

        if preview.obsidian_write_performed:
            blocked_reasons.append("obsidian_write_performed_by_preview")

        if preview.candidate_count <= 0:
            blocked_reasons.append("no_forget_candidates")

    if approval_token != FORGET_PERSON_APPROVAL_TOKEN:
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

    if obsidian_write_requested:
        blocked_reasons.append("obsidian_write_requested")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return ForgetPersonWriteGuardResult(
        allowed=allowed,
        required_token=FORGET_PERSON_APPROVAL_TOKEN,
        candidate_count=candidate_count,
        target_contact_ids=target_contact_ids,
        blocked_reasons=unique_blocked_reasons,
        message=None if allowed else "Forget Person wurde nicht freigegeben.",
        preview_required=True,
        backup_required=True,
        transaction_required=True,
        rollback_required=True,
        token_required=True,
        local_only=True,
        external_action_used=False,
        obsidian_write_performed=False,
        write_performed=False,
        delete_performed=False,
        schema_changed=False,
    )
