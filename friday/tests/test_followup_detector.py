"""Tests for the follow-up ("waiting on reply") detector."""

from __future__ import annotations

from datetime import datetime, timezone

from friday.app.followup_detector import (
    detect_followups,
    extract_email_address,
)

NOW = datetime(2026, 7, 13, 12, 0, tzinfo=timezone.utc)


def _sent(recipient: str, subject: str, sent_at: str, status: str = "sent") -> dict:
    return {"recipient": recipient, "subject": subject, "sent_at": sent_at, "status": status}


def _inbound(sender: str, received_at: str) -> dict:
    return {"sender": sender, "received_at": received_at}


def test_extract_email_address_variants() -> None:
    assert extract_email_address("anna@example.com") == "anna@example.com"
    assert extract_email_address("Anna B <Anna@Example.com>") == "anna@example.com"
    assert extract_email_address("kein-treffer") == ""
    assert extract_email_address(None) == ""


def test_unanswered_old_email_is_flagged() -> None:
    result = detect_followups(
        [_sent("anna@example.com", "Angebot", "2026-07-08T09:00:00+00:00")],
        [],
        now=NOW,
    )
    assert len(result) == 1
    assert result[0].recipient == "anna@example.com"
    assert result[0].days_waiting == 5
    assert "Angebot" in result[0].to_dict()["suggestion"]


def test_reply_after_send_clears_followup() -> None:
    result = detect_followups(
        [_sent("anna@example.com", "Angebot", "2026-07-08T09:00:00+00:00")],
        [_inbound("Anna <anna@example.com>", "2026-07-09T10:00:00+00:00")],
        now=NOW,
    )
    assert result == []


def test_reply_before_send_does_not_count() -> None:
    result = detect_followups(
        [_sent("anna@example.com", "Angebot", "2026-07-08T09:00:00+00:00")],
        [_inbound("anna@example.com", "2026-07-01T10:00:00+00:00")],
        now=NOW,
    )
    assert len(result) == 1


def test_recent_sends_are_not_flagged_yet() -> None:
    result = detect_followups(
        [_sent("anna@example.com", "Angebot", "2026-07-12T09:00:00+00:00")],
        [],
        now=NOW,
        threshold_days=3,
    )
    assert result == []


def test_failed_sends_are_ignored() -> None:
    result = detect_followups(
        [_sent("anna@example.com", "Angebot", "2026-07-01T09:00:00+00:00", status="failed")],
        [],
        now=NOW,
    )
    assert result == []


def test_ancient_sends_are_dropped() -> None:
    result = detect_followups(
        [_sent("anna@example.com", "Uralt", "2026-01-01T09:00:00+00:00")],
        [],
        now=NOW,
        max_age_days=30,
    )
    assert result == []


def test_latest_send_per_recipient_subject_wins() -> None:
    result = detect_followups(
        [
            _sent("anna@example.com", "Angebot", "2026-07-01T09:00:00+00:00"),
            _sent("anna@example.com", "Angebot", "2026-07-08T09:00:00+00:00"),
        ],
        [],
        now=NOW,
    )
    assert len(result) == 1
    assert result[0].days_waiting == 5


def test_results_sorted_oldest_first() -> None:
    result = detect_followups(
        [
            _sent("ben@example.com", "Frage", "2026-07-07T09:00:00+00:00"),
            _sent("anna@example.com", "Angebot", "2026-07-05T09:00:00+00:00"),
        ],
        [],
        now=NOW,
    )
    assert [item.recipient for item in result] == ["anna@example.com", "ben@example.com"]
