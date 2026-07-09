"""Calendar provider abstractions for Friday."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class CalendarProviderEvent:
    """One normalized calendar event."""

    id: str | None
    provider: str
    calendar_id: str
    title: str
    start: str
    end: str
    location: str | None = None
    raw: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CalendarProviderResult:
    """Structured provider operation result."""

    ok: bool
    events: tuple[CalendarProviderEvent, ...] = ()
    event: CalendarProviderEvent | None = None
    message: str = ""
    blocked_reasons: tuple[str, ...] = ()
    provider_event_id: str | None = None
    external_call_used: bool = False


class CalendarProvider(Protocol):
    """Provider interface for real calendar implementations."""

    provider_name: str

    def test_connection(self) -> CalendarProviderResult:
        """Check whether the provider is reachable and authenticated."""

    def list_events(self, *, range_start: str, range_end: str) -> CalendarProviderResult:
        """List events in one range."""

    def create_event(self, event: CalendarProviderEvent) -> CalendarProviderResult:
        """Create one event in the provider."""

    def delete_event(self, *, event_id: str, calendar_id: str) -> CalendarProviderResult:
        """Delete one event in the provider."""
