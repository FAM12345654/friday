"""Read-only privacy cleanup preview model for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePath


EXPORT_CLEANUP_TOKEN = "EXPORT AUFRAEUMEN"
BACKUP_CLEANUP_TOKEN = "BACKUP AUFRAEUMEN"
RESTORE_CLEANUP_TOKEN = "RESTORE AUFRAEUMEN"
REVIEW_CLEANUP_TOKEN = "REVIEW AUFRAEUMEN"
CONTACT_CLEANUP_TOKEN = "KONTAKT LÖSCHEN"

ALLOWED_FILE_CLEANUP_AREAS = {
    "Exporte": ("old_export_folders", "local_data/exports", EXPORT_CLEANUP_TOKEN),
    "Backups": ("old_backup_folders", "local_data/backups", BACKUP_CLEANUP_TOKEN),
    "Restore-Kopien": ("old_restore_copies", "local_data/restores", RESTORE_CLEANUP_TOKEN),
}

ALLOWED_STATUS_CLEANUP_AREAS = {
    "Review-Vorschlaege": ("old_rejected_or_converted_suggestions", "SQLite", REVIEW_CLEANUP_TOKEN),
    "Kontakt-Kontexte": ("single_contact_forget_preview", "SQLite", CONTACT_CLEANUP_TOKEN),
}

BLOCKED_AREAS = {
    "Aufgaben": "task_cleanup_not_allowed_in_privacy",
    "aktive SQLite-DB": "active_database_blocked",
    ".env / Secrets": "secrets_blocked",
    "Obsidian Vault": "obsidian_vault_blocked",
    "global": "global_delete_blocked",
}


@dataclass(frozen=True)
class PrivacyCleanupPreviewItem:
    """One read-only planned cleanup item."""

    area_name: str
    cleanup_type: str
    target_path: str
    count_label: str
    allowed_root: str
    allowed: bool
    blocked_reasons: tuple[str, ...]
    requires_token: str


@dataclass(frozen=True)
class PrivacyCleanupPreview:
    """A side-effect-free cleanup preview."""

    items: tuple[PrivacyCleanupPreviewItem, ...]
    blocked_actions: tuple[str, ...]
    writes_performed: bool
    deletes_performed: bool
    external_lookup_used: bool


def _count_label(count: int | None) -> str:
    if count is None:
        return "nicht gezaehlt"
    return str(count)


def _is_under_allowed_root(target_path: str, allowed_root: str) -> bool:
    normalized_target = PurePath(target_path).as_posix().strip("/")
    normalized_root = PurePath(allowed_root).as_posix().strip("/")
    return normalized_target == normalized_root or normalized_target.startswith(
        f"{normalized_root}/"
    )


def build_privacy_cleanup_preview(
    *,
    export_count: int | None = None,
    backup_count: int | None = None,
    restore_copy_count: int | None = None,
    review_cleanup_count: int | None = None,
    contact_cleanup_count: int | None = None,
    requested_areas: tuple[str, ...] | None = None,
    target_paths: dict[str, str] | None = None,
) -> PrivacyCleanupPreview:
    """Build a read-only cleanup preview from explicit input data.

    The function does not scan folders, open SQLite, write files, delete files,
    call external providers, or perform network access.
    """

    counts = {
        "Exporte": export_count,
        "Backups": backup_count,
        "Restore-Kopien": restore_copy_count,
        "Review-Vorschlaege": review_cleanup_count,
        "Kontakt-Kontexte": contact_cleanup_count,
    }
    target_paths = target_paths or {}
    area_order = requested_areas or (
        "Exporte",
        "Backups",
        "Restore-Kopien",
        "Review-Vorschlaege",
        "Kontakt-Kontexte",
    )

    items: list[PrivacyCleanupPreviewItem] = []
    blocked_actions: list[str] = []

    for area_name in area_order:
        if area_name in ALLOWED_FILE_CLEANUP_AREAS:
            cleanup_type, allowed_root, token = ALLOWED_FILE_CLEANUP_AREAS[area_name]
            target_path = target_paths.get(area_name, allowed_root)
            blocked_reasons: tuple[str, ...] = ()
            allowed = True
            if not _is_under_allowed_root(target_path, allowed_root):
                blocked_reasons = ("outside_allowed_root",)
                allowed = False
            items.append(
                PrivacyCleanupPreviewItem(
                    area_name=area_name,
                    cleanup_type=cleanup_type,
                    target_path=target_path,
                    count_label=_count_label(counts[area_name]),
                    allowed_root=allowed_root,
                    allowed=allowed,
                    blocked_reasons=blocked_reasons,
                    requires_token=token,
                )
            )
            if blocked_reasons:
                blocked_actions.extend(blocked_reasons)
            continue

        if area_name in ALLOWED_STATUS_CLEANUP_AREAS:
            cleanup_type, allowed_root, token = ALLOWED_STATUS_CLEANUP_AREAS[area_name]
            items.append(
                PrivacyCleanupPreviewItem(
                    area_name=area_name,
                    cleanup_type=cleanup_type,
                    target_path=allowed_root,
                    count_label=_count_label(counts[area_name]),
                    allowed_root=allowed_root,
                    allowed=True,
                    blocked_reasons=(),
                    requires_token=token,
                )
            )
            continue

        reason = BLOCKED_AREAS.get(area_name, "missing_future_gate")
        blocked_actions.append(reason)
        items.append(
            PrivacyCleanupPreviewItem(
                area_name=area_name,
                cleanup_type="blocked",
                target_path="nicht erlaubt",
                count_label="nicht gezaehlt",
                allowed_root="nicht erlaubt",
                allowed=False,
                blocked_reasons=(reason,),
                requires_token="nicht freigegeben",
            )
        )

    return PrivacyCleanupPreview(
        items=tuple(items),
        blocked_actions=tuple(dict.fromkeys(blocked_actions)),
        writes_performed=False,
        deletes_performed=False,
        external_lookup_used=False,
    )
