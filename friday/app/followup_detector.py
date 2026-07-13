"""Detect sent emails that are still waiting for a reply.

Pure logic: callers pass already-loaded rows from ``email_send_log`` and the
synced inbox (``ms_mail_messages``). A sent email counts as "waiting" when it
was sent successfully at least ``threshold_days`` ago and no inbound message
from the same address arrived after the send.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

DEFAULT_THRESHOLD_DAYS = 3
MAX_AGE_DAYS = 30

_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


@dataclass(frozen=True)
class FollowUpCandidate:
    """One sent email without a reply."""

    recipient: str
    subject: str
    sent_at: str
    days_waiting: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "recipient": self.recipient,
            "subject": self.subject,
            "sent_at": self.sent_at,
            "days_waiting": self.days_waiting,
            "suggestion": (
                f"Keine Antwort von {self.recipient} seit {self.days_waiting} Tagen"
                f" auf „{self.subject}“."
            ),
        }


def extract_email_address(value: Any) -> str:
    """Pull the bare address out of e.g. 'Anna <anna@example.com>'."""
    match = _EMAIL_PATTERN.search(str(value or ""))
    return match.group(0).lower() if match else ""


def _parse_timestamp(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def detect_followups(
    sent_emails: Iterable[Mapping[str, Any]],
    inbound_messages: Iterable[Mapping[str, Any]],
    *,
    now: datetime | None = None,
    threshold_days: int = DEFAULT_THRESHOLD_DAYS,
    max_age_days: int = MAX_AGE_DAYS,
) -> list[FollowUpCandidate]:
    """Return sent emails still waiting for a reply, oldest first."""
    reference = now or datetime.now(timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    threshold = max(1, int(threshold_days))
    max_age = max(threshold, int(max_age_days))

    # Latest inbound timestamp per sender address.
    latest_inbound: dict[str, datetime] = {}
    for row in inbound_messages:
        address = extract_email_address(row.get("sender"))
        received = _parse_timestamp(row.get("received_at"))
        if not address or received is None:
            continue
        current = latest_inbound.get(address)
        if current is None or received > current:
            latest_inbound[address] = received

    # Latest successful send per (recipient, subject).
    latest_sent: dict[tuple[str, str], tuple[datetime, str, str]] = {}
    for row in sent_emails:
        if str(row.get("status") or "").strip().lower() != "sent":
            continue
        recipient = extract_email_address(row.get("recipient"))
        sent_at = _parse_timestamp(row.get("sent_at"))
        if not recipient or sent_at is None:
            continue
        subject = " ".join(str(row.get("subject") or "").split()) or "(ohne Betreff)"
        key = (recipient, subject.casefold())
        current = latest_sent.get(key)
        if current is None or sent_at > current[0]:
            latest_sent[key] = (sent_at, recipient, subject)

    candidates: list[FollowUpCandidate] = []
    for sent_at, recipient, subject in latest_sent.values():
        age_days = (reference - sent_at).days
        if age_days < threshold or age_days > max_age:
            continue
        reply = latest_inbound.get(recipient)
        if reply is not None and reply > sent_at:
            continue
        candidates.append(
            FollowUpCandidate(
                recipient=recipient,
                subject=subject,
                sent_at=sent_at.isoformat(),
                days_waiting=age_days,
            )
        )

    candidates.sort(key=lambda item: (item.sent_at, item.recipient))
    return candidates
