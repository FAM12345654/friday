"""Tests for the CalDAV calendar provider with a fake transport."""

from __future__ import annotations

from friday.app.calendar_provider_base import CalendarProviderEvent
from friday.app.calendar_provider_caldav import CaldavCalendarProvider

CALENDAR_ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//DE
BEGIN:VEVENT
UID:event-1
SUMMARY:Zahnarzt
DTSTART:20260715T090000Z
DTEND:20260715T100000Z
LOCATION:Praxis
END:VEVENT
END:VCALENDAR
"""

MULTISTATUS = f"""<?xml version="1.0"?>
<d:multistatus xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:response>
    <d:href>/cal/event-1.ics</d:href>
    <d:propstat>
      <d:prop>
        <d:getetag>"abc"</d:getetag>
        <c:calendar-data>{CALENDAR_ICS}</c:calendar-data>
      </d:prop>
      <d:status>HTTP/1.1 200 OK</d:status>
    </d:propstat>
  </d:response>
</d:multistatus>
"""


class FakeTransport:
    def __init__(self, responses: dict[str, tuple[int, bytes]]) -> None:
        self.responses = responses
        self.calls: list[dict] = []

    def __call__(self, method, url, headers, body, timeout):
        self.calls.append(
            {"method": method, "url": url, "headers": headers, "body": body}
        )
        return self.responses.get(method, (500, b""))


def _provider(transport) -> CaldavCalendarProvider:
    return CaldavCalendarProvider(
        calendar_url="https://cloud.example.com/cal",
        username="philip",
        password="geheim",
        transport=transport,
    )


def test_test_connection_ok_on_207() -> None:
    transport = FakeTransport({"PROPFIND": (207, b"<d:multistatus xmlns:d='DAV:'/>")})
    result = _provider(transport).test_connection()
    assert result.ok
    call = transport.calls[0]
    assert call["method"] == "PROPFIND"
    assert call["headers"]["Authorization"].startswith("Basic ")
    assert call["headers"]["Depth"] == "0"


def test_test_connection_fails_on_401() -> None:
    transport = FakeTransport({"PROPFIND": (401, b"")})
    result = _provider(transport).test_connection()
    assert not result.ok
    assert "401" in result.message


def test_list_events_parses_multistatus() -> None:
    transport = FakeTransport({"REPORT": (207, MULTISTATUS.encode("utf-8"))})
    result = _provider(transport).list_events(
        range_start="2026-07-14", range_end="2026-07-16"
    )
    assert result.ok, result.message
    assert len(result.events) == 1
    event = result.events[0]
    assert event.id == "event-1"
    assert event.title == "Zahnarzt"
    assert event.location == "Praxis"
    assert event.provider == "caldav"
    # Time-range filter went into the REPORT body.
    body = transport.calls[0]["body"].decode("utf-8")
    assert 'start="20260714T000000Z"' in body


def test_list_events_outside_range_filtered() -> None:
    transport = FakeTransport({"REPORT": (207, MULTISTATUS.encode("utf-8"))})
    result = _provider(transport).list_events(
        range_start="2026-08-01", range_end="2026-08-02"
    )
    assert result.ok
    assert result.events == ()


def test_create_event_puts_ics_with_no_overwrite() -> None:
    transport = FakeTransport({"PUT": (201, b"")})
    event = CalendarProviderEvent(
        id=None,
        provider="caldav",
        calendar_id="caldav",
        title="Neuer Termin",
        start="2026-07-20T09:00:00+00:00",
        end="2026-07-20T10:00:00+00:00",
        location="Büro",
    )
    result = _provider(transport).create_event(event)
    assert result.ok, result.message
    assert result.provider_event_id
    call = transport.calls[0]
    assert call["method"] == "PUT"
    assert call["headers"]["If-None-Match"] == "*"
    assert b"SUMMARY:Neuer Termin" in call["body"]
    assert call["url"].endswith(f"{result.provider_event_id}.ics")


def test_create_event_conflict_maps_to_blocked() -> None:
    transport = FakeTransport({"PUT": (412, b"")})
    event = CalendarProviderEvent(
        id="event-1",
        provider="caldav",
        calendar_id="caldav",
        title="Doppelt",
        start="2026-07-20T09:00:00+00:00",
        end="2026-07-20T10:00:00+00:00",
    )
    result = _provider(transport).create_event(event)
    assert not result.ok
    assert "caldav_conflict" in result.blocked_reasons


def test_delete_event_ok() -> None:
    transport = FakeTransport({"DELETE": (204, b"")})
    result = _provider(transport).delete_event(event_id="event-1", calendar_id="caldav")
    assert result.ok
    assert transport.calls[0]["url"].endswith("/event-1.ics")


def test_delete_event_not_found() -> None:
    transport = FakeTransport({"DELETE": (404, b"")})
    result = _provider(transport).delete_event(event_id="fehlt", calendar_id="caldav")
    assert not result.ok
    assert "caldav_not_found" in result.blocked_reasons


def test_delete_event_requires_id() -> None:
    transport = FakeTransport({})
    result = _provider(transport).delete_event(event_id="", calendar_id="caldav")
    assert not result.ok
    assert transport.calls == []
