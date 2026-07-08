"""Guard model for local review exports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from friday.app.review_export_preview import (
    REVIEW_EXPORT_APPROVAL_TOKEN,
    REVIEW_EXPORT_REQUIRED_EXCLUSIONS,
    ReviewExportPreview,
)


ReviewExportBlockReason = Literal[
    "missing_preview",
    "invalid_token",
    "target_outside_exports",
    "scanner_smoke_failed",
    "required_exclusion_missing",
    "sensitive_details_not_excluded",
]


@dataclass(frozen=True)
class ReviewExportGuardResult:
    """Structured guard result for a local review export."""

    allowed: bool
    target_root: str | None
    blocked_reasons: tuple[ReviewExportBlockReason, ...]
    message: str | None
    checked_sections: tuple[str, ...]
    required_exclusions: tuple[str, ...]
    missing_exclusions: tuple[str, ...]
    approval_token_required: str
    scanner_smoke_required: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def check_review_export_allowed(
    preview: ReviewExportPreview | None,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    project_root: str | Path,
) -> ReviewExportGuardResult:
    """Check whether a local review export would be allowed."""

    blocked_reasons: list[ReviewExportBlockReason] = []
    checked_sections: tuple[str, ...] = ()
    missing_exclusions: tuple[str, ...] = ()
    target_root: str | None = None

    root = Path(project_root)
    allowed_export_parent = root / "local_data" / "exports"

    if preview is None:
        blocked_reasons.append("missing_preview")
    else:
        target_root = preview.target_root
        target_path = Path(preview.target_root)
        checked_sections = tuple(section.name for section in preview.sections)

        if not _is_relative_to(target_path, allowed_export_parent):
            blocked_reasons.append("target_outside_exports")

        existing_exclusions = set(preview.excluded_items)
        missing_exclusions = tuple(
            item
            for item in REVIEW_EXPORT_REQUIRED_EXCLUSIONS
            if item not in existing_exclusions
        )
        if missing_exclusions:
            blocked_reasons.append("required_exclusion_missing")

        if any(not section.sensitive_details_excluded for section in preview.sections):
            blocked_reasons.append("sensitive_details_not_excluded")

    if approval_token != REVIEW_EXPORT_APPROVAL_TOKEN:
        blocked_reasons.append("invalid_token")

    if not scanner_smoke_passed:
        blocked_reasons.append("scanner_smoke_failed")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return ReviewExportGuardResult(
        allowed=allowed,
        target_root=target_root,
        blocked_reasons=unique_blocked_reasons,
        message=None if allowed else "Review-Export wurde nicht freigegeben.",
        checked_sections=checked_sections,
        required_exclusions=REVIEW_EXPORT_REQUIRED_EXCLUSIONS,
        missing_exclusions=missing_exclusions,
        approval_token_required=REVIEW_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_required=True,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
