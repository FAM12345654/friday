"""Tests for Friday's effective date helper."""

from __future__ import annotations

from datetime import date

from friday import config
from friday.app import date_utils


def test_resolve_today_uses_system_date_when_enabled(monkeypatch) -> None:
    monkeypatch.setattr(config, "USE_REAL_TODAY", True)

    assert date_utils.resolve_today() == date.today().isoformat()


def test_resolve_today_uses_demo_date_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr(config, "USE_REAL_TODAY", False)
    monkeypatch.setattr(config, "DEMO_DATE", "2026-07-05")

    assert date_utils.resolve_today() == "2026-07-05"


def test_day_plan_preview_uses_resolved_today(monkeypatch, capsys) -> None:
    from friday.app.interface import FridayInterface

    class _TaskAgent:
        def get_open_tasks(self) -> list[dict]:
            return []

    monkeypatch.setattr("friday.app.interface.resolve_today", lambda: "2030-01-02")
    interface = FridayInterface(task_agent=_TaskAgent())

    interface._show_local_day_plan_preview()
    output = capsys.readouterr().out

    assert "2030-01-02" in output
    assert config.DEMO_DATE not in output
