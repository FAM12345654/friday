"""Tests for real-calendar activation and write guards."""

from __future__ import annotations

from friday.app.calendar_activation_gate import (
    CALENDAR_ACTIVATION_TOKEN,
    build_calendar_activation_gate,
)
from friday.app.calendar_event_write_guard import (
    CALENDAR_EVENT_SAVE_TOKEN,
    check_calendar_event_write_allowed,
)


def test_calendar_activation_gate_blocks_without_account_and_smoke() -> None:
    gate = build_calendar_activation_gate(
        approval_token=CALENDAR_ACTIVATION_TOKEN,
        account_connected=False,
        connection_test_ok=False,
        scanner_smoke_passed=False,
    )

    assert gate.allowed is False
    assert "calendar_account_missing" in gate.blocked_reasons
    assert "scanner_smoke_not_passed" in gate.blocked_reasons


def test_calendar_activation_gate_allows_only_after_all_checks() -> None:
    gate = build_calendar_activation_gate(
        approval_token=CALENDAR_ACTIVATION_TOKEN,
        account_connected=True,
        connection_test_ok=True,
        scanner_smoke_passed=True,
    )

    assert gate.allowed is True
    assert gate.would_enable_real_calendar is True


def test_calendar_event_write_guard_blocks_when_real_calendar_disabled() -> None:
    guard = check_calendar_event_write_allowed(
        approval_token=CALENDAR_EVENT_SAVE_TOKEN,
        real_calendar_enabled=False,
        main_policy_ok=True,
        connection_ok=True,
    )

    assert guard.allowed is False
    assert "real_calendar_disabled" in guard.blocked_reasons


def test_calendar_event_write_guard_requires_exact_token() -> None:
    guard = check_calendar_event_write_allowed(
        approval_token="JA",
        real_calendar_enabled=True,
        main_policy_ok=True,
        connection_ok=True,
    )

    assert guard.allowed is False
    assert "approval_token_invalid" in guard.blocked_reasons
