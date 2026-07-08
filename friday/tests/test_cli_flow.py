"""End-to-end style CLI flow tests for Friday."""

from __future__ import annotations

from typing import Any, Dict, List

from friday.app.interface import FridayInterface


class _TaskAgentStub:
    def get_task_by_id(self, task_id: int) -> Dict[str, Any] | None:
        return None

    def get_open_tasks(self) -> List[Dict[str, Any]]:
        return [{"id": 1, "title": "Test", "category": "work", "status": "open", "due_date": "2026-07-05"}]

    def detect_priority_hint(self, task: Dict[str, Any]) -> str:
        return "normal"

    def get_tasks_for_date(self, date_iso: str | None = None) -> List[Dict[str, Any]]:
        return []


class _MessageAgentStub:
    def get_messages(self) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "sender": "Kollege", "text": "Lass uns das heute kurz besprechen", "received_at": "2026-07-05T08:00:00"},
        ]

    def is_scheduling_related(self, text: str) -> bool:
        return "treffen" in text.lower()

    def create_reply_suggestion(self, message: Dict[str, Any]) -> str:
        return f"Vorschlag für {message['sender']}"

    def get_contact_type(self, sender: str) -> str:
        return "Freund"


class _CalendarAgentStub:
    def get_free_slots_today(self, duration_minutes: int = 60):
        return [{"start": "11:00", "end": "12:00"}]

    def get_items_for_date(self, date_iso: str):
        return []


class _BriefingAgentStub:
    def build_preview(self, today_iso: str | None = None) -> Dict[str, Any]:
        return {
            "date": "2026-07-05",
            "tasks": [],
            "calendar_items": [],
            "weather": "Demo",
            "music": "Demo",
        }


class _ApprovalAgentFailing:
    def request_approval(self, action: str, message: str | None = None, context: Dict[str, Any] | None = None) -> str:
        raise AssertionError("No approval should be requested in this flow.")


def _build_interface() -> FridayInterface:
    return FridayInterface(
        task_agent=_TaskAgentStub(),
        message_agent=_MessageAgentStub(),
        calendar_agent=_CalendarAgentStub(),
        approval_agent=_ApprovalAgentFailing(),
        briefing_agent=_BriefingAgentStub(),
    )


def test_option_6_opens_review_and_continues() -> None:
    interface = _build_interface()
    calls: Dict[str, int] = {"review": 0}

    def _fake_review() -> None:
        calls["review"] += 1

    interface.review_pending_suggestions = _fake_review  # type: ignore[method-assign]
    should_continue = interface.handle_menu_choice("6")

    assert should_continue is True
    assert calls["review"] == 1


def test_option_11_opens_backup_restore_menu_and_continues() -> None:
    interface = _build_interface()
    calls: Dict[str, int] = {"backup_restore": 0}

    def _fake_backup_restore() -> None:
        calls["backup_restore"] += 1

    interface.open_backup_restore_menu = _fake_backup_restore  # type: ignore[method-assign]
    should_continue = interface.handle_menu_choice("11")

    assert should_continue is True
    assert calls["backup_restore"] == 1


def test_option_13_opens_email_draft_preview_and_continues() -> None:
    interface = _build_interface()
    calls: Dict[str, int] = {"email_preview": 0}

    def _fake_email_preview() -> None:
        calls["email_preview"] += 1

    interface.show_email_draft_preview = _fake_email_preview  # type: ignore[method-assign]
    should_continue = interface.handle_menu_choice("13")

    assert should_continue is True
    assert calls["email_preview"] == 1


def test_option_1_opens_task_management_and_continues() -> None:
    interface = _build_interface()
    calls: Dict[str, int] = {"tasks": 0}

    def _open_task_management() -> None:
        calls["tasks"] += 1

    interface.open_task_management = _open_task_management  # type: ignore[method-assign]
    assert interface.handle_menu_choice("1") is True
    assert calls["tasks"] == 1


def test_option_7_exits() -> None:
    interface = _build_interface()
    assert interface.handle_menu_choice("7") is False


def test_invalid_choice_keeps_running(capsys) -> None:
    interface = _build_interface()
    should_continue = interface.handle_menu_choice("x")

    assert should_continue is True
    out = capsys.readouterr().out
    assert "Ungültige Auswahl. Bitte erneut versuchen." in out


def test_display_options_do_not_call_approval() -> None:
    interface = _build_interface()
    for choice in ("1", "2", "3", "4", "5"):
        interface.open_task_management = (lambda: None)  # type: ignore[method-assign]
        assert interface.handle_menu_choice(choice) is True


def test_only_option_6_triggers_review() -> None:
    interface = _build_interface()
    calls: Dict[str, int] = {"review": 0}
    interface.open_task_management = (lambda: None)  # type: ignore[method-assign]

    def _fake_review() -> None:
        calls["review"] += 1

    interface.review_pending_suggestions = _fake_review  # type: ignore[method-assign]

    for choice in ("1", "2", "3", "4", "5", "7"):
        if choice == "7":
            assert interface.handle_menu_choice(choice) is False
        else:
            assert interface.handle_menu_choice(choice) is True

    assert calls["review"] == 0

    assert interface.handle_menu_choice("6") is True
    assert calls["review"] == 1
