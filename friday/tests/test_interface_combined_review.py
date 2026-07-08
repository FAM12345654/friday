"""Tests for the combined suggestions review flow in the terminal."""

from __future__ import annotations

from friday.agents.calendar_agent import CalendarAgent
from friday.agents.message_agent import MessageAgent
from friday.agents.task_agent import TaskAgent
from friday.app.interface import FridayInterface
from friday.storage.database import setup_local_database


class _NoSuggestionMessageAgent:
    def generate_local_suggestions(self) -> list[dict]:
        return []

    def generate_local_task_suggestions(self) -> list[dict]:
        return []

    def get_pending_suggestions(self) -> list[dict]:
        return []

    def get_pending_task_suggestions(self) -> list[dict]:
        return []

    def get_messages(self) -> list[dict]:
        return []


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
        approval_agent=None,
    )
    return interface, message_agent, task_agent


def _set_inputs(monkeypatch, values: list[str]) -> None:
    iterator = iter(values)

    def _next_input(_: str = "") -> str:
        return next(iterator)

    monkeypatch.setattr("builtins.input", _next_input)


def _insert_custom_messages(message_agent: MessageAgent, messages: list[dict]) -> list[dict]:
    message_agent.get_messages = lambda: messages  # type: ignore[method-assign]
    return messages


class _PassingSafetySmoke:
    passed = True


def _patch_passing_safety_smoke(monkeypatch) -> None:
    monkeypatch.setattr("friday.app.interface.run_safety_smoke", lambda: _PassingSafetySmoke())


def test_combined_review_shows_counts_for_message_and_task_suggestions(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 10, "sender": "Chef", "text": "Kannst du morgen einen Termin bestätigen?"},
            {"id": 11, "sender": "Kollege", "text": "Kannst du bitte den Report fertig machen?"},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()

    _set_inputs(monkeypatch, [""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Offene Nachrichten-Vorschläge:" in output
    assert "Offene Aufgaben-Vorschläge:" in output


def test_combined_review_shows_contact_candidate_preview_for_unknown_sender(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {
                "id": 20,
                "sender": "Unbekannte Person",
                "text": "Kannst du morgen einen Termin bestätigen?",
            },
        ],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, [""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Kontakt-Kontext Hinweise:" in output
    assert "Kontakt-Kontext möglich: Unbekannte Person ist noch unbekannt." in output
    assert interface.contact_context_repository.list_contact_contexts() == []


def test_combined_review_does_not_show_contact_candidate_for_known_context(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    interface.contact_context_repository.create_contact_context(
        contact_id="contact-known",
        display_name="Bekannte Person",
        contact_type="kunde",
        source_context="person_bearbeiten",
        user_approved_persistence=True,
        sensitivity_checked=True,
    )
    _insert_custom_messages(
        message_agent,
        [
            {
                "id": 21,
                "sender": "Bekannte Person",
                "text": "Kannst du morgen einen Termin bestätigen?",
            },
        ],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, [""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Kontakt-Kontext möglich: Bekannte Person ist noch unbekannt." not in output


def test_combined_review_shows_contact_only_candidate_without_other_suggestions(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {
                "id": 221,
                "sender": "Nur Kontakt",
                "text": "Zur Info: kurzes Statusupdate.",
            },
        ],
    )

    _set_inputs(monkeypatch, [""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Keine offenen Vorschläge vorhanden." not in output
    assert "Offene Nachrichten-Vorschläge: 0" in output
    assert "Offene Aufgaben-Vorschläge: 0" in output
    assert "Offene Kontakt-Kontext-Hinweise: 1" in output
    assert "Kontakt-Kontext möglich: Nur Kontakt ist noch unbekannt." in output


def test_combined_review_contact_draft_aborts_without_save_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {
                "id": 22,
                "sender": "Draft Person",
                "text": "Kannst du morgen einen Termin bestätigen?",
            },
        ],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, ["4", "1", "2", "", "z", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Kontakt-Kontext Vorschau" in output
    assert "Kontaktart: kollege" in output
    assert "Speichern wurde abgebrochen." in output
    assert interface.contact_context_repository.find_contact_by_normalized_name("draft person") is None


def test_combined_review_contact_draft_saves_with_hard_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {
                "id": 23,
                "sender": "Save Person",
                "text": "Kannst du morgen einen Termin bestätigen?",
            },
        ],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, ["4", "1", "2", "SPEICHERN", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    saved = interface.contact_context_repository.find_contact_by_normalized_name("save person")

    assert "Kontakt-Kontext wurde lokal gespeichert." in output
    assert saved is not None
    assert saved["display_name"] == "Save Person"
    assert saved["contact_type"] == "kollege"
    assert saved["user_approved_persistence"] == 1


def test_combined_review_contact_draft_skip_suppresses_without_saving(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {
                "id": 24,
                "sender": "Skip Person",
                "text": "Kannst du morgen einen Termin bestätigen?",
            },
        ],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, ["4", "1", "8", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Kontakt-Hinweis wurde für diese Sitzung übersprungen." in output
    assert interface.contact_context_repository.find_contact_by_normalized_name("skip person") is None
    assert "Kontakt-Kontext möglich: Skip Person ist noch unbekannt." not in output.split(
        "Kontakt-Hinweis wurde für diese Sitzung übersprungen.",
        1,
    )[-1]


def test_combined_review_returns_when_no_suggestions_exist(monkeypatch, capsys) -> None:
    interface = FridayInterface(
        message_agent=_NoSuggestionMessageAgent(),
        task_agent=TaskAgent(),
        calendar_agent=CalendarAgent(),
        approval_agent=None,
    )

    _set_inputs(monkeypatch, [""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Keine offenen Vorschläge vorhanden." in output


def test_combined_review_invalid_area_choice_continues(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [{"id": 10, "sender": "Chef", "text": "Kannst du morgen einen Termin bestätigen?"}],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, ["x", "", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültige Auswahl. Bitte erneut versuchen." in output


def test_combined_review_batch_preview_shows_selected_visible_suggestions(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 10, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 11, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestions = message_agent.generate_local_suggestions()
    task_suggestions = message_agent.generate_local_task_suggestions()
    before_tasks = task_agent.get_open_tasks()
    assert message_suggestions
    assert task_suggestions

    _set_inputs(monkeypatch, ["5", "1,2", "", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Batch-Auswahl Vorschläge" in output
    assert "Batch-Auswahl-Vorschau" in output
    assert "Nachrichten-Vorschlag" in output
    assert "Aufgaben-Vorschlag" in output
    assert "Es wurde noch nichts freigegeben, abgelehnt oder gesendet." in output
    assert message_agent.get_pending_suggestions()
    assert message_agent.get_pending_task_suggestions()
    assert task_agent.get_open_tasks() == before_tasks


def test_combined_review_batch_apply_approves_message_with_hard_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _patch_passing_safety_smoke(monkeypatch)
    _insert_custom_messages(
        message_agent,
        [{"id": 40, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"}],
    )
    message_suggestions = message_agent.generate_local_suggestions()
    assert message_suggestions

    _set_inputs(monkeypatch, ["5", "1", "1", "BATCH FREIGEBEN", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Batch-Auswahl-Vorschau" in output
    assert "Safety Smoke: PASS" in output
    assert "Batch-Aktion wurde lokal ausgefuehrt." in output
    assert message_agent.get_pending_suggestions() == []


def test_combined_review_batch_apply_rejects_wrong_token_and_keeps_pending(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _patch_passing_safety_smoke(monkeypatch)
    _insert_custom_messages(
        message_agent,
        [{"id": 41, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"}],
    )
    message_suggestions = message_agent.generate_local_suggestions()
    assert message_suggestions

    _set_inputs(monkeypatch, ["5", "1", "1", "FALSCH", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Batch-Aktion wurde nicht freigegeben." in output
    assert "invalid_token" in output
    assert message_agent.get_pending_suggestions()


def test_combined_review_batch_apply_creates_task_with_hard_token(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _patch_passing_safety_smoke(monkeypatch)
    _insert_custom_messages(
        message_agent,
        [{"id": 42, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."}],
    )
    task_suggestions = message_agent.generate_local_task_suggestions()
    before_tasks = task_agent.get_open_tasks()
    assert task_suggestions

    _set_inputs(monkeypatch, ["5", "1", "3", "BATCH AUFGABEN ERSTELLEN", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Batch-Auswahl-Vorschau" in output
    assert "Batch-Aktion wurde lokal ausgefuehrt." in output
    assert "Erstellte lokale Aufgaben:" in output
    assert message_agent.get_pending_task_suggestions() == []
    assert len(task_agent.get_open_tasks()) == len(before_tasks) + 1


def test_combined_review_activity_summary_shows_local_review_counts(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 43, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 44, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    message_agent.approve_suggestion(message_suggestion["id"])
    message_agent.mark_task_suggestion_converted(task_suggestion["id"], created_task_id=123)

    _set_inputs(monkeypatch, ["6", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "6. Review-Aktivität anzeigen" in output
    assert "Review-Aktivität" in output
    assert "Nachrichten-Vorschläge:" in output
    assert "- Lokal freigegeben: 1" in output
    assert "Aufgaben-Vorschläge:" in output
    assert "- In Aufgaben umgewandelt: 1" in output
    assert "- Mit lokaler Aufgabe verknüpft: 1" in output
    assert "Aufgaben-Vorschlag" in output
    assert "-> Aufgabe 123" in output


def test_combined_review_activity_summary_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 45, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 46, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()
    before_messages = message_agent.get_pending_suggestions()
    before_tasks = message_agent.get_pending_task_suggestions()

    _set_inputs(monkeypatch, ["6", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Review-Aktivität" in output
    assert "Token:" not in output
    assert message_agent.get_pending_suggestions() == before_messages
    assert message_agent.get_pending_task_suggestions() == before_tasks


def test_combined_review_activity_detail_view_shows_local_review_items(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 47, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 48, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    message_agent.approve_suggestion(message_suggestion["id"])
    message_agent.mark_task_suggestion_converted(task_suggestion["id"], created_task_id=456)

    _set_inputs(monkeypatch, ["7", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "7. Review-Aktivität im Detail anzeigen" in output
    assert "Review-Aktivität im Detail" in output
    assert "Nachrichten-Vorschläge:" in output
    assert "Aufgaben-Vorschläge:" in output
    assert "[approved]" in output
    assert "[converted]" in output
    assert "-> Aufgabe 456" in output


def test_combined_review_activity_detail_view_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 49, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 50, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()
    before_messages = message_agent.get_pending_suggestions()
    before_tasks = message_agent.get_pending_task_suggestions()

    _set_inputs(monkeypatch, ["7", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Review-Aktivität im Detail" in output
    assert "Token:" not in output
    assert message_agent.get_pending_suggestions() == before_messages
    assert message_agent.get_pending_task_suggestions() == before_tasks


def test_combined_review_activity_status_filter_shows_converted_items(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 51, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 52, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    message_agent.approve_suggestion(message_suggestion["id"])
    message_agent.mark_task_suggestion_converted(task_suggestion["id"], created_task_id=789)

    _set_inputs(monkeypatch, ["8", "converted", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "8. Review-Aktivität nach Status filtern" in output
    assert "Review-Aktivität nach Status" in output
    assert "Statusfilter: converted" in output
    assert "[converted]" in output
    assert "-> Aufgabe 789" in output
    assert "[approved]" not in output


def test_combined_review_activity_status_filter_invalid_value_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 53, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 54, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()
    before_messages = message_agent.get_pending_suggestions()
    before_tasks = message_agent.get_pending_task_suggestions()

    _set_inputs(monkeypatch, ["8", "komisch", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungültiger Review-Statusfilter." in output
    assert "Token:" not in output
    assert message_agent.get_pending_suggestions() == before_messages
    assert message_agent.get_pending_task_suggestions() == before_tasks


def test_combined_review_activity_type_filter_shows_message_items(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 55, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 56, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    message_agent.approve_suggestion(message_suggestion["id"])
    message_agent.mark_task_suggestion_converted(task_suggestion["id"], created_task_id=790)

    _set_inputs(monkeypatch, ["9", "message", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "9. Review-Aktivität nach Typ filtern" in output
    assert "Review-Aktivität nach Typ" in output
    assert "Typfilter: message" in output
    assert "[approved]" in output
    assert "[converted]" not in output
    assert "-> Aufgabe 790" not in output


def test_combined_review_activity_type_filter_shows_task_items(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 57, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 58, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    message_agent.approve_suggestion(message_suggestion["id"])
    message_agent.mark_task_suggestion_converted(task_suggestion["id"], created_task_id=791)

    _set_inputs(monkeypatch, ["9", "task", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Review-Aktivität nach Typ" in output
    assert "Typfilter: task" in output
    assert "[converted]" in output
    assert "-> Aufgabe 791" in output
    assert "[approved]" not in output


def test_combined_review_activity_type_filter_invalid_value_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 59, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 60, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()
    before_messages = message_agent.get_pending_suggestions()
    before_tasks = message_agent.get_pending_task_suggestions()

    _set_inputs(monkeypatch, ["9", "contact", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungueltiger Review-Typfilter." in output
    assert "Token:" not in output
    assert message_agent.get_pending_suggestions() == before_messages
    assert message_agent.get_pending_task_suggestions() == before_tasks


def test_combined_review_activity_search_shows_matching_items(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 61, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 62, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    message_agent.approve_suggestion(message_suggestion["id"])
    message_agent.mark_task_suggestion_converted(task_suggestion["id"], created_task_id=792)

    _set_inputs(monkeypatch, ["10", "converted", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "10. Review-Aktivität durchsuchen" in output
    assert "Review-Aktivität durchsuchen" in output
    assert "Suchbegriff: converted" in output
    assert "[converted]" in output
    assert "-> Aufgabe 792" in output
    assert "[approved]" not in output


def test_combined_review_activity_search_without_matches_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 63, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 64, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()
    before_messages = message_agent.get_pending_suggestions()
    before_tasks = message_agent.get_pending_task_suggestions()

    _set_inputs(monkeypatch, ["10", "zz", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Keine lokalen Review-Details für diesen Suchbegriff gefunden." in output
    assert "Token:" not in output
    assert message_agent.get_pending_suggestions() == before_messages
    assert message_agent.get_pending_task_suggestions() == before_tasks


def test_combined_review_activity_search_short_query_is_read_only(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 65, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 66, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()
    before_messages = message_agent.get_pending_suggestions()
    before_tasks = message_agent.get_pending_task_suggestions()

    _set_inputs(monkeypatch, ["10", "c", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Ungueltiger Review-Suchbegriff." in output
    assert "Token:" not in output
    assert message_agent.get_pending_suggestions() == before_messages
    assert message_agent.get_pending_task_suggestions() == before_tasks


def test_combined_review_batch_preview_invalid_id_keeps_suggestions_pending(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 12, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 13, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()
    before_tasks = task_agent.get_open_tasks()

    _set_inputs(monkeypatch, ["5", "999", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Batch-Auswahl-Vorschau" in output
    assert "Ungültige Auswahl. Bitte erneut versuchen." in output
    assert "Es wurde noch nichts freigegeben, abgelehnt oder gesendet." in output
    assert message_agent.get_pending_suggestions()
    assert message_agent.get_pending_task_suggestions()
    assert task_agent.get_open_tasks() == before_tasks


def test_combined_review_can_review_message_then_task_in_one_session(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    messages = _insert_custom_messages(
        message_agent,
        [
            {"id": 10, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 11, "sender": "Chef", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestions = message_agent.generate_local_suggestions()
    task_suggestions = message_agent.generate_local_task_suggestions()
    assert message_suggestions
    assert task_suggestions

    _set_inputs(
        monkeypatch,
        [
            "1",
            str(message_suggestions[0]["id"]),
            "a",
            "2",
            str(task_suggestions[0]["id"]),
            "a",
            "",
        ],
    )
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet." in output
    assert "Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt." in output

    assert messages is not None
    message_approved = message_agent.approve_suggestion(message_suggestions[0]["id"])
    assert message_approved is not None
    assert message_approved["status"] == "approved"

    task_suggestion = message_agent.task_suggestion_repository.get_task_suggestion_by_id(task_suggestions[0]["id"])  # type: ignore[union-attr]
    assert task_suggestion is not None
    assert task_suggestion["status"] == "converted"
    assert task_suggestion["created_task_id"] is not None
    task = task_agent.get_task_by_id(int(task_suggestion["created_task_id"]))
    assert task is not None


def test_converted_task_suggestion_does_not_create_duplicate_task(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [{"id": 10, "sender": "Chef", "text": "Bitte bitte die Unterlagen prüfen."}],
    )
    message_agent.generate_local_task_suggestions()
    suggestion = message_agent.generate_local_task_suggestions()[0]
    before_tasks = len(task_agent.get_open_tasks())

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "a", ""])
    interface.review_pending_suggestions()
    after_first = task_agent.get_open_tasks()
    assert len(after_first) == before_tasks + 1

    interface._handle_task_suggestion_action(
        suggestion=suggestion,
        action="a",
    )
    assert len(task_agent.get_open_tasks()) == before_tasks + 1


def test_only_task_suggestions_still_reviewable(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    message_agent.generate_local_suggestions = lambda: []  # type: ignore[method-assign]
    message_agent.get_pending_suggestions = lambda: []  # type: ignore[method-assign]

    _insert_custom_messages(
        message_agent,
        [{"id": 10, "sender": "Chef", "text": "Bitte bitte die Unterlagen prüfen."}],
    )
    suggestion = message_agent.generate_local_task_suggestions()[0]
    before_tasks = len(task_agent.get_open_tasks())

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "a", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt." in output
    assert len(task_agent.get_open_tasks()) == before_tasks + 1


def test_only_message_suggestions_still_reviewable(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    message_agent.generate_local_task_suggestions = lambda: []  # type: ignore[method-assign]
    message_agent.get_pending_task_suggestions = lambda: []  # type: ignore[method-assign]

    _insert_custom_messages(
        message_agent,
        [{"id": 10, "sender": "Chef", "text": "Kannst du morgen einen Termin bestätigen?"}],
    )
    suggestion = message_agent.generate_local_suggestions()[0]
    _set_inputs(monkeypatch, ["1", str(suggestion["id"]), "a", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet." in output


def test_combined_review_refresh_option_keeps_session_open(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 10, "sender": "Chef", "text": "Kannst du morgen einen Termin bestätigen?"},
            {"id": 11, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()

    _set_inputs(monkeypatch, ["3", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert output.count("Offene Nachrichten-Vorschläge:") >= 2
    assert output.count("Offene Aufgaben-Vorschläge:") >= 2
    assert len(message_agent.get_pending_suggestions()) >= 1
    assert len(message_agent.get_pending_task_suggestions()) >= 1


def test_combined_review_z_returns_to_main_menu(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 12, "sender": "Chef", "text": "Kannst du morgen einen Termin bestätigen?"},
            {"id": 13, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."},
        ],
    )
    message_agent.generate_local_suggestions()
    message_agent.generate_local_task_suggestions()

    initial_messages = message_agent.get_pending_suggestions()
    initial_tasks = message_agent.get_pending_task_suggestions()
    assert initial_messages
    assert initial_tasks
    _set_inputs(monkeypatch, ["z"])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert len(message_agent.get_pending_suggestions()) == len(initial_messages)
    assert len(message_agent.get_pending_task_suggestions()) == len(initial_tasks)
    assert "Keine offenen Vorschläge vorhanden." not in output


def test_message_review_z_returns_to_combined_overview(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [{"id": 14, "sender": "Chef", "text": "Kannst du morgen einen Termin bestätigen?"}],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, ["1", "z", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert output.count("Bereich wählen:") >= 2
    assert "Offene Nachrichten-Vorschläge: 1" in output


def test_task_review_z_returns_to_combined_overview(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [{"id": 15, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."}],
    )
    message_agent.generate_local_task_suggestions()
    message_agent.generate_local_suggestions = lambda: []  # type: ignore[method-assign]
    message_agent.get_pending_suggestions = lambda: []  # type: ignore[method-assign]

    suggestion = message_agent.generate_local_task_suggestions()[0]
    _set_inputs(monkeypatch, ["2", "z", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert output.count("Bereich wählen:") >= 2
    pending = message_agent.get_pending_task_suggestions()
    assert any(item["id"] == suggestion["id"] for item in pending)


def test_task_suggestion_detail_shows_known_contact_snapshot(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    interface.contact_context_repository.create_contact_context(
        contact_id="contact-chef",
        display_name="Chef",
        contact_type="kollege",
        source_context="person_bearbeiten",
        user_approved_persistence=True,
        sensitivity_checked=True,
    )
    _insert_custom_messages(
        message_agent,
        [{"id": 25, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."}],
    )
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "z", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Kontakt-Snapshot: | Quelle: Chef | Kontaktart: kollege" in output


def test_task_suggestion_conversion_adds_contact_snapshot_to_created_task_notes(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    interface.contact_context_repository.create_contact_context(
        contact_id="contact-chef",
        display_name="Chef",
        contact_type="kollege",
        source_context="person_bearbeiten",
        user_approved_persistence=True,
        sensitivity_checked=True,
    )
    _insert_custom_messages(
        message_agent,
        [{"id": 26, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."}],
    )
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "a", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out

    assert "Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt." in output
    converted = message_agent.task_suggestion_repository.get_task_suggestion_by_id(suggestion["id"])  # type: ignore[union-attr]
    assert converted is not None
    task = task_agent.get_task_by_id(int(converted["created_task_id"]))
    assert task is not None
    assert "Kontakt-Snapshot:" in task["notes"]
    assert "Quelle: Chef" in task["notes"]
    assert "Kontaktart: kollege" in task["notes"]


def test_converted_task_suggestion_not_listed_as_open(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [{"id": 16, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."}],
    )
    message_agent.generate_local_task_suggestions()
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "a", ""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt." in output

    assert message_agent.get_pending_task_suggestions() == []
    still_open_message_agent = message_agent.get_pending_task_suggestions()
    assert still_open_message_agent == []


def test_review_journey_from_main_menu_message_and_task_flow(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    messages = _insert_custom_messages(
        message_agent,
        [
            {
                "id": 30,
                "sender": "Chef",
                "text": "Kannst du den Termin morgen bestätigen?",
                "received_at": "2026-07-06T09:00:00",
            },
            {
                "id": 31,
                "sender": "Chef",
                "text": "Bitte bitte diese Aufgabe erledigen.",
                "received_at": "2026-07-06T09:05:00",
            },
        ],
    )

    message_suggestions = message_agent.generate_local_suggestions()
    task_suggestions = message_agent.generate_local_task_suggestions()
    assert message_suggestions
    assert task_suggestions
    assert messages is not None

    message_suggestion_id = str(message_suggestions[0]["id"])
    task_suggestion_id = str(task_suggestions[0]["id"])
    review_inputs = iter(
        [
            "1",
            message_suggestion_id,
            "a",
            "2",
            task_suggestion_id,
            "a",
            "z",
        ]
    )
    main_menu_inputs = iter(["6", "7"])

    monkeypatch.setattr("builtins.input", lambda _: next(review_inputs))
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_menu_inputs))
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]

    interface.run()
    output = capsys.readouterr().out

    assert "Vorschläge prüfen / freigeben" in output
    assert "Offene Nachrichten-Vorschläge:" in output
    assert "Offene Aufgaben-Vorschläge:" in output
    assert "Vorschlag wurde lokal freigegeben. Es wurde nichts gesendet." in output
    assert "Aufgaben-Vorschlag wurde als lokale Aufgabe erstellt." in output
    assert "Friday wird beendet." in output

    pending_message_ids = {item["id"] for item in message_agent.get_pending_suggestions()}
    assert message_suggestions[0]["id"] not in pending_message_ids

    task_suggestion = message_agent.task_suggestion_repository.get_task_suggestion_by_id(  # type: ignore[union-attr]
        task_suggestions[0]["id"]
    )
    assert task_suggestion is not None
    assert task_suggestion["status"] == "converted"
    assert task_suggestion["created_task_id"] is not None

    created_task = task_agent.get_task_by_id(int(task_suggestion["created_task_id"]))
    assert created_task is not None
    assert created_task["title"] == task_suggestion["title"]


def test_review_activity_search_journey_from_main_menu(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [
            {"id": 32, "sender": "Chef", "text": "Kannst du morgen den Termin bestätigen?"},
            {"id": 33, "sender": "Team", "text": "Bitte bitte die Rechnung prüfen."},
        ],
    )
    message_suggestion = message_agent.generate_local_suggestions()[0]
    task_suggestion = message_agent.generate_local_task_suggestions()[0]
    message_agent.approve_suggestion(message_suggestion["id"])
    message_agent.mark_task_suggestion_converted(task_suggestion["id"], created_task_id=793)

    review_inputs = iter(["10", "converted", "z"])
    main_menu_inputs = iter(["6", "7"])

    monkeypatch.setattr("builtins.input", lambda _: next(review_inputs))
    monkeypatch.setattr("friday.app.interface.show_menu", lambda: next(main_menu_inputs))
    interface.show_dashboard = lambda: None  # type: ignore[method-assign]

    interface.run()
    output = capsys.readouterr().out

    assert "Review-Aktivität durchsuchen" in output
    assert "Suchbegriff: converted" in output
    assert "[converted]" in output
    assert "-> Aufgabe 793" in output
    assert "Friday wird beendet." in output


def test_direct_reconvert_task_suggestion_does_not_duplicate_task(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, task_agent = _build_interface(tmp_path)
    _insert_custom_messages(
        message_agent,
        [{"id": 17, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."}],
    )
    message_agent.generate_local_task_suggestions()
    suggestion = message_agent.generate_local_task_suggestions()[0]

    _set_inputs(monkeypatch, ["2", str(suggestion["id"]), "a", ""])
    interface.review_pending_suggestions()
    before = task_agent.get_open_tasks()
    output = capsys.readouterr().out
    assert any(task["title"] == suggestion["title"] for task in before)

    suggestion = message_agent.task_suggestion_repository.get_task_suggestion_by_id(suggestion["id"])  # type: ignore[union-attr]
    assert suggestion is not None
    interface._handle_task_suggestion_action(suggestion, "a")
    after = task_agent.get_open_tasks()

    assert len(after) == len(before)
    direct_output = capsys.readouterr().out
    assert (
        "Aufgaben-Vorschlag wurde bereits in eine lokale Aufgabe umgewandelt."
        in direct_output
    )


def test_only_message_suggestions_overview_still_works(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    message_agent.generate_local_task_suggestions = lambda: []  # type: ignore[method-assign]
    message_agent.get_pending_task_suggestions = lambda: []  # type: ignore[method-assign]
    _insert_custom_messages(
        message_agent,
        [{"id": 18, "sender": "Chef", "text": "Kannst du morgen einen Termin bestätigen?"}],
    )
    message_agent.generate_local_suggestions()

    _set_inputs(monkeypatch, [""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Offene Nachrichten-Vorschläge: 1" in output
    assert "Offene Aufgaben-Vorschläge: 0" in output


def test_only_task_suggestions_overview_still_works(tmp_path, monkeypatch, capsys) -> None:
    interface, message_agent, _task_agent = _build_interface(tmp_path)
    message_agent.generate_local_suggestions = lambda: []  # type: ignore[method-assign]
    message_agent.get_pending_suggestions = lambda: []  # type: ignore[method-assign]
    _insert_custom_messages(
        message_agent,
        [{"id": 19, "sender": "Chef", "text": "Bitte bitte den Report fertig machen."}],
    )
    message_agent.generate_local_task_suggestions()

    _set_inputs(monkeypatch, [""])
    interface.review_pending_suggestions()
    output = capsys.readouterr().out
    assert "Offene Nachrichten-Vorschläge: 0" in output
    assert "Offene Aufgaben-Vorschläge: 1" in output
