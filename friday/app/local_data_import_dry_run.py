"""Read-only dry-run model for local Friday data imports."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Literal, Mapping

from friday.app.local_data_import_manifest_reader import LocalDataImportManifestReadResult


LocalDataImportDryRunSectionStatus = Literal["present", "missing", "invalid", "blocked"]
LocalDataImportDryRunBlockReason = Literal[
    "manifest_blocked",
    "export_root_outside_exports",
    "export_root_missing",
    "expected_file_missing",
    "unexpected_path_outside_export",
    "invalid_json_file",
    "forbidden_export_content",
    "safety_flags_enabled",
    "external_lookup_used",
]

EXPECTED_LOCAL_DATA_EXPORT_FILES: tuple[str, ...] = (
    "manifest.json",
    "tasks/tasks.json",
    "tasks/tasks.md",
    "contacts/contact_contexts.json",
    "review/review_suggestions.json",
    "safety/safety_status.json",
    "docs/export_notes.md",
)

ALLOWED_CONTACT_DRY_RUN_FIELDS: tuple[str, ...] = (
    "contact_id",
    "display_name",
    "normalized_name",
    "contact_type",
    "nickname",
    "relationship_context",
    "source_context",
    "updated_at",
)

ALLOWED_REVIEW_DRY_RUN_FIELDS: tuple[str, ...] = (
    "suggestion_id",
    "id",
    "type",
    "status",
    "created_task_id",
    "source",
    "title",
)

SAFE_FALSE_FLAGS: tuple[str, ...] = (
    "ENABLE_REAL_EMAIL",
    "ENABLE_REAL_WHATSAPP",
    "ENABLE_REAL_SMS",
    "ENABLE_REAL_WEATHER",
    "ENABLE_REAL_MUSIC",
)

SAFE_TRUE_FLAGS: tuple[str, ...] = (
    "REQUIRE_USER_APPROVAL",
    "USE_SQLITE_STORAGE",
)

CLI_SAFE_FALSE_FLAGS: tuple[str, ...] = (
    "external_actions_enabled",
    "real_email_enabled",
    "real_whatsapp_enabled",
    "real_sms_enabled",
    "real_weather_enabled",
    "real_music_enabled",
)

CLI_SAFE_TRUE_FLAGS: tuple[str, ...] = (
    "scanner_smoke_passed",
    "requires_user_approval",
)

FORBIDDEN_EXPORT_KEYS: tuple[str, ...] = (
    "api_key",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "private_key",
    "message_text",
    "raw_message_text",
    "private_health_data",
    "private_financial_details",
    "sensitive_contact_free_text",
)


@dataclass(frozen=True)
class LocalDataImportDryRunSection:
    """One file or section checked during local import dry-run."""

    name: str
    relative_path: str
    status: LocalDataImportDryRunSectionStatus
    message: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class LocalDataImportDryRunResult:
    """Structured result of a read-only local import dry-run."""

    allowed: bool
    export_root: str
    manifest_valid: bool
    sections_checked: tuple[LocalDataImportDryRunSection, ...]
    missing_files: tuple[str, ...]
    invalid_files: tuple[str, ...]
    blocked_reasons: tuple[LocalDataImportDryRunBlockReason, ...]
    warnings: tuple[str, ...]
    message: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _section(
    *,
    name: str,
    relative_path: str,
    status: LocalDataImportDryRunSectionStatus,
    message: str,
) -> LocalDataImportDryRunSection:
    return LocalDataImportDryRunSection(
        name=name,
        relative_path=relative_path,
        status=status,
        message=message,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _has_forbidden_content(value: object) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered_key = str(key).lower()
            if lowered_key in FORBIDDEN_EXPORT_KEYS:
                return True
            if _has_forbidden_content(item):
                return True
        return False

    if isinstance(value, list):
        return any(_has_forbidden_content(item) for item in value)

    return False


def _has_external_lookup_used(value: object) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "external_lookup_used" and item is True:
                return True
            if _has_external_lookup_used(item):
                return True
        return False

    if isinstance(value, list):
        return any(_has_external_lookup_used(item) for item in value)

    return False


def _load_json_file(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _contacts_have_only_allowed_fields(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return all(
        isinstance(item, dict) and set(item).issubset(ALLOWED_CONTACT_DRY_RUN_FIELDS)
        for item in value
    )


def _review_has_only_allowed_fields(value: object) -> bool:
    if not isinstance(value, list):
        return False
    return all(
        isinstance(item, dict) and set(item).issubset(ALLOWED_REVIEW_DRY_RUN_FIELDS)
        for item in value
    )


def _safety_flags_are_local_only(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    internal_flags_ok = all(value.get(flag) is False for flag in SAFE_FALSE_FLAGS) and all(
        value.get(flag) is True for flag in SAFE_TRUE_FLAGS
    )
    cli_flags_ok = all(value.get(flag) is False for flag in CLI_SAFE_FALSE_FLAGS) and all(
        value.get(flag) is True for flag in CLI_SAFE_TRUE_FLAGS
    )
    return internal_flags_ok or cli_flags_ok


def build_local_data_import_dry_run(
    *,
    export_root: str | Path,
    manifest_result: LocalDataImportManifestReadResult,
    project_root: str | Path,
) -> LocalDataImportDryRunResult:
    """Check a local data export folder without importing or writing anything."""

    root = Path(project_root)
    export = Path(export_root)
    exports_parent = root / "local_data" / "exports"
    sections: list[LocalDataImportDryRunSection] = []
    missing_files: list[str] = []
    invalid_files: list[str] = []
    blocked_reasons: list[LocalDataImportDryRunBlockReason] = []
    warnings: list[str] = []

    if not manifest_result.allowed:
        blocked_reasons.append("manifest_blocked")

    if not _is_relative_to(export, exports_parent):
        blocked_reasons.append("export_root_outside_exports")

    if not export.exists() or not export.is_dir():
        blocked_reasons.append("export_root_missing")

    if blocked_reasons:
        return LocalDataImportDryRunResult(
            allowed=False,
            export_root=str(export),
            manifest_valid=manifest_result.allowed,
            sections_checked=(),
            missing_files=(),
            invalid_files=(),
            blocked_reasons=tuple(dict.fromkeys(blocked_reasons)),
            warnings=(),
            message="Import Dry-Run wurde blockiert. Es wurde nichts importiert.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    candidate_files = set(EXPECTED_LOCAL_DATA_EXPORT_FILES)
    if manifest_result.summary is not None:
        candidate_files.update(manifest_result.summary.written_files)

    loaded_json: dict[str, object] = {}

    for relative_path in sorted(candidate_files):
        candidate = export / relative_path
        if not _is_relative_to(candidate, export):
            blocked_reasons.append("unexpected_path_outside_export")
            sections.append(
                _section(
                    name=relative_path,
                    relative_path=relative_path,
                    status="blocked",
                    message="Exportdatei zeigt ausserhalb des Exportordners.",
                )
            )
            continue

        if not candidate.exists() or not candidate.is_file():
            missing_files.append(relative_path)
            sections.append(
                _section(
                    name=relative_path,
                    relative_path=relative_path,
                    status="missing",
                    message="Exportdatei fehlt.",
                )
            )
            continue

        if candidate.suffix == ".json":
            parsed = _load_json_file(candidate)
            if parsed is None:
                invalid_files.append(relative_path)
                sections.append(
                    _section(
                        name=relative_path,
                        relative_path=relative_path,
                        status="invalid",
                        message="JSON-Datei ist ungueltig.",
                    )
                )
                continue
            loaded_json[relative_path] = parsed

        sections.append(
            _section(
                name=relative_path,
                relative_path=relative_path,
                status="present",
                message="Exportdatei wurde read-only geprueft.",
            )
        )

    if missing_files:
        blocked_reasons.append("expected_file_missing")

    if invalid_files:
        blocked_reasons.append("invalid_json_file")

    for relative_path, parsed in loaded_json.items():
        if _has_forbidden_content(parsed):
            blocked_reasons.append("forbidden_export_content")
            warnings.append(f"Verbotene Export-Inhalte erkannt: {relative_path}")

        if _has_external_lookup_used(parsed):
            blocked_reasons.append("external_lookup_used")
            warnings.append(f"Externe Lookup-Markierung erkannt: {relative_path}")

    contacts = loaded_json.get("contacts/contact_contexts.json")
    if contacts is not None and not _contacts_have_only_allowed_fields(contacts):
        blocked_reasons.append("forbidden_export_content")
        warnings.append("Kontakt-Export enthaelt nicht erlaubte Felder.")

    review = loaded_json.get("review/review_suggestions.json")
    if review is not None and not _review_has_only_allowed_fields(review):
        blocked_reasons.append("forbidden_export_content")
        warnings.append("Review-Export enthaelt nicht erlaubte Felder.")

    safety = loaded_json.get("safety/safety_status.json")
    if safety is not None and not _safety_flags_are_local_only(safety):
        blocked_reasons.append("safety_flags_enabled")
        warnings.append("Safety-Status ist nicht local-only.")

    unique_blocked_reasons = tuple(dict.fromkeys(blocked_reasons))
    allowed = not unique_blocked_reasons

    return LocalDataImportDryRunResult(
        allowed=allowed,
        export_root=str(export),
        manifest_valid=manifest_result.allowed,
        sections_checked=tuple(sections),
        missing_files=tuple(missing_files),
        invalid_files=tuple(invalid_files),
        blocked_reasons=unique_blocked_reasons,
        warnings=tuple(warnings),
        message=(
            "Import Dry-Run ist bereit. Es wurde nichts importiert."
            if allowed
            else "Import Dry-Run wurde blockiert. Es wurde nichts importiert."
        ),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
