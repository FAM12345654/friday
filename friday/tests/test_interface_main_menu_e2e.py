"""End-to-end style tests for Friday CLI menu and review stability."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from dataclasses import dataclass
import json
import sqlite3

import friday.config as config
from friday.app.backup_write_guard import BACKUP_WRITE_APPROVAL_TOKEN
from friday.app.forget_person_preview import FORGET_PERSON_APPROVAL_TOKEN
from friday.app.interface import FridayInterface
from friday.app.local_data_export_preview import LOCAL_DATA_EXPORT_APPROVAL_TOKEN
from friday.app.local_data_import_apply_preview import LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN
from friday.app.privacy_cleanup_db_preview import CONTACT_DB_CLEANUP_TOKEN, REVIEW_DB_CLEANUP_TOKEN
from friday.app.restore_write_guard import RESTORE_WRITE_APPROVAL_TOKEN
from friday.agents.task_agent import TaskAgent
from friday.storage.contact_context_repository import ContactContextRepository
from friday.storage.database import initialize_database


class _TaskAgentStub:
    def get_open_tasks(self) -> List[Dict[str, Any]]:
        return []

    def detect_priority_hint(self, task: Dict[str, Any]) -> str:
        return "normal"

    def get_task_by_id(self, task_id: int) -> Dict[str, Any] | None:
        return None


class _MessageAgentStub:
    def get_messages(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "sender": "Chef",
                "text": "Bitte bitte den Report prüfen.",
                "received_at": "2026-07-05T08:00:00",
            }
        ]

    def detect_intent(self, text: str) -> str:
        if "treffen" in text.lower() or "termin" in text.lower():
            return "scheduling"
        return "task"

    def create_reply_suggestion(self, message: Dict[str, Any]) -> str:
        return f"Vorschlag für {message['sender']}"

    def get_contact_type(self, sender: str) -> str:
        return "Kunde"

    def generate_local_suggestions(self) -> list[dict]:
        return []

    def generate_local_task_suggestions(self) -> list[dict]:
        return []

    def get_pending_suggestions(self) -> list[dict]:
        return []

    def get_pending_task_suggestions(self) -> list[dict]:
        return []


class _ReviewableMessageAgentStub(_MessageAgentStub):
    def __init__(self) -> None:
        super().__init__()
        self._messages = [
            {"id": 10, "sender": "Chef", "text": "Bitte prüfe den Termin.", "received_at": "2026-07-05T09:00:00"},
            {"id": 11, "sender": "Chef", "text": "Bitte prüfe den Bericht.", "received_at": "2026-07-05T09:15:00"},
        ]
        self._message_suggestions = [
            {"id": 100, "message_id": 10, "draft_text": "Rückmeldung bitte senden.", "status": "pending"},
        ]
        self._task_suggestions = [
            {
                "id": 200,
                "message_id": 11,
                "title": "Bericht prüfen",
                "category": "arbeit",
                "due_date": "2026-07-05",
                "notes": "Aus der Nachricht abgeleitet",
                "priority": "normal",
                "status": "pending",
            }
        ]

    def get_messages(self) -> List[Dict[str, Any]]:
        return self._messages

    def generate_local_suggestions(self) -> list[dict]:
        return self._message_suggestions

    def generate_local_task_suggestions(self) -> list[dict]:
        return self._task_suggestions

    def get_pending_suggestions(self) -> list[dict]:
        return list(self._message_suggestions)

    def get_pending_task_suggestions(self) -> list[dict]:
        return list(self._task_suggestions)

    def create_reply_suggestion(self, message: Dict[str, Any]) -> str:
        return "Vorschlagstext"


class _MessageAgentNoSuggestions(_MessageAgentStub):
    def get_messages(self) -> List[Dict[str, Any]]:
        return []

    def generate_local_suggestions(self) -> list[dict]:
        return []

    def generate_local_task_suggestions(self) -> list[dict]:
        return []

    def get_pending_suggestions(self) -> list[dict]:
        return []

    def get_pending_task_suggestions(self) -> list[dict]:
        return []


def _build_task_agent(tmp_path):
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    return TaskAgent(db_path=db_path)


class _CalendarAgentStub:
    def get_free_slots_today(self, duration_minutes: int = 60) -> list[dict]:
        return [{"start": "10:00", "end": "11:00"}]


class _BriefingAgentStub:
    def build_preview(self, today_iso: str | None = None) -> dict[str, Any]:
        return {
            "date": "2026-07-05",
            "tasks": [],
            "calendar_items": [],
            "weather": "Demo-Wetter: klar",
            "music": "Demo-Musik: Fokus",
        }


@dataclass(frozen=True)
class _SmokeResultStub:
    passed: bool


def _build_interface() -> FridayInterface:
    return FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        briefing_agent=_BriefingAgentStub(),
        approval_agent=None,
    )


def _build_interface_with_task_agent(task_agent: TaskAgent) -> FridayInterface:
    return FridayInterface(
        task_agent=task_agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )


def _build_interface_with_contact_repository(tmp_path) -> tuple[FridayInterface, ContactContextRepository]:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    repository = ContactContextRepository(db_path)
    interface = FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        contact_context_repository=repository,
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )
    return interface, repository


def _build_review_interface() -> FridayInterface:
    return FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_ReviewableMessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )


def _build_review_interface_without_pending() -> FridayInterface:
    return FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_MessageAgentNoSuggestions(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )


def _privacy_area_count(output: str, area_name: str) -> str:
    lines = output.splitlines()
    marker = f"- {area_name}:"
    for index, line in enumerate(lines):
        if line.startswith(marker):
            for detail in lines[index : index + 6]:
                stripped = detail.strip()
                if stripped.startswith("Anzahl:"):
                    return stripped.split(":", 1)[1].strip()
    raise AssertionError(f"Count for {area_name!r} was not shown.")


def _set_inputs(monkeypatch, values: list[str]) -> None:
    iterator = iter(values)

    def _next_input(_: str = "") -> str:
        return next(iterator)

    monkeypatch.setattr("builtins.input", _next_input)


def test_handle_menu_choice_exit(monkeypatch, capsys) -> None:
    interface = _build_interface()
    assert interface.handle_menu_choice("7") is False
    output = capsys.readouterr().out
    assert "Friday wird beendet." in output


def test_show_dashboard_includes_local_onboarding_note(capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard()
    output = capsys.readouterr().out

    assert "Start-Hinweis" in output
    assert "Willkommen bei Friday 1.0.0 (lokale CLI)." in output
    assert "Friday 1.0.0 – lokaler Assistent gestartet." in output
    assert "Alle Aktionen sind lokal" in output


def test_run_shows_onboarding_note_once_on_startup(monkeypatch, capsys) -> None:
    interface = _build_interface()
    choices = iter(["8", "7"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(choices))

    interface.run()
    output = capsys.readouterr().out

    assert output.count("Willkommen bei Friday 1.0.0 (lokale CLI).") == 1
    assert "Hilfe / Übersicht" in output
    assert "Friday wird beendet." in output


def test_handle_menu_choice_invalid_input(monkeypatch, capsys) -> None:
    interface = _build_interface()
    assert interface.handle_menu_choice("x") is True
    output = capsys.readouterr().out
    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_handle_menu_choice_obsidian_brain_preview_stays_local(tmp_path, capsys) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task(
        title="Obsidian Aufgabe",
        category="arbeit",
        due_date="2026-07-06",
        notes="Nur lokale Preview",
        priority="high",
    )
    interface = _build_interface_with_task_agent(task_agent)

    assert interface.handle_menu_choice("10") is True
    output = capsys.readouterr().out

    assert "Obsidian Brain Preview" in output
    assert "Aufgaben/obsidian-aufgabe.md" in output
    assert "Obsidian Write ist deaktiviert. Es wurde nichts geschrieben." in output


def test_handle_menu_choice_backup_restore_menu_returns(tmp_path, monkeypatch, capsys) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["9"])

    assert interface.handle_menu_choice("11") is True
    output = capsys.readouterr().out

    assert "Backup / Restore" in output


def test_handle_menu_choice_email_draft_preview_stays_local(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["1", "6"])

    assert interface.handle_menu_choice("13") is True
    output = capsys.readouterr().out

    assert "E-Mail-Entwurf Preview" in output
    assert "E-Mail-Entwurf (lokal, nicht gesendet)" in output
    assert "Es wurde nichts gesendet." in output
    assert "Kein E-Mail-Provider ist verbunden." in output
    assert "Dies ist nur eine lokale Vorschau." in output
    assert len(interface.email_drafts) == 1


def test_email_draft_preview_can_create_edit_discard_and_return(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(
        monkeypatch,
        [
            "2",
            "Max",
            "Hallo",
            "Lokaler Entwurf",
            "4",
            "Neuer Betreff",
            "Neuer Text",
            "5",
            "6",
        ],
    )

    interface.show_email_draft_preview()
    output = capsys.readouterr().out

    assert "E-Mail-Entwurf (lokal, nicht gesendet)" in output
    assert "Betreff: Neuer Betreff" in output
    assert "Neuer Text" in output
    assert "E-Mail-Entwurf wurde lokal verworfen." in output
    assert interface.email_drafts[-1].status == "discarded"


def test_email_draft_preview_back_without_draft_is_stable(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["3", "4", "5", "6"])

    interface.show_email_draft_preview()
    output = capsys.readouterr().out

    assert "Keine lokalen E-Mail-Entwürfe in dieser Session." in output
    assert "Kein lokaler E-Mail-Entwurf zum Bearbeiten vorhanden." in output
    assert "Kein lokaler E-Mail-Entwurf zum Verwerfen vorhanden." in output
    assert interface.email_drafts == []


def test_backup_restore_menu_backup_rotation_deletes_old_backups_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    backups_root = tmp_path / "local_data" / "backups"
    old_backup = backups_root / "friday_backup_20260701_100000"
    latest_backup = backups_root / "friday_backup_20260702_100000"
    old_backup.mkdir(parents=True)
    latest_backup.mkdir(parents=True)
    old_backup_file = old_backup / "marker.txt"
    latest_backup_file = latest_backup / "marker.txt"
    old_backup_file.write_text("old", encoding="utf-8")
    latest_backup_file.write_text("latest", encoding="utf-8")
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr("friday.app.interface.run_safety_smoke", lambda: _SmokeResultStub(True))
    _set_inputs(monkeypatch, ["10", "BACKUP AUFRAEUMEN", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Backups aufraeumen" in output
    assert "Backup-Rotation wurde lokal ausgefuehrt." in output
    assert old_backup.exists() is False
    assert latest_backup.exists() is True
    assert latest_backup_file.read_text(encoding="utf-8") == "latest"


def test_handle_menu_choice_privacy_dashboard_menu_returns(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["11"])

    assert interface.handle_menu_choice("12") is True
    output = capsys.readouterr().out

    assert "Privacy Dashboard" in output
    assert "Friday arbeitet lokal." in output
    assert "Externe Aktionen sind deaktiviert." in output


def test_privacy_dashboard_menu_shows_local_data_areas(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["1", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Lokale Datenbereiche" in output
    assert "Aufgaben" in output
    assert "Kontakt-Kontexte" in output
    assert "Restore-Kopien" in output
    assert "sensible Inhalte werden nicht angezeigt." in output


def test_privacy_dashboard_menu_shows_local_sqlite_counts(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    db_path = Path(task_agent.db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES ('Task 1', 'work', 'open', NULL, '', 'normal')
            """
        )
        connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES ('Task 2', 'home', 'done', NULL, '', 'low')
            """
        )
        connection.execute(
            """
            INSERT INTO contacts (name, contact_type, notes)
            VALUES ('Ada', 'work', '')
            """
        )
        connection.execute(
            """
            INSERT INTO contact_contexts (
                contact_id,
                display_name,
                normalized_name,
                contact_type,
                source_context,
                created_at,
                updated_at
            )
            VALUES (
                'ada',
                'Ada',
                'ada',
                'work',
                'test',
                '2026-07-08T10:00:00+00:00',
                '2026-07-08T10:00:00+00:00'
            )
            """
        )
        connection.execute(
            """
            INSERT INTO message_suggestions (message_id, draft_text, status)
            VALUES (1, 'Draft', 'pending')
            """
        )
        connection.execute(
            """
            INSERT INTO task_suggestions (message_id, title, status)
            VALUES (1, 'Review Task', 'pending')
            """
        )

    (tmp_path / "local_data" / "backups" / "friday_backup_1").mkdir(parents=True)
    (tmp_path / "local_data" / "restores" / "friday_restore_1").mkdir(parents=True)
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["1", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "SQLite-Status: read-only gezaehlt." in output
    assert _privacy_area_count(output, "Aufgaben") == "2"
    assert _privacy_area_count(output, "Kontakte") == "1"
    assert _privacy_area_count(output, "Kontakt-Kontexte") == "1"
    assert _privacy_area_count(output, "Review-Vorschlaege") == "2"
    assert _privacy_area_count(output, "Backups") == "1"
    assert _privacy_area_count(output, "Restore-Kopien") == "1"


def test_privacy_dashboard_menu_shows_safety_flags(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["2", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Safety-Flags" in output
    assert "ENABLE_REAL_EMAIL: False" in output
    assert "REQUIRE_USER_APPROVAL: True" in output
    assert "USE_SQLITE_STORAGE: True" in output


def test_privacy_dashboard_menu_shows_external_actions(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["3", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Externe Aktionen" in output
    assert "E-Mail: deaktiviert" in output
    assert "WhatsApp: deaktiviert" in output
    assert "Kalender: deaktiviert" in output


def test_privacy_dashboard_menu_shows_gated_actions_as_status(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["4", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Gated Actions" in output
    assert "Kontakt-Kontext sichern" in output
    assert "Token: SPEICHERN" in output
    assert "Token: RESTORE AUSFUEHREN" in output


def test_privacy_dashboard_menu_shows_safety_scanners(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["5", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Safety Scanner" in output
    assert "forbidden_imports" in output
    assert "approval_tokens" in output
    assert "lokaler Prüfpfad" in output


def test_privacy_dashboard_menu_shows_data_management_inventory(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["6", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Privacy Data Management Inventory" in output
    assert "Diese Ansicht ist read-only" in output
    assert "Aufgaben" in output
    assert "Kontakt-Kontexte" in output
    assert "Datenbereich direkt loeschen" in output


def test_privacy_dashboard_menu_shows_cleanup_preview(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["7", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Privacy Cleanup Preview" in output
    assert "Diese Ansicht ist read-only" in output
    assert "Exporte" in output
    assert "EXPORT AUFRAEUMEN" in output
    assert "aktive SQLite-DB" in output
    assert "active_database_blocked" in output
    assert "global_delete_blocked" in output


def test_privacy_dashboard_menu_shows_db_cleanup_preview_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["9", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "DB-Cleanup Preview" in output
    assert "Diese Ansicht ist read-only" in output
    assert "Es wird nichts aus SQLite gelöscht oder geschrieben." in output
    assert "Review-History" in output
    assert "REVIEW AUFRAEUMEN" in output
    assert "Kontakt-Kontext" in output
    assert "KONTAKT LÖSCHEN" in output
    assert "Aufgaben" in output
    assert "task_cleanup_requires_separate_gate" in output
    assert "schema_cleanup_blocked" in output


def _insert_db_cleanup_review_candidates(db_path: Path) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO message_suggestions (
                message_id,
                suggestion_type,
                draft_text,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (9901, "reply", "Nicht anzeigen", "rejected"),
        )
        cursor = connection.execute(
            """
            INSERT INTO tasks (title, category, status, due_date, notes, priority)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("DB Cleanup Aufgabe", "arbeit", "open", None, "", "medium"),
        )
        connection.execute(
            """
            INSERT INTO task_suggestions (
                message_id,
                title,
                status,
                created_task_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (9902, "Nicht anzeigen", "converted", int(cursor.lastrowid)),
        )
        connection.execute(
            """
            INSERT INTO message_suggestions (
                message_id,
                suggestion_type,
                draft_text,
                status
            )
            VALUES (?, ?, ?, ?)
            """,
            (9903, "reply", "Pending bleibt", "pending"),
        )


def _insert_db_cleanup_contact_context(db_path: Path, contact_id: str) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO contact_contexts (
                contact_id,
                display_name,
                normalized_name,
                contact_type,
                source_context,
                user_approved_persistence,
                sensitivity_checked,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                contact_id,
                "Max Mustermann",
                "max mustermann",
                "kunde",
                "test",
                1,
                1,
                "2026-07-08T10:00:00",
                "2026-07-08T10:00:00",
            ),
        )


def _db_count(db_path: Path, table_name: str, where_sql: str = "1 = 1") -> int:
    with sqlite3.connect(db_path) as connection:
        row = connection.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {where_sql}").fetchone()
    return int(row[0])


def _create_backup_marker(tmp_path: Path) -> None:
    (tmp_path / "local_data" / "backups" / "backup-01").mkdir(parents=True)


def test_privacy_dashboard_db_cleanup_missing_backup_blocks(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    _insert_db_cleanup_review_candidates(task_agent.db_path)
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["10", "1", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "DB-Cleanup Preview" in output
    assert "DB-Cleanup wurde blockiert: Backup fehlt." in output
    assert _db_count(task_agent.db_path, "message_suggestions", "status = 'rejected'") == 1


def test_privacy_dashboard_db_cleanup_wrong_token_does_not_delete(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    _insert_db_cleanup_review_candidates(task_agent.db_path)
    _create_backup_marker(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["10", "1", "JA", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "DB-Cleanup wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert _db_count(task_agent.db_path, "message_suggestions", "status = 'rejected'") == 1


def test_privacy_dashboard_db_cleanup_exact_token_deletes_review_history(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    _insert_db_cleanup_review_candidates(task_agent.db_path)
    _create_backup_marker(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["10", "1", REVIEW_DB_CLEANUP_TOKEN, "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "DB-Cleanup wurde lokal ausgefuehrt." in output
    assert "message_suggestions: 1" in output
    assert "task_suggestions: 1" in output
    assert _db_count(task_agent.db_path, "message_suggestions", "status = 'rejected'") == 0
    assert _db_count(task_agent.db_path, "task_suggestions", "status = 'converted'") == 0
    assert _db_count(task_agent.db_path, "message_suggestions", "status = 'pending'") == 1
    assert _db_count(task_agent.db_path, "tasks", "title = 'DB Cleanup Aufgabe'") == 1


def test_privacy_dashboard_db_cleanup_exact_token_deletes_selected_contact(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    _insert_db_cleanup_contact_context(task_agent.db_path, "contact-01")
    _insert_db_cleanup_contact_context(task_agent.db_path, "contact-02")
    _create_backup_marker(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["10", "2", "contact-01", CONTACT_DB_CLEANUP_TOKEN, "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "DB-Cleanup wurde lokal ausgefuehrt." in output
    assert "contact_contexts: 1" in output
    assert _db_count(task_agent.db_path, "contact_contexts", "contact_id = 'contact-01'") == 0
    assert _db_count(task_agent.db_path, "contact_contexts", "contact_id = 'contact-02'") == 1


def test_privacy_dashboard_menu_invalid_input_then_back(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["x", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_run_can_open_privacy_dashboard_then_exit(monkeypatch, capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]
    main_choices = iter(["12", "7"])
    privacy_choices = iter(["11"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_choices))
    monkeypatch.setattr(
        "friday.app.interface.show_privacy_dashboard_menu",
        lambda: next(privacy_choices),
    )

    interface.run()
    output = capsys.readouterr().out

    assert "Privacy Dashboard" in output
    assert "Friday wird beendet." in output


def test_privacy_dashboard_cleanup_wrong_token_does_not_delete(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    target = tmp_path / "local_data" / "exports" / "old_export"
    target.mkdir(parents=True)
    (target / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["8", "1", str(target), "JA", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Privacy Cleanup wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert target.exists() is True


def test_privacy_dashboard_cleanup_exact_token_deletes_allowed_export(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    target = tmp_path / "local_data" / "exports" / "old_export"
    target.mkdir(parents=True)
    (target / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["8", "1", str(target), "EXPORT AUFRAEUMEN", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Privacy Cleanup wurde lokal ausgefuehrt." in output
    assert "Gelöscht:" in output
    assert target.exists() is False


def test_privacy_dashboard_cleanup_blocks_contact_cleanup_area(
    monkeypatch,
    capsys,
) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["8", "4", "11"])

    interface.open_privacy_dashboard_menu()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_backup_restore_menu_shows_backup_preview_without_writing(tmp_path, monkeypatch, capsys) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["1", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Backup-Vorschau" in output
    assert "Geplanter Zielordner:" in output
    assert "Es wurde nichts geschrieben." in output
    assert (tmp_path / "local_data" / "backups").exists() is False


def test_backup_restore_menu_shows_local_data_export_preview_without_exporting(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["5", "", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Lokaler Datenexport Vorschau" in output
    assert "Geplanter Zielordner:" in output
    assert "local_data" in output
    assert "exports" in output
    assert "Es wurde kein Export erstellt." in output
    assert "Safety Smoke: PASS" in output
    assert "Datenexport wurde abgebrochen." in output
    assert "Aufgaben" in output
    assert "Kontakt-Kontexte" in output
    assert "raw_active_database" in output
    assert (tmp_path / "local_data" / "exports").exists() is False


def test_backup_restore_menu_local_data_export_wrong_token_does_not_export(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["5", "JA", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Datenexport wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert (tmp_path / "local_data" / "exports").exists() is False


def test_backup_restore_menu_local_data_export_hard_token_writes_export(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task(
        title="Exportierte Aufgabe",
        category="arbeit",
        due_date="2026-07-07",
        notes="Lokaler Export Test",
        priority="high",
    )
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["5", LOCAL_DATA_EXPORT_APPROVAL_TOKEN, "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    export_root = tmp_path / "local_data" / "exports" / "friday_data_export_YYYYMMDD_HHMMSS"
    manifest_path = export_root / "manifest.json"
    tasks_path = export_root / "tasks" / "tasks.json"

    assert "Datenexport wurde lokal erstellt." in output
    assert "manifest.json" in output
    assert manifest_path.exists()
    assert tasks_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    exported_tasks = json.loads(tasks_path.read_text(encoding="utf-8"))

    assert manifest["export_type"] == "local_data_export"
    assert manifest["scanner_smoke_passed"] is True
    assert manifest["counts"]["tasks"] == 1
    assert exported_tasks[0]["title"] == "Exportierte Aufgabe"
    assert not (export_root / "raw_active_database").exists()


def test_backup_restore_menu_local_data_import_review_checks_export_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task("Import Review Aufgabe")
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )

    _set_inputs(monkeypatch, ["5", LOCAL_DATA_EXPORT_APPROVAL_TOKEN, "9"])
    interface.open_backup_restore_menu()
    capsys.readouterr()

    export_root = tmp_path / "local_data" / "exports" / "friday_data_export_YYYYMMDD_HHMMSS"
    before = sorted(path.relative_to(export_root).as_posix() for path in export_root.rglob("*"))

    _set_inputs(monkeypatch, ["6", str(export_root), "9"])
    interface.open_backup_restore_menu()
    output = capsys.readouterr().out
    after = sorted(path.relative_to(export_root).as_posix() for path in export_root.rglob("*"))

    assert "Lokalen Datenimport prüfen" in output
    assert "Import-Review wurde read-only geprüft." in output
    assert "Import Dry-Run ist bereit. Es wurde nichts importiert." in output
    assert "Es wurde nichts importiert." in output
    assert "Es wurde nichts wiederhergestellt." in output
    assert "Es wurde nichts geschrieben." in output
    assert "tasks/tasks.json: present" in output
    assert before == after


def test_backup_restore_menu_local_data_import_review_blocks_missing_export(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    missing_export = tmp_path / "local_data" / "exports" / "missing_export"

    _set_inputs(monkeypatch, ["6", str(missing_export), "9"])
    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Lokalen Datenimport prüfen" in output
    assert "Import-Manifest wurde blockiert. Es wurde nichts importiert." in output
    assert "Import Dry-Run wurde blockiert. Es wurde nichts importiert." in output
    assert "manifest_missing" in output
    assert "manifest_blocked" in output
    assert missing_export.exists() is False


def test_backup_restore_menu_restore_dry_run_checks_backup_without_writing(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    backup_root = tmp_path / "local_data" / "backups" / "backup"
    backup_root.mkdir(parents=True)
    (backup_root / "manifest.json").write_text(
        '{"planned_backup_root": "' + str(backup_root).replace("\\", "\\\\") + '", "included_sections": []}',
        encoding="utf-8",
    )
    before = sorted(path.relative_to(backup_root).as_posix() for path in backup_root.rglob("*"))
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["3", str(backup_root), "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out
    after = sorted(path.relative_to(backup_root).as_posix() for path in backup_root.rglob("*"))

    assert "Restore-Dry-Run" in output
    assert "Es wurde nichts zurückgeschrieben." in output
    assert before == after


def test_backup_restore_menu_invalid_input_then_back(monkeypatch, capsys) -> None:
    interface = _build_interface()
    _set_inputs(monkeypatch, ["x", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_backup_restore_menu_backup_write_enter_aborts_without_writing(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["2", "", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Backup wurde abgebrochen." in output
    assert (tmp_path / "local_data" / "backups").exists() is False


def test_backup_restore_menu_backup_write_rejects_wrong_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["2", "JA", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Backup wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert (tmp_path / "local_data" / "backups").exists() is False


def test_backup_restore_menu_backup_write_blocks_when_smoke_fails(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=False),
    )
    _set_inputs(monkeypatch, ["2", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Backup wurde blockiert, weil der Safety Smoke nicht erfolgreich war." in output
    assert (tmp_path / "local_data" / "backups").exists() is False


def test_backup_restore_menu_backup_write_creates_local_backup_with_hard_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(
        "friday.app.interface.run_safety_smoke",
        lambda: _SmokeResultStub(passed=True),
    )
    _set_inputs(monkeypatch, ["2", BACKUP_WRITE_APPROVAL_TOKEN, "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out
    backups = list((tmp_path / "local_data" / "backups").glob("friday_backup_*"))

    assert "Backup wurde lokal erstellt." in output
    assert len(backups) == 1
    assert (backups[0] / "manifest.json").exists()


def _write_restore_cli_backup(project_root: Path) -> Path:
    local_data = project_root / "local_data"
    exports = local_data / "exports"
    docs = project_root / "friday" / "docs"
    exports.mkdir(parents=True)
    docs.mkdir(parents=True)
    db_path = local_data / "friday.sqlite"
    db_path.write_text("active-db", encoding="utf-8")
    (exports / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    (docs / "SAFETY_MATRIX.md").write_text("# Safety\n", encoding="utf-8")
    (docs / "TEST_MATRIX.md").write_text("# Tests\n", encoding="utf-8")
    (docs / "FRIDAY_ARCHITECTURE.md").write_text("# Architecture\n", encoding="utf-8")

    from friday.app.backup_preview import build_backup_preview
    from friday.app.backup_writer import write_local_backup

    preview = build_backup_preview(project_root, timestamp="20260707_120000")
    backup = write_local_backup(
        preview=preview,
        approval_token=BACKUP_WRITE_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=project_root,
    )
    assert backup.persisted is True
    assert backup.target_path is not None
    db_path.unlink()
    return Path(backup.target_path)


def test_backup_restore_menu_restore_copy_enter_aborts_without_writing(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    backup_root = _write_restore_cli_backup(tmp_path)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    task_agent_db = Path(task_agent.db_path)
    task_agent_db.unlink()
    _set_inputs(monkeypatch, ["4", str(backup_root), "", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Restore wurde abgebrochen." in output
    assert (tmp_path / "local_data" / "restores").exists() is False


def test_backup_restore_menu_restore_copy_rejects_wrong_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    backup_root = _write_restore_cli_backup(tmp_path)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    task_agent_db = Path(task_agent.db_path)
    task_agent_db.unlink()
    _set_inputs(monkeypatch, ["4", str(backup_root), "BACKUP ERSTELLEN", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Restore Write wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert (tmp_path / "local_data" / "restores").exists() is False


def test_backup_restore_menu_restore_copy_blocks_failed_dry_run(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    missing_backup = tmp_path / "local_data" / "backups" / "missing"
    _set_inputs(monkeypatch, ["4", str(missing_backup), "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Restore wurde blockiert, weil der Dry-Run nicht erfolgreich war." in output
    assert (tmp_path / "local_data" / "restores").exists() is False


def test_backup_restore_menu_restore_copy_blocks_active_database_conflict(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    backup_root = _write_restore_cli_backup(tmp_path)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["4", str(backup_root), RESTORE_WRITE_APPROVAL_TOKEN, "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Restore Write wurde nicht freigegeben." in output
    assert "active_database_conflict" in output
    assert (tmp_path / "local_data" / "restores").exists() is False


def test_backup_restore_menu_restore_copy_creates_separate_restore_folder(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    backup_root = _write_restore_cli_backup(tmp_path)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    task_agent_db = Path(task_agent.db_path)
    task_agent_db.unlink()
    _set_inputs(monkeypatch, ["4", str(backup_root), RESTORE_WRITE_APPROVAL_TOKEN, "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out
    restores = list((tmp_path / "local_data" / "restores").glob("friday_restore_*"))

    assert "Restore wurde lokal in einen separaten Ordner kopiert." in output
    assert len(restores) == 1
    assert (restores[0] / "RESTORE_MANIFEST.json").exists()
    assert task_agent_db.exists() is False


def test_handle_menu_choice_safety_status(tmp_path, capsys) -> None:
    interface = _build_interface()
    interface.handle_menu_choice("5")
    output = capsys.readouterr().out

    assert f"E-Mail echt aktiv: {config.ENABLE_REAL_EMAIL}" in output
    assert f"WhatsApp echt aktiv: {config.ENABLE_REAL_WHATSAPP}" in output
    assert f"SMS echt aktiv: {config.ENABLE_REAL_SMS}" in output
    assert f"Kalender echt aktiv: {config.ENABLE_REAL_CALENDAR}" in output
    assert f"Wetter echt aktiv: {config.ENABLE_REAL_WEATHER}" in output
    assert f"Musik echt aktiv: {config.ENABLE_REAL_MUSIC}" in output
    assert f"Nutzerfreigabe erforderlich: {config.REQUIRE_USER_APPROVAL}" in output
    assert "Kompakter Systemstatus:" in output
    assert f"Local Mode: {config.LOCAL_MODE}" in output
    assert f"Demo Mode: {config.DEMO_MODE}" in output
    assert f"Use Real Today: {config.USE_REAL_TODAY}" in output
    assert f"SQLite Storage: {config.USE_SQLITE_STORAGE}" in output
    assert f"Aktive Datenbank: {config.get_database_path().name}" in output
    assert f"Lokale Benachrichtigungen: {config.ENABLE_LOCAL_NOTIFICATIONS}" in output
    assert "Empfohlene lokale Prüfkommandos (werden hier nicht ausgeführt):" in output
    assert "python -m pytest friday/tests" in output
    assert "python -m compileall friday" in output
    assert "python scripts\\friday_safety_smoke.py" in output
    assert "git diff --check" in output
    assert "Lokaler Modell-Diagnosemodus: Mock/Preview" in output
    assert "ENABLE_LOCAL_OLLAMA: False" in output
    assert "Ollama Modell gesetzt: False" in output
    assert "Ollama URL lokal erlaubt: True" in output
    assert "Ollama Live-Health-Check: nicht automatisch ausgeführt" in output
    assert "Externe Modellaufrufe: False" in output
    assert "Produktfluss angebunden: False" in output


def test_handle_menu_choice_messages_shows_intent(tmp_path, capsys) -> None:
    interface = _build_interface()
    interface.handle_menu_choice("2")
    output = capsys.readouterr().out

    assert "Eingehende Nachrichten" in output
    assert "Erkannte Absicht:" in output


def test_handle_menu_choice_help_overview(tmp_path, capsys) -> None:
    interface = _build_interface()
    assert interface.handle_menu_choice("8") is True
    output = capsys.readouterr().out

    assert "Hilfe / Übersicht" in output


def _write_import_apply_preview_cli_export(project_root: Path) -> Path:
    from friday.app.local_data_export_preview import (
        LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        build_local_data_export_preview,
    )
    from friday.app.local_data_export_writer import LocalDataExportPayload, write_local_data_export

    preview = build_local_data_export_preview(
        project_root=project_root,
        local_data_dir=project_root / "local_data",
        timestamp="20260707_235500",
    )
    result = write_local_data_export(
        preview=preview,
        approval_token=LOCAL_DATA_EXPORT_APPROVAL_TOKEN,
        scanner_smoke_passed=True,
        project_root=project_root,
        payload=LocalDataExportPayload(
            tasks=(
                {
                    "id": 1,
                    "title": "Apply CLI Preview Aufgabe",
                    "status": "open",
                },
            ),
            contact_contexts=(),
            review_suggestions=(),
            safety_status={
                "ENABLE_REAL_EMAIL": False,
                "ENABLE_REAL_WHATSAPP": False,
                "ENABLE_REAL_SMS": False,
                "ENABLE_REAL_CALENDAR": False,
                "ENABLE_REAL_WEATHER": False,
                "ENABLE_REAL_MUSIC": False,
                "REQUIRE_USER_APPROVAL": True,
                "USE_SQLITE_STORAGE": True,
            },
        ),
    )
    assert result.persisted is True
    assert result.target_path is not None
    return Path(result.target_path)


def test_backup_restore_menu_import_apply_preview_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    export_root = _write_import_apply_preview_cli_export(tmp_path)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    _set_inputs(monkeypatch, ["7", str(export_root), "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out
    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    assert "Import-Apply-Vorschau wurde read-only erstellt." in output
    assert "Es wurde nichts importiert." in output
    assert "Es wurde nichts geschrieben." in output
    assert "Import anwenden ist noch nicht freigegeben." in output
    assert "Es wurde kein Token abgefragt." in output
    assert "Status: blocked" in output
    assert "backup_required" in output
    assert before == after


def test_backup_restore_menu_import_apply_preview_z_returns_without_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    _set_inputs(monkeypatch, ["7", "z", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Import-Apply-Vorschau wurde read-only erstellt." not in output
    assert "IMPORT ANWENDEN" not in output


def test_backup_restore_menu_import_apply_write_blocks_without_backup(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    export_root = _write_import_apply_preview_cli_export(tmp_path)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    before_tasks = task_agent.get_open_tasks()
    _set_inputs(monkeypatch, ["8", str(export_root), "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Import nach Freigabe anwenden" in output
    assert "backup_required" in output
    assert "Import-Apply wurde blockiert. Es wurde kein Token abgefragt." in output
    assert "Tippe IMPORT ANWENDEN" not in output
    assert task_agent.get_open_tasks() == before_tasks


def test_backup_restore_menu_import_apply_write_rejects_wrong_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    export_root = _write_import_apply_preview_cli_export(tmp_path)
    (tmp_path / "local_data" / "backups" / "friday_backup_test").mkdir(parents=True)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr("friday.app.interface.run_safety_smoke", lambda: _SmokeResultStub(True))
    _set_inputs(monkeypatch, ["8", str(export_root), "JA", "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out

    assert "Safety Smoke: PASS" in output
    assert "Import-Apply wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert task_agent.get_open_tasks() == []


def test_backup_restore_menu_import_apply_write_applies_with_exact_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    export_root = _write_import_apply_preview_cli_export(tmp_path)
    (tmp_path / "local_data" / "backups" / "friday_backup_test").mkdir(parents=True)
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr("friday.app.interface.run_safety_smoke", lambda: _SmokeResultStub(True))
    _set_inputs(monkeypatch, ["8", str(export_root), LOCAL_DATA_IMPORT_APPLY_APPROVAL_TOKEN, "9"])

    interface.open_backup_restore_menu()
    output = capsys.readouterr().out
    tasks = task_agent.get_open_tasks()

    assert "Safety Smoke: PASS" in output
    assert "Import-Apply wurde lokal angewendet." in output
    assert "Erstellte Aufgaben: 1" in output
    assert any(task["title"] == "Apply CLI Preview Aufgabe" for task in tasks)


def test_handle_menu_choice_empty_or_whitespace_input_is_invalid(monkeypatch, capsys) -> None:
    interface = _build_interface()
    assert interface.handle_menu_choice("") is True
    assert interface.handle_menu_choice("   ") is True
    output = capsys.readouterr().out

    assert output.count("Ungültige Auswahl. Bitte erneut versuchen.") >= 2


def test_handle_menu_choice_contact_context_menu_returns(tmp_path, monkeypatch, capsys) -> None:
    interface, _repository = _build_interface_with_contact_repository(tmp_path)
    _set_inputs(monkeypatch, ["5"])

    assert interface.handle_menu_choice("9") is True
    output = capsys.readouterr().out

    assert "Kontakt-Kontext" in output


def test_run_can_open_contact_context_then_exit(tmp_path, monkeypatch, capsys) -> None:
    interface, _repository = _build_interface_with_contact_repository(tmp_path)
    _set_inputs(monkeypatch, ["9", "5", "7"])

    interface.run()
    output = capsys.readouterr().out

    assert "Kontakt-Kontext" in output
    assert "Friday wird beendet." in output


def test_contact_context_menu_shows_empty_state(tmp_path, monkeypatch, capsys) -> None:
    interface, _repository = _build_interface_with_contact_repository(tmp_path)
    _set_inputs(monkeypatch, ["1", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Lokale Kontakt-Kontexte" in output
    assert "Keine lokalen Kontakt-Kontexte vorhanden." in output


def test_contact_context_menu_search_finds_local_context(tmp_path, monkeypatch, capsys) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
        source_context="nachrichten_review",
    )
    _set_inputs(monkeypatch, ["2", "max", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Kontakt-Suche" in output
    assert "Max Mustermann" in output
    assert "Typ: kunde" in output


def test_contact_context_menu_show_lists_visible_local_fields(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    _set_inputs(monkeypatch, ["1", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Lokale Kontakt-Kontexte" in output
    assert "[contact-01] Max Mustermann" in output
    assert "Typ: kunde" in output
    assert "Spitzname: kein Spitzname" in output
    assert "Kontext: kein Kontext" in output


def test_contact_context_menu_search_without_match_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    before_contact = repository.get_contact_context("contact-01")
    _set_inputs(monkeypatch, ["2", "anna", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Kontakt-Suche" in output
    assert "Keine passenden Kontakt-Kontexte gefunden." in output
    assert repository.get_contact_context("contact-01") == before_contact


def test_contact_context_menu_edit_draft_preview_does_not_change_storage(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    _set_inputs(monkeypatch, ["3", "contact-01", "2", "", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Kontakt-Kontext Vorschau" in output
    assert "Name: Max Mustermann" in output
    assert "Kontaktart: kollege" in output
    assert "Speichern wurde abgebrochen." in output
    assert repository.get_contact_context("contact-01")["contact_type"] == "kunde"


def test_contact_context_menu_edit_draft_saves_only_with_hard_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    _set_inputs(monkeypatch, ["3", "contact-01", "2", "SPEICHERN", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out
    updated = repository.get_contact_context("contact-01")

    assert "Kontakt-Kontext wurde lokal gespeichert." in output
    assert updated["contact_type"] == "kollege"
    assert updated["user_approved_persistence"] == 1
    assert updated["sensitivity_checked"] == 1


def test_contact_context_menu_edit_draft_rejects_ja_save_confirmation(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    _set_inputs(monkeypatch, ["3", "contact-01", "2", "JA", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Speichern wurde abgebrochen." in output
    assert repository.get_contact_context("contact-01")["contact_type"] == "kunde"


def test_contact_context_menu_edit_draft_rejects_lowercase_ja_save_confirmation(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    _set_inputs(monkeypatch, ["3", "contact-01", "2", "ja", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Speichern wurde abgebrochen." in output
    assert repository.get_contact_context("contact-01")["contact_type"] == "kunde"


def test_contact_context_menu_edit_draft_invalid_input_keeps_storage(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    _set_inputs(monkeypatch, ["3", "contact-01", "JA", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    assert repository.get_contact_context("contact-01")["contact_type"] == "kunde"


def test_contact_context_menu_edit_draft_skip_keeps_storage(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(
        contact_id="contact-01",
        display_name="Max Mustermann",
        contact_type="kunde",
    )
    _set_inputs(monkeypatch, ["3", "contact-01", "8", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Kontakt-Bearbeitung wurde übersprungen." in output
    assert repository.get_contact_context("contact-01")["contact_type"] == "kunde"


def test_contact_context_menu_forget_wrong_confirmation_keeps_storage(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    (tmp_path / "local_data" / "backups" / "friday_backup_test").mkdir(parents=True)
    monkeypatch.setattr("friday.app.interface.run_safety_smoke", lambda: _SmokeResultStub(True))
    _set_inputs(monkeypatch, ["4", "contact-01", "JA", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Forget Person wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert repository.get_contact_context("contact-01") is not None


def test_contact_context_menu_forget_missing_backup_keeps_storage(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    _set_inputs(monkeypatch, ["4", "contact-01", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Forget Person wurde blockiert: Backup fehlt." in output
    assert repository.get_contact_context("contact-01") is not None


def test_contact_context_menu_forget_old_token_keeps_storage(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    (tmp_path / "local_data" / "backups" / "friday_backup_test").mkdir(parents=True)
    monkeypatch.setattr("friday.app.interface.run_safety_smoke", lambda: _SmokeResultStub(True))
    _set_inputs(monkeypatch, ["4", "contact-01", CONTACT_DB_CLEANUP_TOKEN, "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Forget Person wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert repository.get_contact_context("contact-01") is not None


def test_contact_context_menu_forget_hard_token_deletes_local_context(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, repository = _build_interface_with_contact_repository(tmp_path)
    repository.create_contact_context(contact_id="contact-01", display_name="Max Mustermann")
    (tmp_path / "local_data" / "backups" / "friday_backup_test").mkdir(parents=True)
    monkeypatch.setattr("friday.app.interface.run_safety_smoke", lambda: _SmokeResultStub(True))
    _set_inputs(monkeypatch, ["4", "contact-01", FORGET_PERSON_APPROVAL_TOKEN, "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Forget Person wurde lokal ausgefuehrt." in output
    assert "contact_contexts: 1" in output
    assert repository.get_contact_context("contact-01") is None


def test_contact_context_menu_forget_unknown_id_is_stable(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, _repository = _build_interface_with_contact_repository(tmp_path)
    _set_inputs(monkeypatch, ["4", "does-not-exist", "5"])

    interface.open_contact_context_menu()
    output = capsys.readouterr().out

    assert "Kontakt-Kontext wurde nicht gefunden." in output


def test_handle_menu_choice_calendar_preview(tmp_path, capsys) -> None:
    interface = _build_interface()
    interface.handle_menu_choice("3")
    output = capsys.readouterr().out

    assert "Kalender-Vorschläge" in output


def test_handle_menu_choice_morning_briefing(tmp_path, capsys) -> None:
    interface = _build_interface()
    interface.handle_menu_choice("4")
    output = capsys.readouterr().out

    assert "Morgenübersicht" in output
    assert "Wetter:" in output
    assert "Musik:" in output


def test_task_menu_invalid_input_returns_to_loop_then_back(monkeypatch, capsys) -> None:
    interface = _build_interface()
    choices = iter(["x", "12"])
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(choices))

    interface.open_task_management()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_task_menu_multiple_invalid_inputs_then_back(tmp_path, monkeypatch, capsys) -> None:
    interface = _build_interface()
    choices = iter(["x", "", "abc", "12"])
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(choices))

    interface.open_task_management()
    output = capsys.readouterr().out

    assert output.count("Ungültige Auswahl. Bitte erneut versuchen.") >= 3


def test_task_menu_quick_add_then_back(tmp_path, monkeypatch, capsys) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]

    quick_add_inputs = iter(["Quick Journey Aufgabe", "j"])
    monkeypatch.setattr("builtins.input", lambda _: next(quick_add_inputs))

    main_choices = iter(["1", "7"])
    task_choices = iter(["9", "12"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_choices))
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(task_choices))

    interface.run()
    output = capsys.readouterr().out

    assert "Aufgabe wurde schnell erstellt." in output
    assert "Friday wird beendet." in output
    tasks = task_agent.get_open_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Quick Journey Aufgabe"
    assert tasks[0]["priority"] == "normal"
    assert tasks[0]["status"] == "open"


def test_task_menu_markdown_export_then_back(tmp_path, monkeypatch, capsys) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task("Export Journey Aufgabe")
    interface = _build_interface_with_task_agent(task_agent)
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]

    main_choices = iter(["1", "7"])
    task_choices = iter(["10", "12"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_choices))
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(task_choices))

    interface.run()
    output = capsys.readouterr().out

    assert "Aufgaben wurden lokal exportiert:" in output
    path_line = next(
        line
        for line in output.splitlines()
        if "Aufgaben wurden lokal exportiert:" in line
    )
    exported_path_text = path_line.split("Aufgaben wurden lokal exportiert: ", 1)[1].strip()
    exported_path = Path(exported_path_text)
    if not exported_path.is_absolute():
        exported_path = tmp_path / exported_path
    assert exported_path.exists()
    assert "Friday wird beendet." in output


def test_task_delete_empty_id_does_not_delete(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Test Task")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )

    _set_inputs(monkeypatch, [""])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Ungültige Aufgaben-ID." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_task_delete_nonnumeric_id_does_not_delete(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Test Task")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )

    _set_inputs(monkeypatch, ["abc"])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Ungültige Aufgaben-ID." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_task_delete_nonexistent_id_prints_not_found(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    _ = agent.create_task("Test Task")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )

    _set_inputs(monkeypatch, ["9999"])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde nicht gefunden." in output


def test_task_delete_empty_confirmation_aborts(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Löschen abbrechen")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )

    _set_inputs(monkeypatch, [str(created["id"]), ""])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Löschen wurde abgebrochen." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_task_delete_lowercase_with_whitespace_confirmation_does_not_delete(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Nicht mit leerzeichen gelöscht")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )

    _set_inputs(monkeypatch, [str(created["id"]), " ja "])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Löschen wurde abgebrochen." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_task_delete_uppercase_with_whitespace_is_trimmed_by_current_implementation(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Mit Leerzeichen löschen")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )

    _set_inputs(monkeypatch, [str(created["id"]), " JA "])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde dauerhaft gelöscht." in output
    assert agent.get_task_by_id(created["id"]) is None


def test_task_delete_lowercase_ja_does_not_delete(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Nicht mit klein ja löschen")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )
    _set_inputs(monkeypatch, [str(created["id"]), "ja"])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Löschen wurde abgebrochen." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_task_delete_exact_ja_deletes(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Ja löscht diese Aufgabe")
    interface = FridayInterface(
        task_agent=agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=None,
        briefing_agent=_BriefingAgentStub(),
    )

    _set_inputs(monkeypatch, [str(created["id"]), "JA"])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde dauerhaft gelöscht." in output
    assert agent.get_task_by_id(created["id"]) is None


def test_run_processes_invalid_inputs_then_exits_cleanly(monkeypatch, capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]
    choices = iter(["x", "", "  ", "7"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(choices))

    interface.run()
    output = capsys.readouterr().out

    assert output.count("Ungültige Auswahl. Bitte erneut versuchen.") >= 3
    assert "Friday wird beendet." in output


def test_run_can_open_help_then_exit(monkeypatch, capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]
    choices = iter(["8", "7"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(choices))

    interface.run()
    output = capsys.readouterr().out

    assert "Hilfe / Übersicht" in output
    assert "Aufgabe schnell erfassen" in output
    assert "!hoch @morgen #taeglich" in output
    assert "Wiederkehrende Aufgaben" in output
    assert "Friday wird beendet." in output


def test_startup_notification_preview_is_silent_when_flag_disabled(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task("Heute fällig", due_date="2026-07-05")
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(config, "ENABLE_LOCAL_NOTIFICATIONS", False)
    monkeypatch.setattr("friday.app.notification_preview.resolve_today", lambda: "2026-07-05")

    interface._show_startup_notification_preview_if_enabled()
    output = capsys.readouterr().out

    assert "Lokale Benachrichtigung" not in output
    assert "Aufgaben heute fällig" not in output


def test_startup_notification_preview_shows_console_text_when_flag_enabled(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task("Heute fällig", due_date="2026-07-05")
    interface = _build_interface_with_task_agent(task_agent)
    monkeypatch.setattr(config, "ENABLE_LOCAL_NOTIFICATIONS", True)
    monkeypatch.setattr("friday.app.notification_preview.resolve_today", lambda: "2026-07-05")

    interface._show_startup_notification_preview_if_enabled()
    output = capsys.readouterr().out

    assert "Lokale Benachrichtigung" in output
    assert "1 Aufgaben heute fällig" in output


def test_run_can_open_help_multiple_times_then_exit(monkeypatch, capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]
    choices = iter(["8", "8", "7"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(choices))

    interface.run()
    output = capsys.readouterr().out

    assert output.count("Hilfe / Übersicht") >= 2
    assert "Friday wird beendet." in output


def test_run_invalid_input_then_help_then_exit(monkeypatch, capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]
    choices = iter(["x", "8", "7"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(choices))

    interface.run()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    assert "Hilfe / Übersicht" in output
    assert "Friday wird beendet." in output


def test_run_task_menu_back_then_help_then_exit(monkeypatch, capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]
    main_choices = iter(["1", "8", "7"])
    task_choices = iter(["12"])
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_choices))
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(task_choices))

    interface.run()
    output = capsys.readouterr().out

    assert "Hilfe / Übersicht" in output
    assert "Friday wird beendet." in output


def test_combined_review_no_suggestions_returns_cleanly(monkeypatch, capsys) -> None:
    interface = _build_review_interface_without_pending()
    _set_inputs(monkeypatch, [""])

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Keine offenen Vorschläge vorhanden." in output


def test_combined_review_refresh_then_exit(monkeypatch, capsys) -> None:
    interface = _build_review_interface()
    message_agent = interface.message_agent
    assert isinstance(message_agent, _ReviewableMessageAgentStub)

    _set_inputs(monkeypatch, ["3", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert output.count("Offene Nachrichten-Vorschläge:") >= 1
    assert output.count("Offene Aufgaben-Vorschläge:") >= 1
    assert any(item["id"] == 100 for item in message_agent.get_pending_suggestions())
    assert any(item["id"] == 200 for item in message_agent.get_pending_task_suggestions())


def test_review_pending_suggestions_invalid_area_then_exit_keeps_open(tmp_path, monkeypatch, capsys) -> None:
    interface = _build_review_interface()
    message_agent = interface.message_agent
    assert isinstance(message_agent, _ReviewableMessageAgentStub)

    initial_message_count = len(message_agent.get_pending_suggestions())
    initial_task_count = len(message_agent.get_pending_task_suggestions())

    _set_inputs(monkeypatch, ["x", "z"])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    assert len(message_agent.get_pending_suggestions()) == initial_message_count
    assert len(message_agent.get_pending_task_suggestions()) == initial_task_count


def test_run_exits_cleanly_from_main_menu(monkeypatch, capsys) -> None:
    interface = _build_interface()
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: "7")

    interface.run()
    output = capsys.readouterr().out

    assert "Friday wird beendet." in output


def test_full_local_task_journey_create_search_and_mark_done(tmp_path, monkeypatch, capsys) -> None:
    task_agent = _build_task_agent(tmp_path)
    interface = _build_interface_with_task_agent(task_agent)

    created_task_id: dict[str, int | None] = {"value": None}
    journey_inputs = iter(
        [
            "Journey Aufgabe",
            "arbeit",
            "2026-07-06",
            "Journey Test",
            "high",
            "",
            "Journey",
            "",
            "",
            "",
        ]
    )

    def _journey_input(prompt: str = "") -> str:
        try:
            return next(journey_inputs)
        except StopIteration:
            if "ID der Aufgabe" in prompt:
                if created_task_id["value"] is None:
                    open_tasks = task_agent.get_open_tasks()
                    if open_tasks:
                        created_task_id["value"] = open_tasks[0]["id"]
                return str(created_task_id["value"] or "")
            return ""

    main_choices = iter(["1", "7"])
    task_choices = iter(["2", "5", "4", "12"])

    monkeypatch.setattr("builtins.input", _journey_input)
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_choices))
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(task_choices))

    interface.run()
    output = capsys.readouterr().out

    assert "Aufgabe wurde erstellt." in output
    assert "Journey Aufgabe" in output
    assert "Aufgabe wurde als erledigt markiert." in output
    assert "Friday wird beendet." in output
    assert created_task_id["value"] is not None

    journey_task = task_agent.get_task_by_id(int(created_task_id["value"]))
    assert journey_task is not None
    assert journey_task["status"] == "done"
    assert all(task["id"] != journey_task["id"] for task in task_agent.get_open_tasks())


def test_task_menu_local_day_planning_preview_then_back(tmp_path, monkeypatch, capsys) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task(
        "Tagesplan Aufgabe",
        due_date="2026-07-05",
        priority="high",
    )
    interface = _build_interface_with_task_agent(task_agent)

    task_choices = iter(["11", "12"])
    monkeypatch.setattr("friday.app.interface.resolve_today", lambda: "2026-07-05")
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(task_choices))

    interface.open_task_management()
    output = capsys.readouterr().out

    assert "Lokale Tagesplanung fuer 2026-07-05" in output
    assert "1. Tagesplan Aufgabe" in output
    assert "Prioritaet: high" in output
    assert "nur eine lokale Vorschau" in output
    stored = task_agent.get_open_tasks()
    assert len(stored) == 1
    assert stored[0]["title"] == "Tagesplan Aufgabe"
    assert stored[0]["status"] == "open"


def test_run_can_open_day_planning_preview_then_exit(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    task_agent = _build_task_agent(tmp_path)
    task_agent.create_task(
        "Run Tagesplan Aufgabe",
        due_date="2026-07-05",
        priority="urgent",
    )
    interface = _build_interface_with_task_agent(task_agent)
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]

    main_choices = iter(["1", "7"])
    task_choices = iter(["11", "12"])
    monkeypatch.setattr("friday.app.interface.resolve_today", lambda: "2026-07-05")
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_choices))
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(task_choices))

    interface.run()
    output = capsys.readouterr().out

    assert "Lokale Tagesplanung fuer 2026-07-05" in output
    assert "1. Run Tagesplan Aufgabe" in output
    assert "Prioritaet: urgent" in output
    assert "nur eine lokale Vorschau" in output
    assert "Friday wird beendet." in output
    stored = task_agent.get_open_tasks()
    assert len(stored) == 1
    assert stored[0]["title"] == "Run Tagesplan Aufgabe"
    assert stored[0]["status"] == "open"
