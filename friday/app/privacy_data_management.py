"""Read-only privacy data management inventory for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from friday import config


@dataclass(frozen=True)
class PrivacyManagedDataArea:
    """A local data area considered for later privacy data management."""

    name: str
    storage: str
    path: str
    visibility: str
    current_access: str
    future_management: str
    safety_boundary: str
    count_label: str
    management_write_available: bool
    management_delete_available: bool
    sensitive_details_hidden: bool


@dataclass(frozen=True)
class PrivacyBlockedManagementAction:
    """An action intentionally blocked until a later explicit gate."""

    name: str
    reason: str
    required_future_gate: str


@dataclass(frozen=True)
class PrivacyDataManagementInventory:
    """Read-only inventory for later local privacy data management."""

    app_name: str
    local_mode: bool
    sqlite_storage: bool
    local_data_dir: str
    database_path: str
    areas: tuple[PrivacyManagedDataArea, ...]
    blocked_actions: tuple[PrivacyBlockedManagementAction, ...]
    writes_performed: bool
    deletes_performed: bool
    exports_performed: bool
    external_lookup_used: bool


def _count_label(count: int | None) -> str:
    if count is None:
        return "nicht gezaehlt"
    return str(count)


def build_privacy_data_management_inventory(
    *,
    local_data_dir: Path | None = None,
    database_path: Path | None = None,
    task_count: int | None = None,
    contact_context_count: int | None = None,
    review_suggestion_count: int | None = None,
    export_count: int | None = None,
    backup_count: int | None = None,
    restore_copy_count: int | None = None,
    import_review_count: int | None = None,
    obsidian_note_count: int | None = None,
    scanner_count: int | None = None,
) -> PrivacyDataManagementInventory:
    """Build a read-only inventory of local data management areas.

    This function does not create folders, open databases, write files,
    delete data, export data, call providers, or perform network access.
    """

    resolved_local_data_dir = Path(local_data_dir or config.LOCAL_DATA_DIR)
    resolved_database_path = Path(database_path or config.DATABASE_PATH)

    areas = (
        PrivacyManagedDataArea(
            name="Aufgaben",
            storage="SQLite lokal",
            path=str(resolved_database_path),
            visibility="Anzahl, Status und lokaler DB-Bezug",
            current_access="vorhandene Task-Flows",
            future_management="spaeter gezielte lokale Pflege ueber bestehende Task-Gates",
            safety_boundary="keine Massenloeschung ohne eigenes Gate",
            count_label=_count_label(task_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Kontakt-Kontexte",
            storage="SQLite lokal",
            path=str(resolved_database_path),
            visibility="Anzahl und Typen ohne sensible Details",
            current_access="Kontakt-CLI mit harten Tokens",
            future_management="spaeter Anzeigen, Suchen, Bearbeiten oder Vergessen",
            safety_boundary="sensible Freitexte bleiben verborgen",
            count_label=_count_label(contact_context_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Review-Vorschlaege",
            storage="SQLite lokal",
            path=str(resolved_database_path),
            visibility="Anzahl und Status",
            current_access="lokaler Review-Flow",
            future_management="spaeter optionale Bereinigung alter lokaler Vorschlaege",
            safety_boundary="kein Versand, keine externen Aktionen",
            count_label=_count_label(review_suggestion_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Exporte",
            storage="lokaler Ordner",
            path=str(resolved_local_data_dir / "exports"),
            visibility="Pfad und Anzahl",
            current_access="token-gated lokaler Datenexport",
            future_management="spaeter alte Exportordner gezielt bereinigen",
            safety_boundary="nur unter local_data/exports",
            count_label=_count_label(export_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Backups",
            storage="lokaler Ordner",
            path=str(resolved_local_data_dir / "backups"),
            visibility="Pfad und Anzahl",
            current_access="token-gated lokaler Backup-Write",
            future_management="spaeter alte Backupordner gezielt bereinigen",
            safety_boundary="aktive Datenbank nie direkt ersetzen",
            count_label=_count_label(backup_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Restore-Kopien",
            storage="lokaler Ordner",
            path=str(resolved_local_data_dir / "restores"),
            visibility="Pfad und Anzahl",
            current_access="token-gated Restore-Kopie",
            future_management="spaeter alte Restore-Kopien gezielt bereinigen",
            safety_boundary="kein In-Place-Restore",
            count_label=_count_label(restore_copy_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Import-Reviews",
            storage="lokale Exportordner",
            path=str(resolved_local_data_dir / "exports"),
            visibility="Manifest-, Dry-Run- und Apply-Status",
            current_access="read-only Review plus token-gated Apply",
            future_management="spaeter alte Import-Pruefungen nachvollziehbar anzeigen",
            safety_boundary="kein Import ohne Backup, Guard, Safety Smoke und Token",
            count_label=_count_label(import_review_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Obsidian-Previews/Writes",
            storage="konfigurierter lokaler Vault-Bereich",
            path=config.OBSIDIAN_ALLOWED_SUBDIR,
            visibility="Preview-, Guard- und Write-Freigabe-Status",
            current_access="token-gated Obsidian-Write",
            future_management="spaeter lokale Write-Historie sichtbar machen",
            safety_boundary="kein Vault-Scan, kein Write ohne Token",
            count_label=_count_label(obsidian_note_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
        PrivacyManagedDataArea(
            name="Safety-Scanner",
            storage="lokale Python-Scanner",
            path="scripts/friday_safety_smoke.py",
            visibility="Scannerliste und PASS/FAIL-Status",
            current_access="lokaler Safety Smoke",
            future_management="spaeter zentral im Privacy-Bereich anzeigen",
            safety_boundary="keine Provider- oder Netzwerkaktionen",
            count_label=_count_label(scanner_count),
            management_write_available=False,
            management_delete_available=False,
            sensitive_details_hidden=True,
        ),
    )

    blocked_actions = (
        PrivacyBlockedManagementAction(
            name="Datenbereich direkt loeschen",
            reason="Loeschungen brauchen ein eigenes Safety-Gate und harte Tokens.",
            required_future_gate="Privacy Data Cleanup Approval Gate",
        ),
        PrivacyBlockedManagementAction(
            name="Aktive SQLite-Datenbank ersetzen",
            reason="In-Place-Restore ist nicht freigegeben.",
            required_future_gate="Restore In-Place Approval Gate",
        ),
        PrivacyBlockedManagementAction(
            name="Secrets oder .env exportieren",
            reason="Secrets bleiben dauerhaft ausgeschlossen.",
            required_future_gate="nicht vorgesehen",
        ),
        PrivacyBlockedManagementAction(
            name="Obsidian Vault scannen",
            reason="Vault-Zugriff bleibt scoped und approval-gated.",
            required_future_gate="Obsidian Vault Privacy Gate",
        ),
        PrivacyBlockedManagementAction(
            name="Externe Provider pruefen",
            reason="Friday bleibt lokal-only.",
            required_future_gate="External Integration Safety Gate",
        ),
    )

    return PrivacyDataManagementInventory(
        app_name=config.APP_NAME,
        local_mode=config.LOCAL_MODE,
        sqlite_storage=config.USE_SQLITE_STORAGE,
        local_data_dir=str(resolved_local_data_dir),
        database_path=str(resolved_database_path),
        areas=areas,
        blocked_actions=blocked_actions,
        writes_performed=False,
        deletes_performed=False,
        exports_performed=False,
        external_lookup_used=False,
    )
