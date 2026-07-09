"""Tests for Google Calendar provider mapping without real network calls."""

from __future__ import annotations

from friday.app.calendar_provider_base import CalendarProviderEvent
from friday.app.calendar_provider_google import GoogleCalendarProvider


class _Executable:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return self.payload


class _Events:
    def list(self, **_kwargs):
        return _Executable(
            {
                "items": [
                    {
                        "id": "abc",
                        "summary": "PH Dienst",
                        "start": {"dateTime": "2026-07-15T10:00:00+02:00"},
                        "end": {"dateTime": "2026-07-15T11:00:00+02:00"},
                        "location": "Buero",
                    }
                ]
            }
        )

    def insert(self, **_kwargs):
        return _Executable(
            {
                "id": "created-1",
                "summary": "Termin",
                "start": {"dateTime": "2026-07-15T10:00:00+02:00"},
                "end": {"dateTime": "2026-07-15T11:00:00+02:00"},
            }
        )


class _CalendarList:
    def get(self, **_kwargs):
        return _Executable({"id": "primary"})


class _Service:
    def events(self):
        return _Events()

    def calendarList(self):
        return _CalendarList()


def test_google_provider_maps_list_events_without_real_network() -> None:
    provider = GoogleCalendarProvider(service=_Service())

    result = provider.list_events(
        range_start="2026-07-15T00:00:00+02:00",
        range_end="2026-07-16T00:00:00+02:00",
    )

    assert result.ok is True
    assert result.external_call_used is True
    assert result.events[0].title == "PH Dienst"
    assert result.events[0].provider == "google_calendar"


def test_google_provider_maps_create_event_without_real_network() -> None:
    provider = GoogleCalendarProvider(service=_Service())

    result = provider.create_event(
        CalendarProviderEvent(
            id=None,
            provider="google_calendar",
            calendar_id="primary",
            title="Termin",
            start="2026-07-15T10:00:00+02:00",
            end="2026-07-15T11:00:00+02:00",
        )
    )

    assert result.ok is True
    assert result.provider_event_id == "created-1"
    assert result.event is not None

