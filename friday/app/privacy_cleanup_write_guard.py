"""Side-effect-free guard for possible future privacy cleanup writes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


PrivacyCleanupArea = Literal[
    "exports",
    "backups",
    "restore_work",
    "review_history",
    "contact_context",
]

PrivacyCleanupWriteBlockReason = Literal[
    "unknown_cleanup_area",
    "missing_preview",
    "invalid_token",
    "scanner_smoke_failed",
    "external_actions_enabled",
    "missing_target_path",
    "target_is_project_root",
    "target_is_root",
    "target_outside_allowed_scope",
    "sensitive_path",
    "obsidian_vault_path",
    "active_database_path",
    "protected_project_file",
]

PRIVACY_CLEANUP_TOKENS: dict[str, str] = {
    "exports": "EXPORT AUFRAEUMEN",
    "backups": "BACKUP AUFRAEUMEN",
    "restore_work": "RESTORE AUFRAEUMEN",
    "review_history": "REVIEW AUFRAEUMEN",
    "contact_context": "KONTAKT L\u00d6SCHEN",
}

PATH_REQUIRED_AREAS = (
    "exports",
    "backups",
    "restore_work",
)

PROTECTED_PROJECT_FILENAMES = (
    "requirements.txt",
    "start_friday.bat",
    "setup_friday.bat",
    "run_tests.bat",
)

SENSITIVE_PATH_PARTS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "token",
    "tokens",
)


@dataclass(frozen=True)
class PrivacyCleanupWriteGuardResult:
    """Structured guard result for a possible future privacy cleanup write."""

    allowed: bool
    cleanup_area: str
    target_path: str | None
    allowed_base_path: str | None
    required_token: str | None
    blocked_reasons: tuple[PrivacyCleanupWriteBlockReason, ...]
    message: str | None
    preview_required: bool
    token_required: bool
    preview_only: bool
    persisted: bool
    external_action_used: bool
    write_performed: bool


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _is_root_path(path: Path) -> bool:
    resolved = path.resolve()
    return resolved == resolved.anchor or resolved.parent == resolved


def _has_sensitive_path_part(path: Path) -> bool:
    lowered_parts = tuple(part.lower() for part in path.parts)
    return any(
        sensitive in part
        for part in lowered_parts
        for sensitive in SENSITIVE_PATH_PARTS
    )


def _is_protected_project_file(path: Path, project_root: Path) -> bool:
    if not _is_relative_to(path, project_root):
        return False

    relative = path.resolve().relative_to(project_root.resolve())
    if len(relative.parts) == 1 and relative.name in PROTECTED_PROJECT_FILENAMES:
        return True

    if relative.parts and relative.parts[0] in ("friday", "tests", "scripts"):
        return True

    return False


def _is_same_or_inside(path: Path, parent: Path) -> bool:
    return path.resolve() == parent.resolve() or _is_relative_to(path, parent)


def check_privacy_cleanup_write_allowed(
    *,
    cleanup_area: str,
    target_path: str | Path | None,
    project_root: str | Path,
    allowed_base_path: str | Path | None,
    preview_was_shown: bool,
    approval_token: str | None,
    scanner_smoke_passed: bool,
    external_actions_enabled: bool = False,
    active_database_path: str | Path | None = None,
    obsidian_vault_path: str | Path | None = None,
) -> PrivacyCleanupWriteGuardResult:
    """Check whether a possible future privacy cleanup write would be allowed.

    The guard is intentionally side-effect-free. It does not delete, write,
    read SQLite, call the network, prompt the user, or print output.
    """

    blocked_reasons: list[PrivacyCleanupWriteBlockReason] = []
    root = Path(project_root)
    required_token = PRIVACY_CLEANUP_TOKENS.get(cleanup_area)

    if required_token is None:
        blocked_reasons.append("unknown_cleanup_area")

    if not preview_was_shown:
        blocked_reasons.append("missing_preview")

    if approval_token != required_token:
        blocked_reasons.append("invalid_token")

    if not scanner_smoke_passed:
        blocked_reasons.append("scanner_smoke_failed")

    if external_actions_enabled:
        blocked_reasons.append("external_actions_enabled")

    normalized_target: Path | None = None
    normalized_allowed_base: Path | None = None

    if target_path is not None and str(target_path).strip():
        normalized_target = Path(target_path)

    if allowed_base_path is not None and str(allowed_base_path).strip():
        normalized_allowed_base = Path(allowed_base_path)

    if cleanup_area in PATH_REQUIRED_AREAS and normalized_target is None:
        blocked_reasons.append("missing_target_path")

    if normalized_target is not None:
        if normalized_target.resolve() == root.resolve():
            blocked_reasons.append("target_is_project_root")

        if _is_root_path(normalized_target):
            blocked_reasons.append("target_is_root")

        if normalized_allowed_base is None:
            blocked_reasons.append("target_outside_allowed_scope")
        elif not _is_relative_to(normalized_target, normalized_allowed_base):
            blocked_reasons.append("target_outside_allowed_scope")

        if _has_sensitive_path_part(normalized_target):
            blocked_reasons.append("sensitive_path")

        if obsidian_vault_path is not None and _is_same_or_inside(
            normalized_target,
            Path(obsidian_vault_path),
        ):
            blocked_reasons.append("obsidian_vault_path")

        if active_database_path is not None and normalized_target.resolve() == Path(
            active_database_path
        ).resolve():
            blocked_reasons.append("active_database_path")

        if _is_protected_project_file(normalized_target, root):
            blocked_reasons.append("protected_project_file")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return PrivacyCleanupWriteGuardResult(
        allowed=allowed,
        cleanup_area=cleanup_area,
        target_path=str(normalized_target) if normalized_target is not None else None,
        allowed_base_path=str(normalized_allowed_base)
        if normalized_allowed_base is not None
        else None,
        required_token=required_token,
        blocked_reasons=unique_blocked_reasons,
        message=None if allowed else "Privacy Cleanup wurde nicht freigegeben.",
        preview_required=True,
        token_required=True,
        preview_only=True,
        persisted=False,
        external_action_used=False,
        write_performed=False,
    )
