"""Tests for Friday's deterministic morning-routine wake time."""

from __future__ import annotations

from datetime import date, time
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from friday.app.morning_routine import compute_wake_time


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location(
        "friday_api_main_for_morning_routine_test",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_compute_wake_time_uses_first_appointment_before_cutoff() -> None:
    appointment = {
        "id": "appointment-1",
        "title": "Frueher Kundentermin",
        "start": "2026-07-15T08:30:00+02:00",
        "end": "2026-07-15T09:00:00+02:00",
    }

    result = compute_wake_time(date(2026, 7, 15), calendar_events=[appointment])

    assert result.alarm_time == time(7, 0)
    assert result.reason == "Erster Termin um 08:30 - 90min Vorbereitung"
    assert result.first_appointment == appointment
    assert result.is_workday is True


def test_compute_wake_time_uses_default_without_early_appointment() -> None:
    result = compute_wake_time(
        date(2026, 7, 15),
        calendar_events=[
            {
                "title": "Spaeter Termin",
                "start": "2026-07-15T10:30:00+02:00",
            }
        ],
    )

    assert result.alarm_time == time(8, 0)
    assert result.first_appointment is None
    assert result.is_workday is False


def test_compute_wake_time_uses_fixed_fallback_on_calendar_failure() -> None:
    result = compute_wake_time(date(2026, 7, 15), calendar_failed=True)

    assert result.alarm_time == time(7, 0)
    assert "Kalender konnte nicht gelesen werden" in result.reason
    assert result.first_appointment is None
    assert result.is_workday is False


def test_wake_time_endpoint_uses_cached_calendar_payload(monkeypatch) -> None:
    api = _load_api_module()

    async def _cached_calendar(**kwargs):
        assert kwargs["date"] == "2026-07-15"
        return {
            "ok": True,
            "data": {
                "merged_items": [
                    {
                        "title": "Teamtermin",
                        "start": "2026-07-15T09:00:00+02:00",
                    }
                ],
                "source_errors": [],
            },
        }

    monkeypatch.setattr(api, "get_calendar", _cached_calendar)
    response = TestClient(api.app).get("/morning-routine/wake-time?date=2026-07-15")

    assert response.status_code == 200
    assert response.json()["alarm_time"] == "07:30:00"
    assert response.json()["is_workday"] is True


def test_wake_time_endpoint_falls_back_when_calendar_read_raises(monkeypatch) -> None:
    api = _load_api_module()

    async def _failed_calendar(**_kwargs):
        raise RuntimeError("calendar unavailable")

    monkeypatch.setattr(api, "get_calendar", _failed_calendar)
    response = TestClient(api.app).get("/morning-routine/wake-time?date=2026-07-15")

    assert response.status_code == 200
    assert response.json()["alarm_time"] == "07:00:00"
    assert response.json()["is_workday"] is False
