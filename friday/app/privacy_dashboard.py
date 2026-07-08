"""Read-only privacy dashboard model for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from friday import config
from friday.app.forget_person_preview import FORGET_PERSON_APPROVAL_TOKEN


@dataclass(frozen=True)
class PrivacySafetyFlag:
    """A safety flag displayed in the privacy dashboard."""

    name: str
    value: bool
    expected_value: bool
    status: str


@dataclass(frozen=True)
class PrivacyDataArea:
    """A local data area summarized without exposing sensitive details."""

    name: str
    storage: str
    path: str
    count_label: str
    write_status: str
    sensitive_details_hidden: bool


@dataclass(frozen=True)
class PrivacyDashboardLocalCounts:
    """Read-only local count snapshot for the privacy dashboard."""

    task_count: int | None
    contact_count: int | None
    contact_context_count: int | None
    review_suggestion_count: int | None
    backup_count: int | None
    restore_copy_count: int | None
    database_available: bool
    database_readable: bool


@dataclass(frozen=True)
class PrivacyExternalAction:
    """An external action status shown to the user."""

    name: str
    enabled: bool
    status: str


@dataclass(frozen=True)
class PrivacyGatedAction:
    """A local write action that requires a hard approval token."""

    name: str
    token: str
    status: str


@dataclass(frozen=True)
class PrivacyDashboardSummary:
    """Read-only privacy summary for local Friday runtime state."""

    app_name: str
    local_mode: bool
    sqlite_storage: bool
    project_root: str
    local_data_dir: str
    database_path: str
    safety_flags: tuple[PrivacySafetyFlag, ...]
    data_areas: tuple[PrivacyDataArea, ...]
    external_actions: tuple[PrivacyExternalAction, ...]
    gated_actions: tuple[PrivacyGatedAction, ...]
    scanner_names: tuple[str, ...]
    writes_performed: bool
    external_lookup_used: bool


def _flag_status(value: bool, expected_value: bool) -> str:
    if value == expected_value:
        return "safe"
    return "unexpected"


def _count_label(count: int | None) -> str:
    if count is None:
        return "nicht gezaehlt"
    return str(count)


def _count_directories(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for candidate in path.iterdir() if candidate.is_dir())


def _count_table_rows(connection: sqlite3.Connection, table_name: str) -> int:
    exists = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        LIMIT 1
        """,
        (table_name,),
    ).fetchone()
    if exists is None:
        return 0

    row = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
    return int(row[0]) if row is not None else 0


def collect_privacy_dashboard_local_counts(
    *,
    local_data_dir: Path | None = None,
    database_path: Path | None = None,
) -> PrivacyDashboardLocalCounts:
    """Collect local counts without creating paths, schemas, or rows."""

    resolved_local_data_dir = Path(local_data_dir or config.LOCAL_DATA_DIR)
    resolved_database_path = Path(database_path or config.DATABASE_PATH)
    backup_count = _count_directories(resolved_local_data_dir / "backups")
    restore_copy_count = _count_directories(resolved_local_data_dir / "restores")

    task_count: int | None = None
    contact_count: int | None = None
    contact_context_count: int | None = None
    review_suggestion_count: int | None = None
    database_available = resolved_database_path.exists() and resolved_database_path.is_file()
    database_readable = False

    if database_available:
        connection: sqlite3.Connection | None = None
        try:
            uri = f"{resolved_database_path.resolve().as_uri()}?mode=ro"
            connection = sqlite3.connect(uri, uri=True)
            task_count = _count_table_rows(connection, "tasks")
            contact_count = _count_table_rows(connection, "contacts")
            contact_context_count = _count_table_rows(connection, "contact_contexts")
            review_suggestion_count = sum(
                _count_table_rows(connection, table_name)
                for table_name in (
                    "message_suggestions",
                    "task_suggestions",
                    "calendar_suggestions",
                )
            )
            database_readable = True
        except sqlite3.Error:
            task_count = None
            contact_count = None
            contact_context_count = None
            review_suggestion_count = None
            database_readable = False
        finally:
            if connection is not None:
                connection.close()

    return PrivacyDashboardLocalCounts(
        task_count=task_count,
        contact_count=contact_count,
        contact_context_count=contact_context_count,
        review_suggestion_count=review_suggestion_count,
        backup_count=backup_count,
        restore_copy_count=restore_copy_count,
        database_available=database_available,
        database_readable=database_readable,
    )


def build_privacy_dashboard_summary(
    *,
    project_root: Path | None = None,
    local_data_dir: Path | None = None,
    database_path: Path | None = None,
    task_count: int | None = None,
    contact_count: int | None = None,
    contact_context_count: int | None = None,
    review_suggestion_count: int | None = None,
    backup_count: int | None = None,
    restore_copy_count: int | None = None,
) -> PrivacyDashboardSummary:
    """Build a read-only privacy dashboard summary.

    The function does not write files, change configuration, call providers,
    connect to a network, or inspect sensitive row-level data.
    """

    resolved_project_root = Path(project_root or config.PROJECT_ROOT)
    resolved_local_data_dir = Path(local_data_dir or config.LOCAL_DATA_DIR)
    resolved_database_path = Path(database_path or config.DATABASE_PATH)

    safety_flags = (
        PrivacySafetyFlag(
            "ENABLE_REAL_EMAIL",
            config.ENABLE_REAL_EMAIL,
            False,
            _flag_status(config.ENABLE_REAL_EMAIL, False),
        ),
        PrivacySafetyFlag(
            "ENABLE_REAL_WHATSAPP",
            config.ENABLE_REAL_WHATSAPP,
            False,
            _flag_status(config.ENABLE_REAL_WHATSAPP, False),
        ),
        PrivacySafetyFlag(
            "ENABLE_REAL_SMS",
            config.ENABLE_REAL_SMS,
            False,
            _flag_status(config.ENABLE_REAL_SMS, False),
        ),
        PrivacySafetyFlag(
            "ENABLE_REAL_CALENDAR",
            config.ENABLE_REAL_CALENDAR,
            False,
            _flag_status(config.ENABLE_REAL_CALENDAR, False),
        ),
        PrivacySafetyFlag(
            "ENABLE_REAL_WEATHER",
            config.ENABLE_REAL_WEATHER,
            False,
            _flag_status(config.ENABLE_REAL_WEATHER, False),
        ),
        PrivacySafetyFlag(
            "ENABLE_REAL_MUSIC",
            config.ENABLE_REAL_MUSIC,
            False,
            _flag_status(config.ENABLE_REAL_MUSIC, False),
        ),
        PrivacySafetyFlag(
            "REQUIRE_USER_APPROVAL",
            config.REQUIRE_USER_APPROVAL,
            True,
            _flag_status(config.REQUIRE_USER_APPROVAL, True),
        ),
        PrivacySafetyFlag(
            "USE_SQLITE_STORAGE",
            config.USE_SQLITE_STORAGE,
            True,
            _flag_status(config.USE_SQLITE_STORAGE, True),
        ),
    )

    data_areas = (
        PrivacyDataArea(
            name="Aufgaben",
            storage="SQLite lokal",
            path=str(resolved_database_path),
            count_label=_count_label(task_count),
            write_status="lokal, nutzergesteuert",
            sensitive_details_hidden=True,
        ),
        PrivacyDataArea(
            name="Kontakte",
            storage="SQLite lokal",
            path=str(resolved_database_path),
            count_label=_count_label(contact_count),
            write_status="lokal, nutzergesteuert",
            sensitive_details_hidden=True,
        ),
        PrivacyDataArea(
            name="Kontakt-Kontexte",
            storage="SQLite lokal",
            path=str(resolved_database_path),
            count_label=_count_label(
                contact_context_count if contact_context_count is not None else contact_count
            ),
            write_status="nur mit SPEICHERN",
            sensitive_details_hidden=True,
        ),
        PrivacyDataArea(
            name="Review-Vorschlaege",
            storage="SQLite lokal",
            path=str(resolved_database_path),
            count_label=_count_label(review_suggestion_count),
            write_status="lokal, nutzergesteuert",
            sensitive_details_hidden=True,
        ),
        PrivacyDataArea(
            name="Backups",
            storage="lokaler Ordner",
            path=str(resolved_local_data_dir / "backups"),
            count_label=_count_label(backup_count),
            write_status="nur mit BACKUP ERSTELLEN",
            sensitive_details_hidden=True,
        ),
        PrivacyDataArea(
            name="Restore-Kopien",
            storage="lokaler Ordner",
            path=str(resolved_local_data_dir / "restores"),
            count_label=_count_label(restore_copy_count),
            write_status="nur mit RESTORE AUSFUEHREN",
            sensitive_details_hidden=True,
        ),
    )

    external_actions = (
        PrivacyExternalAction("E-Mail", config.ENABLE_REAL_EMAIL, "deaktiviert"),
        PrivacyExternalAction("WhatsApp", config.ENABLE_REAL_WHATSAPP, "deaktiviert"),
        PrivacyExternalAction("SMS", config.ENABLE_REAL_SMS, "deaktiviert"),
        PrivacyExternalAction("Kalender", config.ENABLE_REAL_CALENDAR, "deaktiviert"),
        PrivacyExternalAction("Wetter", config.ENABLE_REAL_WEATHER, "deaktiviert"),
        PrivacyExternalAction("Musik", config.ENABLE_REAL_MUSIC, "deaktiviert"),
    )

    gated_actions = (
        PrivacyGatedAction("Kontakt-Kontext sichern", "SPEICHERN", "hart gegatet"),
        PrivacyGatedAction("Kontakt-Kontext entfernen", "KONTAKT LÖSCHEN", "hart gegatet"),
        PrivacyGatedAction("Person vergessen", FORGET_PERSON_APPROVAL_TOKEN, "hart gegatet"),
        PrivacyGatedAction("Obsidian-Notiz", "OBSIDIAN SCHREIBEN", "hart gegatet"),
        PrivacyGatedAction("Backup erstellen", "BACKUP ERSTELLEN", "hart gegatet"),
        PrivacyGatedAction("Restore-Kopie erstellen", "RESTORE AUSFUEHREN", "hart gegatet"),
    )

    scanner_names = (
        "forbidden_imports",
        "no_network",
        "no_input_print",
        "safety_flags",
        "approval_tokens",
    )

    return PrivacyDashboardSummary(
        app_name=config.APP_NAME,
        local_mode=config.LOCAL_MODE,
        sqlite_storage=config.USE_SQLITE_STORAGE,
        project_root=str(resolved_project_root),
        local_data_dir=str(resolved_local_data_dir),
        database_path=str(resolved_database_path),
        safety_flags=safety_flags,
        data_areas=data_areas,
        external_actions=external_actions,
        gated_actions=gated_actions,
        scanner_names=scanner_names,
        writes_performed=False,
        external_lookup_used=False,
    )
