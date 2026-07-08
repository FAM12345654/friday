"""Tests for local message suggestion review flow in the terminal interface."""

from __future__ import annotations

from typing import Any, Dict, List

from friday.app.interface import FridayInterface
from friday.agents.calendar_agent import CalendarAgent
from friday.agents.message_agent import MessageAgent
from friday.storage.database import setup_local_database


class _NoSuggestionMessageAgent:
    def generate_local_suggestions(self) -> List[Dict[str, Any]]:
        return []

    def get_pending_suggestions(self) -> List[Dict[str, Any]]:
        return []

    def get_messages(self) -> List[Dict[str, Any]]:
        return []


class _TaskAgentStub:
    def get_open_tasks(self):
        return []

    def detect_priority_hint(self, task: Dict[str, Any]) -> str:
        return "normal"

    def get_task_by_id(self, task_id: int):
        return None


class _CalendarAgentStub:
    def get_free_slots_today(self, duration_minutes: int = 60):
        return []

    def get_calendar_suggestions_for_message(self, message_id: int):
        return []

    def get_calendar_suggestion_by_id(self, suggestion_id: int):
        return None

    def select_calendar_suggestion(self, suggestion_id: int):
        return None


class _NoSlotCalendarAgent(_CalendarAgentStub):
    def get_calendar_suggestions_for_message(self, message_id: int):
        return []

    def generate_calendar_suggestions_for_message(self, message_id: int, date_iso: str | None = None, duration_minutes: int = 60):
        return []


class _MessageAgentForWrongMessageFlow:
    def __init__(self, suggestions: list[dict], messages: list[dict]) -> None:
        self._suggestions = suggestions
        self._messages = messages

    def generate_local_suggestions(self) -> list[dict]:
        return self._suggestions

    def get_pending_suggestions(self) -> list[dict]:
        return self._suggestions

    def get_messages(self) -> list[dict]:
        return self._messages

    def edit_suggestion(self, suggestion_id: int, draft_text: str):
        for item in self._suggestions:
            if item["id"] == suggestion_id:
                item["draft_text"] = draft_text
                item["status"] = "edited"
                return item
        return None


class _ApprovalAgentFailing:
    def request_approval(
        self, action: str, message: str | None = None, context: Dict[str, Any] | None = None
    ) -> str:
        raise AssertionError("No approval flow should run during review.")


def _build_interface(tmp_path):
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    message_agent = MessageAgent(db_path=db_file)
    return _build_interface_with_agents(db_file=db_file, message_agent=message_agent)


def _build_interface_with_agents(
    db_file,
    message_agent: Any | None = None,
    calendar_agent: Any | None = None,
):
    if message_agent is None:
        message_agent = MessageAgent(db_path=db_file)
    if calendar_agent is None:
        calendar_agent = CalendarAgent(db_path=db_file)
    return (
        FridayInterface(
            task_agent=_TaskAgentStub(),
            message_agent=message_agent,
            calendar_agent=calendar_agent,
            approval_agent=_ApprovalAgentFailing(),
        ),
        message_agent,
    )


def test_review_pending_suggestions_prints_no_pending_message(capsys) -> None:
    interface = FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_NoSuggestionMessageAgent(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=_ApprovalAgentFailing(),
    )
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Keine offenen Vorschläge vorhanden." in output


def test_review_pending_suggestions_approves_suggestion(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "a", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet." in output


def test_review_pending_suggestions_rejects_suggestion(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "r", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Vorschlag wurde abgelehnt." in output


def test_review_pending_suggestions_edits_suggestion(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "e", "Neue Antwort", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Vorschlag wurde lokal bearbeitet." in output


def test_review_pending_suggestions_handles_invalid_id(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    _ = message_agent.generate_local_suggestions()

    values = iter(["1", "abc", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Ungültige Vorschlags-ID." in output


def test_review_pending_suggestions_requires_edit_text(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "e", "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Ein Vorschlag braucht Text." in output


def test_review_pending_suggestions_can_approve_edited_suggestion(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    message_agent.edit_suggestion(suggestion["id"], "Neu formuliert")

    values = iter(["1", str(suggestion["id"]), "a", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet." in output


def test_review_pending_suggestions_can_attach_calendar_slot(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    calendar_suggestions = interface.calendar_agent.get_calendar_suggestions_for_message(
        message_id=int(suggestion["message_id"])
    )
    if not calendar_suggestions:
        calendar_suggestions = interface.calendar_agent.generate_calendar_suggestions_for_message(
            message_id=int(suggestion["message_id"])
        )
    slot_id = calendar_suggestions[0]["id"]

    values = iter(["1", str(suggestion["id"]), "k", str(slot_id), "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Kalender-Slot wurde lokal mit dem Vorschlag verbunden. Es wurde kein echter Termin erstellt." in output
    updated = message_agent.get_pending_suggestions()
    assert any(
        item["id"] == suggestion["id"] and "Möglicher Termin:" in item["draft_text"]
        for item in updated
    )


def test_review_pending_suggestions_invalid_calendar_slot_id(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    interface.calendar_agent.generate_calendar_suggestions_for_message(message_id=int(suggestion["message_id"]))

    values = iter(["1", str(suggestion["id"]), "k", "abc", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Ungültige Kalender-Slot-ID." in output


def test_review_pending_suggestions_selected_slot_remains_editable(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    suggestion_slots = interface.calendar_agent.generate_calendar_suggestions_for_message(
        message_id=int(suggestion["message_id"])
    )
    slot_id = suggestion_slots[0]["id"]

    values = iter(["1", str(suggestion["id"]), "k", str(slot_id), "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Kalender-Slot wurde lokal mit dem Vorschlag verbunden." in output

    pending = message_agent.get_pending_suggestions()
    selected = next(item for item in pending if item["id"] == suggestion["id"])
    assert selected["status"] == "edited"


def test_review_pending_suggestions_can_approve_after_slot_selection(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    calendar_slots = interface.calendar_agent.generate_calendar_suggestions_for_message(
        message_id=int(suggestion["message_id"])
    )
    slot_id = calendar_slots[0]["id"]

    values_for_selection = iter(["1", str(suggestion["id"]), "k", str(slot_id), "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values_for_selection))
    interface.review_pending_suggestions()

    values_for_approval = iter(["1", str(suggestion["id"]), "a", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values_for_approval))
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert output.count("Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet.") == 1


def test_calendar_slot_selection_replaces_existing_slot_line(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    slots = interface.calendar_agent.generate_calendar_suggestions_for_message(
        message_id=int(suggestion["message_id"])
    )
    assert slots

    first = slots[0]
    second = slots[1]

    values = iter(["1", str(suggestion["id"]), "k", str(first["id"]), "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))
    interface.review_pending_suggestions()
    values = iter(["1", str(suggestion["id"]), "k", str(second["id"]), "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))
    interface.review_pending_suggestions()

    output = capsys.readouterr().out
    updated = message_agent.get_pending_suggestions()
    selected = next(item for item in updated if item["id"] == suggestion["id"])
    term_lines = [line for line in str(selected["draft_text"]).splitlines() if line.startswith("Möglicher Termin:")]
    assert len(term_lines) == 1
    assert "Möglicher Termin: 2026-07-05 von 10:00 bis 11:00." not in "\n".join(term_lines)
    assert interface._format_calendar_slot_text(second) in "\n".join(term_lines)


def test_calendar_slot_selection_rejects_wrong_message_slot(tmp_path, monkeypatch, capsys) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    calendar_agent = CalendarAgent(db_path=db_file)
    slots_message_one = calendar_agent.generate_calendar_suggestions_for_message(message_id=1)
    slots_message_two = calendar_agent.generate_calendar_suggestions_for_message(message_id=2)

    message_agent = _MessageAgentForWrongMessageFlow(
        suggestions=[
            {"id": 10, "message_id": 1, "draft_text": "Erst", "status": "pending", "suggestion_type": "reply"},
            {"id": 11, "message_id": 2, "draft_text": "Zweit", "status": "pending", "suggestion_type": "reply"},
        ],
        messages=[
            {"id": 1, "sender": "Erste Person", "text": "Termin bitte", "received_at": "2026-07-05T08:00:00"},
            {"id": 2, "sender": "Zweite Person", "text": "Termin bitte", "received_at": "2026-07-05T09:00:00"},
        ],
    )
    interface, _ = _build_interface_with_agents(db_file=db_file, message_agent=message_agent, calendar_agent=calendar_agent)

    values = iter(["1", "10", "k", str(slots_message_two[0]["id"]), "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Kalender-Slot gehört nicht zu diesem Vorschlag." in output


def test_calendar_slot_selection_missing_slot(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    slots = interface.calendar_agent.generate_calendar_suggestions_for_message(
        message_id=int(suggestion["message_id"])
    )
    assert slots

    values = iter(["1", str(suggestion["id"]), "k", "99999", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))
    interface.review_pending_suggestions()

    output = capsys.readouterr().out
    assert "Kalender-Slot wurde nicht gefunden." in output


def test_calendar_slot_selection_no_slots_available(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    interface.calendar_agent = _NoSlotCalendarAgent()

    values = iter(["1", str(suggestion["id"]), "k", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))
    interface.review_pending_suggestions()

    output = capsys.readouterr().out
    assert "Keine Kalender-Slots verfügbar." in output


def test_review_loop_can_approve_two_suggestions_in_one_session(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    first = message_agent.generate_local_suggestions()[0]
    second = message_agent.suggestion_repository.create_suggestion(
        message_id=2,
        draft_text="Bitte prüfen Sie den Termin.",
    )
    assert second is not None

    values = iter(["1", str(first["id"]), "a", "1", str(second["id"]), "a", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert output.count("Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet.") == 2
    updated_first = message_agent.suggestion_repository.get_suggestion_by_id(first["id"])
    updated_second = message_agent.suggestion_repository.get_suggestion_by_id(second["id"])
    assert updated_first["status"] == "approved"
    assert updated_second["status"] == "approved"


def test_review_loop_returns_on_empty_input(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]
    initial = next(iter(message_agent.get_pending_suggestions()), None)
    assert initial is not None

    values = iter(["", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    after = message_agent.get_pending_suggestions()

    assert "Reviewbare Vorschläge" not in output
    assert "Offene Nachrichten-Vorschläge:" in output
    assert "Offene Aufgaben-Vorschläge:" in output
    assert len(after) == 1
    assert after[0]["id"] == initial["id"]


def test_review_loop_continues_after_invalid_suggestion_id(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    _ = message_agent.generate_local_suggestions()[0]

    values = iter(["1", "abc", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Vorschlags-ID." in output


def test_review_loop_continues_after_unknown_suggestion_id(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    _ = message_agent.generate_local_suggestions()[0]

    values = iter(["1", "99999", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Vorschlag wurde nicht gefunden." in output


def test_review_pending_suggestions_unknown_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "x", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    pending = message_agent.get_pending_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)
    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_review_pending_suggestions_whitespace_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "   ", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    pending = message_agent.get_pending_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)
    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_review_pending_suggestions_special_character_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "##", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    pending = message_agent.get_pending_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)
    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_review_pending_suggestions_multiple_invalid_actions_then_return(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(
        [
            "1",
            str(suggestion["id"]),
            "x",
            "1",
            str(suggestion["id"]),
            "###",
            "1",
            str(suggestion["id"]),
            "   ",
            "z",
            "",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    pending = message_agent.get_pending_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)
    assert output.count("Ungültige Auswahl. Bitte erneut versuchen.") >= 2
    assert "Offene Nachrichten-Vorschläge:" in output


def test_review_pending_suggestions_empty_action_stays_open(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    pending = message_agent.get_pending_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)
    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_show_messages_with_suggestions_displays_intent(tmp_path, capsys) -> None:
    interface, _ = _build_interface(tmp_path)

    interface._show_messages_with_suggestions()
    output = capsys.readouterr().out

    assert "Erkannte Absicht:" in output
    assert output.count("Erkannte Absicht:") == 3


def test_review_loop_later_keeps_suggestion_open(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent = _build_interface(tmp_path)
    suggestion = message_agent.generate_local_suggestions()[0]

    values = iter(["1", str(suggestion["id"]), "s", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(values))

    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    pending = message_agent.get_pending_suggestions()

    assert "Vorschlag bleibt offen." in output
    assert any(item["id"] == suggestion["id"] for item in pending)
