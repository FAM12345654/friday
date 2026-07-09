"""Deterministic local relevance rules for task suggestions."""

from __future__ import annotations

import re
from typing import Any, Mapping


USER_TRIGGER_WORDS = {"philip", "phips", "ph", "zeitler"}
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
