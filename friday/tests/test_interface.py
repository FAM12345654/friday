"""Tests for Friday interface helper behavior."""

from __future__ import annotations

from typing import Any, Dict, List

from friday.app.interface import FridayInterface


class _MessageAgentStub:
    def get_messages(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": 1,
                "sender": "Kollege",
                "text": "Kannst du morgen um 10 Uhr ein Treffen bestätigen?",
                "received_at": "2026-07-05T08:00:00",
            }
        ]

    def is_scheduling_related(self, text: str) -> bool:
        return "treffen" in text.lower()

    def create_reply_suggestion(self, message: Dict[str, Any]) -> str:
        return f"Vorschlag für {message['sender']}"

    def get_contact_type(self, sender: str) -> str:
        return "Freund"


class _CalendarAgentStub:
    def get_free_slots_today(self, duration_minutes: int = 60):
        return [
            {"start": "11:00", "end": "12:00"},
            {"start": "15:00", "end": "16:00"},
        ]


class _TaskAgentStub:
    def get_open_tasks(self) -> List[Dict[str, Any]]:
        return []

    def detect_priority_hint(self, task: Dict[str, Any]) -> str:
        return "normal"

    def get_task_by_id(self, task_id: int) -> Dict[str, Any] | None:
        return None


class _ApprovalAgentFailing:
    def request_approval(
        self, action: str, message: str | None = None, context: Dict[str, Any] | None = None
    ) -> str:
        raise AssertionError("Approval should not be called during display functions.")


def test_interface_has_review_pending_suggestions() -> None:
    interface = FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=_ApprovalAgentFailing(),
    )
    assert callable(getattr(interface, "review_pending_suggestions", None))


def test_open_task_management_can_be_triggered() -> None:
    interface = FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=_ApprovalAgentFailing(),
    )
    called: Dict[str, int] = {"open": 0}

    def _fake_open_task_management() -> None:
        called["open"] += 1

    interface.open_task_management = _fake_open_task_management  # type: ignore[method-assign]
    assert interface.handle_menu_choice("1") is True
    assert called["open"] == 1


def test_display_methods_do_not_call_approval() -> None:
    interface = FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=_ApprovalAgentFailing(),
    )
    interface._show_messages_with_suggestions()
    interface._show_calendar()
