"""CLI coverage for Microsoft mail relevance display."""

from __future__ import annotations

from friday.agents.calendar_agent import CalendarAgent
from friday.agents.message_agent import MessageAgent
from friday.agents.task_agent import TaskAgent
from friday.app.interface import FridayInterface
from friday.storage.database import setup_local_database
from friday.storage.repositories import MsMailMessageRepository


def test_cli_all_ms_mail_view_shows_hidden_office_relevance_reason(tmp_path, capsys) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)
    MsMailMessageRepository(db_path).upsert_messages(
        [
            {
                "message_id": "graph-office-hidden",
                "sender": "info@example.test",
                "subject": "Bitte Unterlagen prüfen",
                "received_at": "2026-07-09T10:00:00Z",
                "snippet": "Bitte erledigen.",
                "recipients": [{"name": "Alex", "address": "alex@familienhelden.at"}],
            }
        ],
        account_id="office_familienhelden_at",
        account_username="office@familienhelden.at",
    )
    interface = FridayInterface(
        task_agent=TaskAgent(db_path=db_path),
        message_agent=MessageAgent(db_path=db_path),
        calendar_agent=CalendarAgent(db_path=db_path),
        approval_agent=None,
    )

    interface._show_all_ms_mail_messages()
    output = capsys.readouterr().out

    assert "Microsoft-Mails (alle lokalen Vorschauen)" in output
    assert "Bitte Unterlagen prüfen" in output
    assert "Im Standardfilter sichtbar: nein (not_relevant)" in output
