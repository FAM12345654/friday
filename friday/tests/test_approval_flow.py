"""Tests for safe local approval behavior."""

from __future__ import annotations

from friday.agents.approval_agent import ApprovalAgent


def test_request_approval_returns_expected_statuses(monkeypatch) -> None:
    """ApprovalAgent should only ever return the documented status values."""
    agent = ApprovalAgent()

    cases = [
        ("j", "approved"),
        ("n", "rejected"),
        ("", "pending"),
        ("x", "pending"),
    ]
    for user_input, expected in cases:
        monkeypatch.setattr("builtins.input", lambda _=None, value=user_input: value)
        status = agent.request_approval("Testaktion")
        assert status == expected
