"""Tests for Google Calendar provider mapping without real network calls."""

from __future__ import annotations

from friday.app import calendar_provider_google
from friday.app.calendar_provider_base import CalendarProviderEvent
from friday.app.calendar_provider_google import (
    GoogleCalendarProvider,
    exchange_google_oauth_authorization_response,
)


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

    def delete(self, **_kwargs):
        return _Executable({})


class _CalendarList:
    def get(self, **_kwargs):
        return _Executable({"id": "primary"})


class _Service:
    def events(self):
        return _Events()

    def calendarList(self):
        return _CalendarList()


class _FakeCredentials:
    def to_json(self):
        return '{"token": "fake-token"}'


class _FakeFlow:
    def __init__(self):
        self.credentials = _FakeCredentials()
        self.authorization_response = None

    def fetch_token(self, *, authorization_response):
        self.authorization_response = authorization_response


class _FakeInstalledAppFlow:
    latest_flow = None

    @classmethod
    def from_client_secrets_file(cls, *_args, **_kwargs):
        cls.latest_flow = _FakeFlow()
        return cls.latest_flow


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


def test_google_provider_maps_delete_event_without_real_network() -> None:
    provider = GoogleCalendarProvider(service=_Service())

    result = provider.delete_event(event_id="created-1", calendar_id="primary")

    assert result.ok is True
    assert result.provider_event_id == "created-1"
    assert result.external_call_used is True


def test_google_oauth_exchange_uses_authorization_response_without_returning_secret(
    tmp_path,
    monkeypatch,
) -> None:
    secrets_path = tmp_path / "client_secret.json"
    secrets_path.write_text('{"installed": {"client_id": "fake"}}', encoding="utf-8")
    monkeypatch.setattr(
        calendar_provider_google,
        "_load_google_dependencies",
        lambda: {
            "InstalledAppFlow": _FakeInstalledAppFlow,
            "Credentials": object,
            "build": object,
        },
    )

    result = exchange_google_oauth_authorization_response(
        client_secrets_path=secrets_path,
        authorization_response="http://localhost/?code=abc&scope=calendar",
    )

    assert result.ok is True
    assert result.credentials_json == '{"token": "fake-token"}'
    assert result.external_call_used is True
    assert _FakeInstalledAppFlow.latest_flow is not None
    assert (
        _FakeInstalledAppFlow.latest_flow.authorization_response
        == "http://localhost/?code=abc&scope=calendar"
    )


def test_to_rfc3339_normalizes_date_only_inputs():
    # Google's timeMin/timeMax reject plain dates with HTTP 400; date-only inputs
    # must become full RFC3339 timestamps.
    assert calendar_provider_google._to_rfc3339("2026-07-01") == "2026-07-01T00:00:00Z"
    assert (
        calendar_provider_google._to_rfc3339("2026-07-31", end_of_day=True)
        == "2026-07-31T23:59:59Z"
    )


def test_to_rfc3339_passes_through_datetimes_and_empty():
    existing = "2026-07-01T09:30:00+02:00"
    assert calendar_provider_google._to_rfc3339(existing) == existing
    assert calendar_provider_google._to_rfc3339("") == ""
