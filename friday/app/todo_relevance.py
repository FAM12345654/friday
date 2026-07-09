"""Deterministic local relevance rules for task suggestions."""

from __future__ import annotations

import re
from typing import Any, Mapping


USER_TRIGGER_WORDS = {"philip", "phips", "ph", "zeitler"}
PARTNER_TRIGGER_WORDS = {
    "philip": {"philip", "phips", "ph", "zeitler"},
    "alex": {"alex"},
    "flo": {"flo", "florian"},
}
SHARED_MAILBOX_IDENTIFIERS = {"office@familienhelden.at", "office_familienhelden_at"}
PERSONAL_MAILBOX_IDENTIFIERS = {"philip@familienhelden.at", "philip_familienhelden_at"}
_TOKEN_RE = re.compile(r"[0-9A-Za-zÄÖÜäöüß]+")


def _text_tokens(text: str) -> set[str]:
    """Return case-insensitive word tokens from local text."""
    return {match.group(0).casefold() for match in _TOKEN_RE.finditer(text or "")}


def is_relevant_for_user(
    *,
    text: str,
    sender_contact: Mapping[str, Any] | None = None,
) -> bool:
    """Return whether a task-like message should become a Friday task.

    This intentionally stays deterministic and local. A task-like message is
    relevant when it explicitly mentions Philip/Phips/PH/Zeitler as a whole
    word, or when the known sender contact is a customer assigned to Philip.
    """

    if sender_contact:
        betreuer = str(sender_contact.get("betreuer") or "").strip().casefold()
        if betreuer == "philip":
            return True

    return bool(USER_TRIGGER_WORDS.intersection(_text_tokens(text)))


def _recipient_text(recipients: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None) -> str:
    parts: list[str] = []
    for item in recipients or ():
        if not isinstance(item, Mapping):
            continue
        parts.append(str(item.get("name") or ""))
        parts.append(str(item.get("address") or ""))
        parts.append(str(item.get("label") or ""))
    return " ".join(parts)


def _mailbox_tokens(value: str | None) -> set[str]:
    lowered = str(value or "").strip().casefold()
    return {lowered, lowered.replace("@", "_").replace(".", "_")}


def _is_shared_mailbox(account: str | None) -> bool:
    tokens = _mailbox_tokens(account)
    return bool(tokens.intersection(SHARED_MAILBOX_IDENTIFIERS))


def _is_personal_mailbox(account: str | None) -> bool:
    tokens = _mailbox_tokens(account)
    return bool(tokens.intersection(PERSONAL_MAILBOX_IDENTIFIERS))


def _mentions_all_partners(tokens: set[str]) -> bool:
    return all(bool(words.intersection(tokens)) for words in PARTNER_TRIGGER_WORDS.values())


def determine_mail_relevance(
    *,
    account: str | None,
    subject: str | None,
    snippet: str | None,
    sender: str | None,
    recipients: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    sender_contact: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return deterministic local relevance for Microsoft mail previews.

    Shared office mailboxes show only messages relevant to Philip by default.
    Personal mailboxes remain fully visible.
    """
    account_text = str(account or "").strip()
    if _is_personal_mailbox(account_text) or not _is_shared_mailbox(account_text):
        return {
            "relevant": True,
            "reason": "personal_mailbox",
        }

    combined = " ".join(
        [
            str(subject or ""),
            str(snippet or ""),
            str(sender or ""),
            _recipient_text(recipients),
        ]
    )
    tokens = _text_tokens(combined)
    if _mentions_all_partners(tokens):
        return {
            "relevant": True,
            "reason": "team_all_partners",
        }
    if USER_TRIGGER_WORDS.intersection(tokens):
        return {
            "relevant": True,
            "reason": "philip_trigger",
        }
    if sender_contact:
        betreuer = str(sender_contact.get("betreuer") or "").strip().casefold()
        if betreuer == "philip":
            return {
                "relevant": True,
                "reason": "customer_betreuer_philip",
            }
    return {
        "relevant": False,
        "reason": "office_not_relevant",
    }


def is_mail_relevant(
    *,
    account: str | None,
    subject: str | None,
    snippet: str | None,
    sender: str | None,
    recipients: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    sender_contact: Mapping[str, Any] | None = None,
) -> bool:
    """Return whether a mail preview should be visible in the default view."""
    return bool(
        determine_mail_relevance(
            account=account,
            subject=subject,
            snippet=snippet,
            sender=sender,
            recipients=recipients,
            sender_contact=sender_contact,
        )["relevant"]
    )
