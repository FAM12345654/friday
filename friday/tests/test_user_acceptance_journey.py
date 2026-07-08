"""End-to-end user acceptance journey for Friday 1.0 local CLI."""

from __future__ import annotations

from typing import Any

from friday.agents.task_agent import TaskAgent
from friday.app.interface import FridayInterface
from friday.storage.database import initialize_database


class _MessageAgentStub:
    def get_messages(self) -> list[dict[str, Any]]:
        return [
            {
                "id": 1,
                "sender": "Max",
                "text": "Kannst du mir kurz antworten?",
                "received_at": "2026-07-05T08:00:00",
            }
        ]

    def detect_intent(self, text: str) -> str:
        return "question"

    def create_reply_suggestion(self, message: dict[str, Any]) -> str:
        return f"Hallo {message['sender']}, danke fuer deine Nachricht."

    def get_contact_type(self, sender: str) -> str:
        return "other"

    def generate_local_suggestions(self) -> list[dict]:
        return []

    def generate_local_task_suggestions(self) -> list[dict]:
        return []

    def get_pending_suggestions(self) -> list[dict]:
        return []

    def get_pending_task_suggestions(self) -> list[dict]:
        return []


class _CalendarAgentStub:
    def get_free_slots_today(self, duration_minutes: int = 60) -> list[dict]:
        return [{"start": "10:00", "end": "11:00"}]

    def get_items_for_date(self, date_iso: str) -> list[dict]:
        return []


class _BriefingAgentStub:
    def build_preview(self, today_iso: str | None = None) -> dict[str, Any]:
        return {
            "date": "2026-07-05",
            "tasks": [],
            "calendar_items": [],
            "weather": "Platzhalter",
            "music": "Platzhalter",
        }


def _build_interface(tmp_path) -> tuple[FridayInterface, TaskAgent]:
    db_path = tmp_path / "friday.db"
    initialize_database(db_path)
    task_agent = TaskAgent(db_path=db_path)
    interface = FridayInterface(
        task_agent=task_agent,
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        briefing_agent=_BriefingAgentStub(),
        approval_agent=None,
    )
    return interface, task_agent


def test_friday_1_0_user_acceptance_journey(tmp_path, monkeypatch, capsys) -> None:
    interface, task_agent = _build_interface(tmp_path)
    main_choices = iter(["1", "13", "12", "7"])
    task_choices = iter(["9", "2", "4", "11", "12"])
    scripted_inputs = iter(
        [
            "Acceptance Quick !hoch @morgen",
            "j",
            "Acceptance Wiederkehrend",
            "arbeit",
            "2026-07-05",
            "Akzeptanztest",
            "high",
            "taeglich",
            "2",
            "Acceptance Empfaenger",
            "Acceptance Betreff",
            "Acceptance Nachricht",
            "5",
            "6",
            "11",
        ]
    )

    def _input(prompt: str = "") -> str:
        if "ID der Aufgabe" in prompt:
            recurring = [
                task
                for task in task_agent.get_open_tasks()
                if task["title"] == "Acceptance Wiederkehrend"
            ]
            assert recurring
            return str(recurring[0]["id"])
        return next(scripted_inputs)

    monkeypatch.setattr("builtins.input", _input)
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_choices))
    monkeypatch.setattr("friday.app.interface.show_task_menu", lambda: next(task_choices))
    monkeypatch.setattr("friday.app.interface.resolve_today", lambda: "2026-07-05")
    monkeypatch.setattr("friday.app.quick_add_parser.resolve_today", lambda: "2026-07-05")

    interface.run()
    output = capsys.readouterr().out

    assert "Friday 1.0.0 – lokaler Assistent gestartet." in output
    assert "Aufgabe wurde schnell erstellt." in output
    assert "Aufgabe wurde erstellt." in output
    assert "Aufgabe wurde als erledigt markiert." in output
    assert "Lokale Tagesplanung fuer 2026-07-05" in output
    assert "E-Mail-Entwurf wurde lokal verworfen." in output
    assert "Privacy Dashboard" in output
    assert "Friday wird beendet." in output

    quick_tasks = [
        task for task in task_agent.get_open_tasks() if task["title"] == "Acceptance Quick"
    ]
    assert quick_tasks

    follow_up_tasks = [
        task
        for task in task_agent.get_open_tasks()
        if task["title"] == "Acceptance Wiederkehrend"
    ]
    assert len(follow_up_tasks) == 1
    assert follow_up_tasks[0]["due_date"] == "2026-07-06"
    assert follow_up_tasks[0]["recurrence"] == "taeglich"
    assert interface.email_drafts[-1].status == "discarded"
