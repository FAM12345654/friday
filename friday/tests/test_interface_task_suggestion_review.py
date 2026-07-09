"""Tests for local task suggestion review flow in the terminal interface."""

from __future__ import annotations

from typing import Any, Dict

from friday.agents.calendar_agent import CalendarAgent
from friday.agents.message_agent import MessageAgent
from friday.agents.task_agent import TaskAgent
from friday.app.interface import FridayInterface
from friday.storage.database import get_connection
from friday.storage.database import setup_local_database


class _ApprovalAgentFailing:
    def request_approval(self, action: str, message: str | None = None, context: Dict[str, Any] | None = None) -> str:
        raise AssertionError("No external approval flow may be used here.")


class _BriefingAgentStub:
    def build_preview(self):
        return {
            "date": "2026-07-05",
            "tasks": [],
            "calendar_items": [],
            "weather": "Demo",
            "music": "Demo",
        }


def _build_interface(tmp_path):
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    task_agent = TaskAgent(db_path=db_file)
    message_agent = MessageAgent(db_path=db_file)
    calendar_agent = CalendarAgent(db_path=db_file)
    interface = FridayInterface(
        task_agent=task_agent,
        message_agent=message_agent,
        calendar_agent=calendar_agent,
        approval_agent=_ApprovalAgentFailing(),
        briefing_agent=_BriefingAgentStub(),
    )
    return interface, message_agent, task_agent


def _insert_task_message(db_file, message_id: int, sender: str, text: str) -> None:
    with get_connection(db_file) as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO messages (id, sender, text, received_at, contact_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, sender, text, "2026-07-05T12:00:00", "other"),
        )
        connection.execute(
            """
            INSERT INTO contacts (name, contact_type, notes, betreuer)
            VALUES (?, ?, ?, ?)
            """,
            (sender, "kunde", "Testkunde fuer Task-Suggestion-Review.", "philip"),
        )


def _set_inputs(monkeypatch, values: list[str]) -> None:
    iterator = iter(values)

    def _next_input(_: str = "") -> str:
        return next(iterator)

    monkeypatch.setattr("builtins.input", _next_input)


def _prepare_message_agent_for_task_only(monkeypatch, message_agent: MessageAgent) -> None:
    monkeypatch.setattr(message_agent, "generate_local_suggestions", lambda: None)
    monkeypatch.setattr(message_agent, "get_pending_suggestions", lambda: [])


def test_review_pending_task_suggestions_creates_local_task(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 10, "Chef", "Kannst du bitte den Report fertig machen?")
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]
    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "a", ""])

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt." in output
    assert any(task["title"] == suggestion["title"] for task in task_agent.get_open_tasks())
    pending = message_agent.get_pending_task_suggestions()
    assert all(item["id"] != suggestion["id"] for item in pending)


def test_review_pending_task_suggestion_rejects(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 11, "Chef", "Bitte bitte das Dokument prüfen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]
    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "r", ""])

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Aufgaben-Vorschlag wurde abgelehnt." in output
    remaining = message_agent.get_pending_task_suggestions()
    assert all(item["id"] != suggestion["id"] for item in remaining)


def test_review_pending_task_suggestion_edit_keeps_open(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 12, "Chef", "Bitte bitte den Kalender eintragen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]
    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "e", "Neue Aufgabe", "", "", "", "", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Aufgaben-Vorschlag wurde lokal bearbeitet." in output
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] and item["title"] == "Neue Aufgabe" for item in pending)


def test_review_pending_task_suggestion_edit_empty_title_shows_error(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 13, "Chef", "Bitte bitte einen Termin bestätigen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]
    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "e", "", "", "", "", "", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ein Aufgaben-Vorschlag braucht einen Titel." in output
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)


def test_review_pending_task_suggestion_keep_open_with_s(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 14, "Chef", "Bitte bitte die Aufgabe planen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]
    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "s", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Aufgaben-Vorschlag bleibt offen." in output
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)


def test_review_pending_task_suggestion_does_not_call_external_services(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 15, "Chef", "Bitte bitte die Daten prüfen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]
    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "a", ""])

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt." in output
    assert "wird keine externe" not in output.lower()


def test_task_review_invalid_task_suggestion_id_prints_specific_message(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 16, "Chef", "Bitte bitte den Report prüfen.")
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]

    before_tasks = task_agent.get_open_tasks()
    _set_inputs(monkeypatch, ["2", "abc", "", ""])

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Aufgaben-Vorschlags-ID." in output
    assert task_agent.get_open_tasks() == before_tasks
    assert any(item["id"] == suggestion["id"] for item in message_agent.get_pending_task_suggestions())


def test_review_pending_task_suggestion_unknown_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 17, "Chef", "Bitte bitte das Protokoll prüfen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "x", "z", ""])

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)


def test_review_pending_task_suggestion_whitespace_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 19, "Chef", "Kannst du bitte den Report fertig machen?")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "   ", "", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)


def test_review_pending_task_suggestion_special_character_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 20, "Chef", "Bitte bitte die Agenda prüfen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "^^", "", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)


def test_review_pending_task_suggestion_multiple_invalid_actions_then_return(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 21, "Chef", "Bitte bitte den Report fertig machen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]
    before_tasks = list(_task_agent.get_open_tasks())

    _set_inputs(
        monkeypatch,
        [
            "2",
            str(suggestion["id"]),
            "x",
            "2",
            str(suggestion["id"]),
            "§§",
            "2",
            str(suggestion["id"]),
            "   ",
            "z",
            "",
        ],
    )
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert output.count("Ungültige Auswahl. Bitte erneut versuchen.") >= 2
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)
    assert "Offene Aufgaben-Vorschläge:" in output
    assert _task_agent.get_open_tasks() == before_tasks


def test_review_pending_task_suggestion_empty_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    _insert_task_message(db_file, 18, "Chef", "Bitte bitte die Präsentation prüfen.")
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _prepare_message_agent_for_task_only(monkeypatch, message_agent)
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "", "z", ""])

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)
