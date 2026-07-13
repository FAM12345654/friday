"""CalDAV calendar provider for Friday (Nextcloud, iCloud, Radicale, ...).

Speaks plain CalDAV over HTTPS with stdlib urllib — no extra dependency.
The HTTP transport is injectable so tests never touch the network, matching
the fetcher pattern of the ICS provider.
"""

from __future__ import annotations

import base64
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime, time, timezone
from typing import Any, Callable
from urllib import error, request

from friday.app.calendar_provider_base import CalendarProviderEvent, CalendarProviderResult

# transport(method, url, headers, body, timeout) -> (status_code, response_body)
Transport = Callable[[str, str, dict[str, str], bytes | None, int], tuple[int, bytes]]

_NS = {
    "d": "DAV:",
    "c": "urn:ietf:params:xml:ns:caldav",
}

_REPORT_TEMPLATE = """<?xml version="1.0" encoding="utf-8" ?>
<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:prop>
    <d:getetag/>
    <c:calendar-data/>
  </d:prop>
  <c:filter>
    <c:comp-filter name="VCALENDAR">
      <c:comp-filter name="VEVENT">
        <c:time-range start="{start}" end="{end}"/>
      </c:comp-filter>
    </c:comp-filter>
  </c:filter>
</c:calendar-query>
"""


def _default_transport(
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes | None,
    timeout_seconds: int,
) -> tuple[int, bytes]:
    req = request.Request(url, data=body, method=method)
    for name, value in headers.items():
        req.add_header(name, value)
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            return response.status, response.read()
    except error.HTTPError as exc:
        return exc.code, exc.read()


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


def _caldav_stamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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


class CaldavCalendarProvider:
    """Read/write CalDAV provider using basic auth."""

    provider_name = "caldav"

    def __init__(
        self,
        *,
        calendar_url: str,
        username: str,
        password: str,
        transport: Transport | None = None,
        timeout_seconds: int = 10,
        calendar_id: str = "caldav",
    ) -> None:
        self.calendar_url = calendar_url.rstrip("/") + "/"
        self.username = username
        self.password = password
        self.transport = transport or _default_transport
        self.timeout_seconds = int(timeout_seconds)
        self.calendar_id = calendar_id

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _auth_header(self) -> str:
        credentials = f"{self.username}:{self.password}".encode("utf-8")
        return "Basic " + base64.b64encode(credentials).decode("ascii")

    def _request(
        self,
        method: str,
        url: str,
        *,
        body: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes]:
        headers = {
            "Authorization": self._auth_header(),
            "User-Agent": "friday-caldav/1.0",
        }
        if extra_headers:
            headers.update(extra_headers)
        return self.transport(method, url, headers, body, self.timeout_seconds)

    # ------------------------------------------------------------------
    # Provider interface
    # ------------------------------------------------------------------

    def test_connection(self) -> CalendarProviderResult:
        try:
            status, _ = self._request(
                "PROPFIND",
                self.calendar_url,
                body=b'<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>',
                extra_headers={"Depth": "0", "Content-Type": "application/xml; charset=utf-8"},
            )
            if 200 <= status < 300 or status == 207:
                return CalendarProviderResult(
                    ok=True,
                    message="CalDAV-Kalender erreichbar.",
                    external_call_used=True,
                )
            return CalendarProviderResult(
                ok=False,
                message=f"CalDAV-Verbindung fehlgeschlagen (HTTP {status}).",
                blocked_reasons=("caldav_unreachable",),
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - defensive provider boundary
            return CalendarProviderResult(
                ok=False,
                message=f"CalDAV-Verbindung fehlgeschlagen: {exc}",
                blocked_reasons=("caldav_unreachable",),
                external_call_used=True,
            )

    def list_events(self, *, range_start: str, range_end: str) -> CalendarProviderResult:
        try:
            import recurring_ical_events
            from icalendar import Calendar

            start = _parse_boundary(range_start)
            end = _parse_boundary(range_end, end_of_day=True)
            report = _REPORT_TEMPLATE.format(
                start=_caldav_stamp(start), end=_caldav_stamp(end)
            ).encode("utf-8")

            status, payload = self._request(
                "REPORT",
                self.calendar_url,
                body=report,
                extra_headers={"Depth": "1", "Content-Type": "application/xml; charset=utf-8"},
            )
            if status != 207:
                return CalendarProviderResult(
                    ok=False,
                    message=f"CalDAV-Abfrage fehlgeschlagen (HTTP {status}).",
                    blocked_reasons=("caldav_list_failed",),
                    external_call_used=True,
                )

            events: list[CalendarProviderEvent] = []
            root = ET.fromstring(payload)
            for response in root.findall("d:response", _NS):
                data_node = response.find(".//c:calendar-data", _NS)
                if data_node is None or not (data_node.text or "").strip():
                    continue
                calendar = Calendar.from_ical(data_node.text)
                for component in recurring_ical_events.of(calendar).between(start, end):
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
                            title=_component_text(component, "SUMMARY") or "CalDAV-Termin",
                            start=_to_iso(dtstart),
                            end=_to_iso(dtend),
                            location=_component_text(component, "LOCATION"),
                            raw={"uid": uid, "source": "caldav"},
                        )
                    )
            return CalendarProviderResult(
                ok=True,
                events=tuple(events),
                message="CalDAV-Events gelesen.",
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - defensive provider boundary
            return CalendarProviderResult(
                ok=False,
                message=f"CalDAV-Events konnten nicht gelesen werden: {exc}",
                blocked_reasons=("caldav_list_failed",),
                external_call_used=True,
            )

    def create_event(self, event: CalendarProviderEvent) -> CalendarProviderResult:
        try:
            from icalendar import Calendar, Event

            uid = event.id or f"friday-{uuid.uuid4()}"
            calendar = Calendar()
            calendar.add("prodid", "-//Friday//CalDAV//DE")
            calendar.add("version", "2.0")
            vevent = Event()
            vevent.add("uid", uid)
            vevent.add("summary", event.title)
            vevent.add("dtstart", _parse_boundary(event.start))
            vevent.add("dtend", _parse_boundary(event.end, end_of_day="T" not in event.end))
            vevent.add("dtstamp", datetime.now(timezone.utc))
            if event.location:
                vevent.add("location", event.location)
            calendar.add_component(vevent)

            status, _ = self._request(
                "PUT",
                f"{self.calendar_url}{uid}.ics",
                body=calendar.to_ical(),
                extra_headers={
                    "Content-Type": "text/calendar; charset=utf-8",
                    # Never overwrite an existing event.
                    "If-None-Match": "*",
                },
            )
            if status in (200, 201, 204):
                return CalendarProviderResult(
                    ok=True,
                    provider_event_id=uid,
                    message="CalDAV-Termin erstellt.",
                    external_call_used=True,
                )
            if status == 412:
                return CalendarProviderResult(
                    ok=False,
                    message="CalDAV-Termin existiert bereits (UID-Konflikt).",
                    blocked_reasons=("caldav_conflict",),
                    external_call_used=True,
                )
            return CalendarProviderResult(
                ok=False,
                message=f"CalDAV-Termin konnte nicht erstellt werden (HTTP {status}).",
                blocked_reasons=("caldav_create_failed",),
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - defensive provider boundary
            return CalendarProviderResult(
                ok=False,
                message=f"CalDAV-Termin konnte nicht erstellt werden: {exc}",
                blocked_reasons=("caldav_create_failed",),
                external_call_used=True,
            )

    def delete_event(self, *, event_id: str, calendar_id: str) -> CalendarProviderResult:
        normalized = str(event_id or "").strip()
        if not normalized:
            return CalendarProviderResult(
                ok=False,
                message="CalDAV-Löschen ohne Event-ID ist nicht möglich.",
                blocked_reasons=("caldav_missing_event_id",),
                external_call_used=False,
            )
        try:
            status, _ = self._request("DELETE", f"{self.calendar_url}{normalized}.ics")
            if status in (200, 202, 204):
                return CalendarProviderResult(
                    ok=True,
                    provider_event_id=normalized,
                    message="CalDAV-Termin gelöscht.",
                    external_call_used=True,
                )
            if status == 404:
                return CalendarProviderResult(
                    ok=False,
                    message="CalDAV-Termin wurde nicht gefunden.",
                    blocked_reasons=("caldav_not_found",),
                    provider_event_id=normalized,
                    external_call_used=True,
                )
            return CalendarProviderResult(
                ok=False,
                message=f"CalDAV-Termin konnte nicht gelöscht werden (HTTP {status}).",
                blocked_reasons=("caldav_delete_failed",),
                provider_event_id=normalized,
                external_call_used=True,
            )
        except Exception as exc:  # pragma: no cover - defensive provider boundary
            return CalendarProviderResult(
                ok=False,
                message=f"CalDAV-Termin konnte nicht gelöscht werden: {exc}",
                blocked_reasons=("caldav_delete_failed",),
                provider_event_id=normalized,
                external_call_used=True,
            )
