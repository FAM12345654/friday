"""Tests for local task input flows in the Friday terminal interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from friday.agents.task_agent import TaskAgent
from friday.app.interface import FridayInterface
from friday.storage.database import initialize_database


class _MessageAgentStub:
    def get_messages(self):
        return []


class _CalendarAgentStub:
    def get_free_slots_today(self, duration_minutes: int = 60):
        return []

    def get_items_for_date(self, date_iso: str):
        return []


class _ApprovalAgentStub:
    def request_approval(self, action: str, message: str | None = None, context: Dict[str, Any] | None = None) -> str:
        return "abgelehnt"


class _BriefingAgentStub:
    def build_preview(self):
        return {
            "date": "2026-07-05",
            "tasks": [],
            "calendar_items": [],
            "weather": "Demo",
            "music": "Demo",
        }


def _build_task_agent(tmp_path):
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    return TaskAgent(db_path=db_path)


def _build_interface(task_agent: TaskAgent) -> FridayInterface:
    return FridayInterface(
        task_agent=task_agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=_ApprovalAgentStub(),
        briefing_agent=_BriefingAgentStub(),
    )


def _set_inputs(monkeypatch, values: list[str]) -> None:
    iterator = iter(values)

    def _next_input(_: str = "") -> str:
        return next(iterator)

    monkeypatch.setattr("builtins.input", _next_input)


def test_create_task_from_input_creates_local_task(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    _set_inputs(
        monkeypatch,
        ["Neue lokale Aufgabe", "arbeit", "2026-07-05", "Testnotiz", "high", ""],
    )

    interface._create_task_from_input()
    tasks = agent.get_open_tasks()
    output = capsys.readouterr().out

    assert len(tasks) == 1
    assert tasks[0]["title"] == "Neue lokale Aufgabe"
    assert tasks[0]["category"] == "arbeit"
    assert tasks[0]["due_date"] == "2026-07-05"
    assert tasks[0]["notes"] == "Testnotiz"
    assert tasks[0]["priority"] == "high"
    assert "Aufgabe wurde erstellt." in output


def test_create_task_from_input_rejects_invalid_priority(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    _set_inputs(monkeypatch, ["Neue Aufgabe", "arbeit", "2026-07-05", "Test", "zu hoch", ""])

    interface._create_task_from_input()
    output = capsys.readouterr().out

    assert "Ungültige Priorität." in output
    assert agent.get_open_tasks() == []


def test_create_task_from_input_rejects_empty_title(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    _set_inputs(monkeypatch, [""])

    interface._create_task_from_input()
    output = capsys.readouterr().out

    assert "Eine Aufgabe braucht mindestens einen Titel." in output
    assert agent.get_open_tasks() == []


def test_quick_add_task_from_input_creates_local_task_with_defaults(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    _set_inputs(monkeypatch, ["Schnelle lokale Aufgabe", "j"])

    interface._quick_add_task_from_input()
    tasks = agent.get_open_tasks()
    output = capsys.readouterr().out

    assert len(tasks) == 1
    created = tasks[0]
    assert created["title"] == "Schnelle lokale Aufgabe"
    assert created["category"] == "sonstiges"
    assert created["priority"] == "normal"
    assert created["status"] == "open"
    assert created["due_date"] in (None, "")
    assert created["notes"] in (None, "")
    assert "Aufgabe wurde schnell erstellt." in output


def test_quick_add_task_from_input_rejects_empty_title(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    _set_inputs(monkeypatch, [""])

    interface._quick_add_task_from_input()
    output = capsys.readouterr().out

    assert "Eine Aufgabe braucht mindestens einen Titel." in output
    assert agent.get_open_tasks() == []


def test_quick_add_task_from_input_creates_task_from_structured_line(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    monkeypatch.setattr("friday.app.quick_add_parser.resolve_today", lambda: "2026-07-05")
    _set_inputs(monkeypatch, ["Zahnarzt anrufen !hoch @morgen", "j"])

    interface._quick_add_task_from_input()
    created = agent.get_open_tasks()[0]
    output = capsys.readouterr().out

    assert "Quick-Add Vorschau" in output
    assert created["title"] == "Zahnarzt anrufen"
    assert created["priority"] == "high"
    assert created["due_date"] == "2026-07-06"


def test_quick_add_task_from_input_can_be_cancelled(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    _set_inputs(monkeypatch, ["Bericht fertig !mittel @2026-07-15", "n"])

    interface._quick_add_task_from_input()
    output = capsys.readouterr().out

    assert "Schnellerfassung wurde abgebrochen." in output
    assert agent.get_open_tasks() == []


def test_edit_task_from_input_keeps_old_values_on_empty_input(tmp_path, monkeypatch) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task(
        title="Alt",
        category="arbeit",
        due_date="2026-07-05",
        notes="Altnotiz",
        priority="high",
    )
    interface = _build_interface(agent)
    _set_inputs(
        monkeypatch,
        [str(created["id"]), "", "", "", "", "", ""],
    )

    interface._edit_task_from_input()
    updated = agent.get_task_by_id(created["id"])

    assert updated is not None
    assert updated["title"] == "Alt"
    assert updated["category"] == "arbeit"
    assert updated["due_date"] == "2026-07-05"
    assert updated["notes"] == "Altnotiz"
    assert updated["priority"] == "high"


def test_edit_task_from_input_changes_provided_values(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task(
        title="Alt",
        category="arbeit",
        due_date="2026-07-05",
        notes="Altnotiz",
        priority="low",
    )
    interface = _build_interface(agent)
    _set_inputs(
        monkeypatch,
        [str(created["id"]), "Geänderter Titel", "privat", "2026-07-06", "Neue Notiz", "urgent", ""],
    )

    interface._edit_task_from_input()
    updated = agent.get_task_by_id(created["id"])
    output = capsys.readouterr().out

    assert updated is not None
    assert updated["title"] == "Geänderter Titel"
    assert updated["category"] == "privat"
    assert updated["due_date"] == "2026-07-06"
    assert updated["notes"] == "Neue Notiz"
    assert updated["priority"] == "urgent"
    assert "Aufgabe wurde aktualisiert." in output


def test_edit_task_from_input_rejects_invalid_priority(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Alt", priority="normal")
    interface = _build_interface(agent)
    _set_inputs(
        monkeypatch,
        [str(created["id"]), "", "", "", "", "zu hoch", ""],
    )

    interface._edit_task_from_input()
    output = capsys.readouterr().out

    assert "Ungültige Priorität." in output
    assert agent.get_task_by_id(created["id"])["priority"] == "normal"


def test_edit_task_from_input_invalid_id_does_not_change_any_task(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task(
        title="Bleibt",
        category="arbeit",
        due_date="2026-07-05",
        notes="Bestand",
        priority="normal",
    )
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["abc"])
    interface._edit_task_from_input()
    output = capsys.readouterr().out

    assert "Ungültige Aufgaben-ID." in output
    unchanged = agent.get_task_by_id(created["id"])
    assert unchanged is not None
    assert unchanged["title"] == "Bleibt"


def test_edit_task_from_input_unknown_id_prints_not_found(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Bestehende Aufgabe")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["99999"])
    interface._edit_task_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde nicht gefunden." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_mark_task_done_from_input_marks_task_done(tmp_path, monkeypatch) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task(
        title="Erledigen",
        category="arbeit",
    )
    interface = _build_interface(agent)
    _set_inputs(monkeypatch, [str(created["id"])])

    interface._mark_task_done_from_input()
    marked = agent.get_task_by_id(created["id"])

    assert marked is not None
    assert marked["status"] == "done"
    assert all(task["id"] != created["id"] for task in agent.get_open_tasks())


def test_mark_task_done_from_input_unknown_id_prints_not_found(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["99999"])
    interface._mark_task_done_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde nicht gefunden." in output


def test_mark_task_done_from_input_repeated_keeps_done_status(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Erneut erledigen")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, [str(created["id"])])
    interface._mark_task_done_from_input()
    _set_inputs(monkeypatch, [str(created["id"])])
    interface._mark_task_done_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde als erledigt markiert." in output
    marked = agent.get_task_by_id(created["id"])
    assert marked is not None
    assert marked["status"] == "done"


def test_mark_task_done_from_input_invalid_id(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)
    _set_inputs(monkeypatch, ["abc"])

    interface._mark_task_done_from_input()
    output = capsys.readouterr().out

    assert "Ungültige Aufgaben-ID." in output


def test_search_or_filter_tasks_from_input_searches_by_text(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    agent.create_task("Rechnung prüfen", category="arbeit", due_date="2026-07-05")
    agent.create_task("Einkauf", category="privat", due_date="2026-07-06")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["rechnung", "", "", ""])
    interface._search_or_filter_tasks_from_input()
    output = capsys.readouterr().out

    assert "Rechnung prüfen" in output
    assert "Einkauf" not in output


def test_search_or_filter_tasks_from_input_empty_query_shows_filtered_results(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    agent.create_task("Arbeit", category="arbeit", due_date="2026-07-05")
    agent.create_task("Privat", category="privat", due_date="2026-07-06")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["", "", "", ""])
    interface._search_or_filter_tasks_from_input()
    output = capsys.readouterr().out

    assert "Arbeit" in output
    assert "Privat" in output


def test_search_or_filter_tasks_from_input_no_match_prints_empty_message(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    agent.create_task("Arbeit", category="arbeit")
    agent.create_task("Privat", category="privat")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["nicht vorhanden", "", "", ""])
    interface._search_or_filter_tasks_from_input()
    output = capsys.readouterr().out

    assert "Keine passenden Aufgaben gefunden." in output


def test_delete_task_from_input_rejects_lowercase_ja(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Nicht mit klein ja löschen")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, [str(created["id"]), "ja"])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Löschen wurde abgebrochen." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_search_or_filter_tasks_from_input_filters_when_query_empty(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    agent.create_task("Arbeit", category="arbeit", due_date="2026-07-05")
    agent.create_task("Privat", category="privat", due_date="2026-07-06")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["", "open", "arbeit", "2026-07-05"])
    interface._search_or_filter_tasks_from_input()
    output = capsys.readouterr().out

    assert "Arbeit" in output
    assert "Privat" not in output


def test_archive_task_from_input_archives_task(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Zu archivieren")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, [str(created["id"])])
    interface._archive_task_from_input()
    output = capsys.readouterr().out

    updated = agent.get_task_by_id(created["id"])
    assert updated is not None
    assert updated["status"] == "archived"
    assert "Aufgabe wurde archiviert." in output


def test_archive_task_from_input_invalid_id(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["abc"])
    interface._archive_task_from_input()
    output = capsys.readouterr().out

    assert "Ungültige Aufgaben-ID." in output


def test_archive_task_from_input_missing_id_prints_not_found(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, ["99999"])
    interface._archive_task_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde nicht gefunden." in output


def test_archive_task_from_input_repeated_mark_stays_archived(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Archiv-Mehrfach")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, [str(created["id"])])
    interface._archive_task_from_input()
    _set_inputs(monkeypatch, [str(created["id"])])
    interface._archive_task_from_input()
    output = capsys.readouterr().out

    assert output.count("Aufgabe wurde archiviert.") >= 1
    updated = agent.get_task_by_id(created["id"])
    assert updated is not None
    assert updated["status"] == "archived"

def test_delete_task_from_input_requires_confirmation(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Nicht löschen")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, [str(created["id"]), "NEIN"])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Löschen wurde abgebrochen." in output
    assert agent.get_task_by_id(created["id"]) is not None


def test_delete_task_from_input_deletes_after_exact_ja(tmp_path, monkeypatch, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    created = agent.create_task("Löschen bestätigen")
    interface = _build_interface(agent)

    _set_inputs(monkeypatch, [str(created["id"]), "JA"])
    interface._delete_task_from_input()
    output = capsys.readouterr().out

    assert "Aufgabe wurde dauerhaft gelöscht." in output
    assert agent.get_task_by_id(created["id"]) is None


def test_export_tasks_to_markdown_from_task_interface_writes_file(tmp_path, capsys) -> None:
    agent = _build_task_agent(tmp_path)
    agent.create_task("Offene Aufgabe")
    done_task = agent.create_task("Erledigte Aufgabe")
    agent.mark_task_done(done_task["id"])
    archived_task = agent.create_task("Archivierte Aufgabe")
    agent.archive_task(archived_task["id"])
    interface = _build_interface(agent)

    interface._export_tasks_to_markdown()
    output = capsys.readouterr().out

    assert "Aufgaben wurden lokal exportiert:" in output
    prefix = "Aufgaben wurden lokal exportiert: "
    output_path_text = output.split(prefix, 1)[1].strip().splitlines()[0]
    output_path = Path(output_path_text)
    if not output_path.is_absolute():
        output_path = tmp_path / output_path

    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "## Offene Aufgaben" in content
    assert "## Erledigte Aufgaben" in content
    assert "## Archivierte Aufgaben" in content
    assert "Offene Aufgabe" in content
    assert "Erledigte Aufgabe" in content
    assert "Archivierte Aufgabe" in content
