"""Tests for the read-only Outlook ICS calendar provider."""

from __future__ import annotations

from friday.app.calendar_provider_base import CalendarProviderEvent
from friday.app.calendar_provider_ics import OutlookIcsCalendarProvider


def _fetcher(payload: str):
    def _inner(_url: str, _timeout_seconds: int) -> bytes:
        return payload.encode("utf-8")

    return _inner


def test_ics_provider_reads_timed_event_without_real_network() -> None:
    provider = OutlookIcsCalendarProvider(
        ics_url="https://example.invalid/calendar.ics",
        fetcher=_fetcher(
            """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:timed-1
SUMMARY:PH Dienst
DTSTART:20260715T080000Z
DTEND:20260715T120000Z
LOCATION:Buero
END:VEVENT
END:VCALENDAR
"""
        ),
    )

    result = provider.list_events(range_start="2026-07-15", range_end="2026-07-15")

    assert result.ok is True
    assert result.external_call_used is True
    assert result.events[0].id == "timed-1"
    assert result.events[0].title == "PH Dienst"
    assert result.events[0].provider == "outlook_ics"
    assert result.events[0].location == "Buero"


def test_ics_provider_reads_all_day_event_without_real_network() -> None:
    provider = OutlookIcsCalendarProvider(
        ics_url="https://example.invalid/calendar.ics",
        fetcher=_fetcher(
            """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:all-day-1
SUMMARY:PH Frei
DTSTART;VALUE=DATE:20260715
DTEND;VALUE=DATE:20260716
END:VEVENT
END:VCALENDAR
"""
        ),
    )

    result = provider.list_events(range_start="2026-07-15", range_end="2026-07-15")

    assert result.ok is True
    assert result.events[0].title == "PH Frei"
    assert result.events[0].start == "2026-07-15"


def test_ics_provider_expands_simple_recurring_event_without_real_network() -> None:
    provider = OutlookIcsCalendarProvider(
        ics_url="https://example.invalid/calendar.ics",
        fetcher=_fetcher(
            """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:repeat-1
SUMMARY:PH Wiederholung
DTSTART:20260710T080000Z
DTEND:20260710T090000Z
RRULE:FREQ=DAILY;COUNT=3
END:VEVENT
END:VCALENDAR
"""
        ),
    )

    result = provider.list_events(range_start="2026-07-11", range_end="2026-07-11")

    assert result.ok is True
    assert any(event.title == "PH Wiederholung" for event in result.events)


def test_ics_provider_returns_error_without_exposing_secret_url() -> None:
    def _broken(_url: str, _timeout_seconds: int) -> bytes:
        raise RuntimeError("boom")

    provider = OutlookIcsCalendarProvider(
        ics_url="https://secret.invalid/private.ics",
        fetcher=_broken,
    )

    result = provider.list_events(range_start="2026-07-15", range_end="2026-07-15")

    assert result.ok is False
    assert "ics_list_failed" in result.blocked_reasons
    assert "secret.invalid" not in result.message


def test_ics_provider_is_read_only() -> None:
    provider = OutlookIcsCalendarProvider(ics_url="https://example.invalid/calendar.ics")

    create_result = provider.create_event(
        CalendarProviderEvent(
            id=None,
            provider="outlook_ics",
            calendar_id="outlook_ics",
            title="Termin",
            start="2026-07-15",
            end="2026-07-15",
        )
    )
    delete_result = provider.delete_event(event_id="event-1", calendar_id="outlook_ics")

    assert create_result.ok is False
    assert delete_result.ok is False
    assert create_result.blocked_reasons == ("ics_read_only",)
    assert delete_result.blocked_reasons == ("ics_read_only",)
