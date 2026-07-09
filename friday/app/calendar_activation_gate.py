"""Guard for enabling real calendar access in Friday."""

from __future__ import annotations

from dataclasses import asdict, dataclass


CALENDAR_ACTIVATION_TOKEN = "KALENDER AKTIVIEREN"


@dataclass(frozen=True)
class CalendarActivationGate:
    """Preview result for calendar activation."""

    allowed: bool
    would_enable_real_calendar: bool
    message: str
    blocked_reasons: tuple[str, ...]
    preview_only: bool
    external_call_used: bool

    def to_dict(self) -> dict:
        return asdict(self)


def build_calendar_activation_gate(
    *,
    approval_token: str,
    account_connected: bool,
    connection_test_ok: bool,
    scanner_smoke_passed: bool,
) -> CalendarActivationGate:
    """Check whether Friday may enable real calendar access."""
    blocked: list[str] = []
    if approval_token != CALENDAR_ACTIVATION_TOKEN:
        blocked.append("approval_token_invalid")
    if not account_connected:
        blocked.append("calendar_account_missing")
    if not connection_test_ok:
        blocked.append("calendar_connection_test_failed")
    if not scanner_smoke_passed:
        blocked.append("scanner_smoke_not_passed")

    if blocked:
        return CalendarActivationGate(
            allowed=False,
            would_enable_real_calendar=False,
            message="Kalender-Aktivierung blockiert.",
            blocked_reasons=tuple(blocked),
            preview_only=True,
            external_call_used=False,
        )
    return CalendarActivationGate(
        allowed=True,
        would_enable_real_calendar=True,
        message="Kalender-Aktivierung waere erlaubt. Config-Write bleibt separater Apply-Schritt.",
        blocked_reasons=(),
        preview_only=True,
        external_call_used=False,
    )

