"""Read-only manifest reader for local Friday data exports."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Literal, Mapping


LocalDataImportManifestBlockReason = Literal[
    "manifest_outside_exports",
    "manifest_missing",
    "manifest_not_file",
    "manifest_invalid_json",
    "manifest_not_object",
    "missing_required_field",
    "invalid_export_type",
    "target_root_outside_exports",
    "scanner_smoke_not_passed",
    "export_not_persisted",
    "export_marked_preview",
    "external_lookup_used",
    "missing_exclusions",
    "forbidden_manifest_content",
]

REQUIRED_LOCAL_DATA_IMPORT_MANIFEST_FIELDS: tuple[str, ...] = (
    "export_type",
    "target_root",
    "scanner_smoke_passed",
    "sections",
    "excluded_items",
    "counts",
    "written_files",
    "preview_only",
    "persisted",
    "external_lookup_used",
)

REQUIRED_LOCAL_DATA_IMPORT_EXCLUSIONS: tuple[str, ...] = (
    ".env",
    "api_keys",
    "tokens",
    "cache_files",
    "obsidian_vault",
    "full_private_messages",
    "sensitive_contact_free_text",
    "raw_active_database",
)

FORBIDDEN_MANIFEST_KEYS: tuple[str, ...] = (
    "api_key",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "private_key",
    "message_text",
    "raw_message_text",
    "sensitive_contact_free_text_value",
)

FORBIDDEN_MANIFEST_VALUE_FRAGMENTS: tuple[str, ...] = (
    "begin private key",
    "password=",
    "api_key=",
    "access_token=",
    "refresh_token=",
    "obsidian_vault/",
    "obsidianvault/",
)


@dataclass(frozen=True)
class LocalDataImportManifestSummary:
    """Safe summary extracted from a local data export manifest."""

    export_type: str
    target_root: str
    sections: tuple[str, ...]
    excluded_items: tuple[str, ...]
    written_files: tuple[str, ...]
    counts: Mapping[str, int]
    scanner_smoke_passed: bool
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


@dataclass(frozen=True)
class LocalDataImportManifestReadResult:
    """Result of a read-only import manifest check."""

    allowed: bool
    manifest_path: str
    summary: LocalDataImportManifestSummary | None
    missing_fields: tuple[str, ...]
    missing_exclusions: tuple[str, ...]
    blocked_reasons: tuple[LocalDataImportManifestBlockReason, ...]
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


def _blocked(
    *,
    manifest_path: Path,
    reasons: list[LocalDataImportManifestBlockReason],
    missing_fields: tuple[str, ...] = (),
    missing_exclusions: tuple[str, ...] = (),
) -> LocalDataImportManifestReadResult:
    return LocalDataImportManifestReadResult(
        allowed=False,
        manifest_path=str(manifest_path),
        summary=None,
        missing_fields=missing_fields,
        missing_exclusions=missing_exclusions,
        blocked_reasons=tuple(dict.fromkeys(reasons)),
        message="Import-Manifest wurde blockiert. Es wurde nichts importiert.",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )


def _as_string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str))


def _as_counts(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    counts: dict[str, int] = {}
    for key, item in value.items():
        if isinstance(key, str) and isinstance(item, int):
            counts[key] = item
    return counts


def _contains_forbidden_manifest_content(value: object) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered_key = str(key).lower()
            if any(forbidden == lowered_key for forbidden in FORBIDDEN_MANIFEST_KEYS):
                return True
            if _contains_forbidden_manifest_content(item):
                return True
        return False

    if isinstance(value, list):
        return any(_contains_forbidden_manifest_content(item) for item in value)

    if isinstance(value, str):
        lowered_value = value.lower()
        return any(fragment in lowered_value for fragment in FORBIDDEN_MANIFEST_VALUE_FRAGMENTS)

    return False


def read_local_data_import_manifest(
    manifest_path: str | Path,
    project_root: str | Path,
) -> LocalDataImportManifestReadResult:
    """Read and validate a local data export manifest without importing anything."""

    manifest = Path(manifest_path)
    root = Path(project_root)
    exports_root = root / "local_data" / "exports"
    reasons: list[LocalDataImportManifestBlockReason] = []

    if not _is_relative_to(manifest, exports_root):
        reasons.append("manifest_outside_exports")
        return _blocked(manifest_path=manifest, reasons=reasons)

    if not manifest.exists():
        reasons.append("manifest_missing")
        return _blocked(manifest_path=manifest, reasons=reasons)

    if not manifest.is_file():
        reasons.append("manifest_not_file")
        return _blocked(manifest_path=manifest, reasons=reasons)

    try:
        loaded = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        reasons.append("manifest_invalid_json")
        return _blocked(manifest_path=manifest, reasons=reasons)

    if not isinstance(loaded, dict):
        reasons.append("manifest_not_object")
        return _blocked(manifest_path=manifest, reasons=reasons)

    missing_fields = tuple(
        field for field in REQUIRED_LOCAL_DATA_IMPORT_MANIFEST_FIELDS if field not in loaded
    )
    if missing_fields:
        reasons.append("missing_required_field")

    if loaded.get("export_type") != "local_data_export":
        reasons.append("invalid_export_type")

    target_root = loaded.get("target_root")
    if isinstance(target_root, str) and target_root:
        target_path = Path(target_root)
        if target_path.is_absolute() and not _is_relative_to(target_path, exports_root):
            reasons.append("target_root_outside_exports")

    if loaded.get("scanner_smoke_passed") is not True:
        reasons.append("scanner_smoke_not_passed")

    if loaded.get("persisted") is not True:
        reasons.append("export_not_persisted")

    if loaded.get("preview_only") is not False:
        reasons.append("export_marked_preview")

    if loaded.get("external_lookup_used") is not False:
        reasons.append("external_lookup_used")

    excluded_items = _as_string_tuple(loaded.get("excluded_items"))
    missing_exclusions = tuple(
        item for item in REQUIRED_LOCAL_DATA_IMPORT_EXCLUSIONS if item not in excluded_items
    )
    if missing_exclusions:
        reasons.append("missing_exclusions")

    if _contains_forbidden_manifest_content(loaded):
        reasons.append("forbidden_manifest_content")

    if reasons:
        return _blocked(
            manifest_path=manifest,
            reasons=reasons,
            missing_fields=missing_fields,
            missing_exclusions=missing_exclusions,
        )

    summary = LocalDataImportManifestSummary(
        export_type=str(loaded["export_type"]),
        target_root=str(loaded["target_root"]),
        sections=_as_string_tuple(loaded["sections"]),
        excluded_items=excluded_items,
        written_files=_as_string_tuple(loaded["written_files"]),
        counts=_as_counts(loaded["counts"]),
        scanner_smoke_passed=loaded["scanner_smoke_passed"] is True,
        preview_only=loaded["preview_only"] is True,
        persisted=loaded["persisted"] is True,
        external_lookup_used=loaded["external_lookup_used"] is True,
    )

    return LocalDataImportManifestReadResult(
        allowed=True,
        manifest_path=str(manifest),
        summary=summary,
        missing_fields=(),
        missing_exclusions=(),
        blocked_reasons=(),
        message="Import-Manifest wurde gelesen. Es wurde nichts importiert.",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
