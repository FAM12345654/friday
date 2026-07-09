"""Read-only Outlook ICS calendar provider for Friday.

Only this module may fetch ICS URLs. The URL is encrypted at rest and never
returned by status endpoints or logs.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any, Callable
from urllib import request

from friday.app.calendar_ics_account_store import (
    OutlookIcsAccount,
    decrypt_outlook_ics_url,
    load_outlook_ics_account,
)
from friday.app.calendar_provider_base import CalendarProviderEvent, CalendarProviderResult


FetchIcs = Callable[[str, int], bytes | str]


def _parse_boundary(value: str, *, end_of_day: bool = False) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ValueError("Kalender-Zeitbereich fehlt.")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if "T" not in text:
        boundary_time = time.max if end_of_day else time.min
        return datetime.combine(date.fromisoformat(text), boundary_time, tzinfo=timezone.utc)
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _to_iso(value: Any) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value or "")


def _component_text(component: Any, name: str) -> str | None:
    value = component.get(name)
    if value is None:
        return None
    return str(value)


def _default_fetch_ics(url: str, timeout_seconds: int) -> bytes:
    with request.urlopen(url, timeout=timeout_seconds) as response:
        return response.read()


class OutlookIcsCalendarProvider:
    """Read-only provider for Outlook published ICS calendars."""

    provider_name = "outlook_ics"

    def __init__(
        self,
        *,
        policy_id: int | None = None,
        ics_url: str | None = None,
        account: OutlookIcsAccount | None = None,
        fetcher: FetchIcs | None = None,
        timeout_seconds: int = 10,
        calendar_id: str = "outlook_ics",
    ) -> None:
        self.policy_id = policy_id
        self.ics_url = ics_url
        self.account = account
        self.fetcher = fetcher or _default_fetch_ics
        self.timeout_seconds = int(timeout_seconds)
        self.calendar_id = calendar_id

    def _resolve_url(self) -> str:
        if self.ics_url:
            return str(self.ics_url).strip()
        account = self.account
        if account is None and self.policy_id is not None:
            account = load_outlook_ics_account(int(self.policy_id))
        if account is None:
            raise RuntimeError("Keine Outlook-ICS-Quelle verbunden.")
        return decrypt_outlook_ics_url(account)

    def _fetch_calendar(self):
        from icalendar import Calendar

        raw = self.fetcher(self._resolve_url(), self.timeout_seconds)
        payload = raw.encode("utf-8") if isinstance(raw, str) else raw
        return Calendar.from_ical(payload)

    def test_connection(self) -> CalendarProviderResult:
        try:
            self._fetch_calendar()
            return CalendarProviderResult(
                ok=True,
                message="Outlook-ICS-Quelle gelesen.",
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - defensive provider boundary
            return CalendarProviderResult(
                ok=False,
                message=f"Outlook-ICS-Lesen fehlgeschlagen: {exc}",
                blocked_reasons=("ics_read_failed",),
                external_call_used=True,
            )

    def list_events(self, *, range_start: str, range_end: str) -> CalendarProviderResult:
        try:
            import recurring_ical_events

            calendar = self._fetch_calendar()
            start = _parse_boundary(range_start)
            end = _parse_boundary(range_end, end_of_day=True)
            components = recurring_ical_events.of(calendar).between(start, end)
            events: list[CalendarProviderEvent] = []
            for component in components:
                if component.name != "VEVENT":
                    continue
                uid = _component_text(component, "UID")
                dtstart = component.decoded("DTSTART")
                dtend = component.decoded("DTEND", None)
                if dtend is None:
                    dtend = dtstart
                events.append(
                    CalendarProviderEvent(
                        id=uid,
                        provider=self.provider_name,
                        calendar_id=self.calendar_id,
                        title=_component_text(component, "SUMMARY") or "Outlook-Termin",
                        start=_to_iso(dtstart),
                        end=_to_iso(dtend),
                        location=_component_text(component, "LOCATION"),
                        raw={
                            "uid": uid,
                            "source": "outlook_ics",
                            "policy_id": self.policy_id,
                        },
                    )
                )
            return CalendarProviderResult(
                ok=True,
                events=tuple(events),
                message="Outlook-ICS-Events gelesen.",
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - defensive provider boundary
            return CalendarProviderResult(
                ok=False,
                message=f"Outlook-ICS-Events konnten nicht gelesen werden: {exc}",
                blocked_reasons=("ics_list_failed",),
                external_call_used=True,
            )

    def create_event(self, event: CalendarProviderEvent) -> CalendarProviderResult:
        return CalendarProviderResult(
            ok=False,
            message="Outlook-ICS ist nur lesbar. Es wurde nichts erstellt.",
            blocked_reasons=("ics_read_only",),
            external_call_used=False,
        )

    def delete_event(self, *, event_id: str, calendar_id: str) -> CalendarProviderResult:
        return CalendarProviderResult(
            ok=False,
            message="Outlook-ICS ist nur lesbar. Es wurde nichts geloescht.",
            blocked_reasons=("ics_read_only",),
            provider_event_id=str(event_id or "").strip() or None,
            external_call_used=False,
        )
