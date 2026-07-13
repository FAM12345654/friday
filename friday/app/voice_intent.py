"""Parse transcribed voice commands into structured intents.

Deterministic pattern matching over German and English phrasings — no LLM
required, so push-to-talk works even when local AI is off. The parser is
pure (no I/O); executing an intent against the agents happens in the API.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Iterable, Mapping

INTENTS = (
    "briefing",
    "create_task",
    "complete_task",
    "snooze_task",
    "search",
    "calendar_today",
    "unknown",
)

_FILLER_PREFIX = re.compile(
    r"^(hey friday|friday|ok friday|okay friday|bitte|please|hallo|hi)[,!.\s]+",
    re.IGNORECASE,
)

# Ordered: first match wins. Each entry: (intent, language, compiled pattern).
# Argument-capturing patterns use the named group "arg".
_PATTERNS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    # --- briefing / today's overview -------------------------------------
    ("briefing", "de", re.compile(r"\b(briefing|tagesübersicht|was steht heute an|wie sieht mein tag aus|guten morgen)\b", re.IGNORECASE)),
    ("briefing", "de", re.compile(r"\b(meine|welche) aufgaben\b", re.IGNORECASE)),
    ("briefing", "en", re.compile(r"\b(briefing|what's on today|whats on today|my tasks for today|good morning|what do i have today)\b", re.IGNORECASE)),
    # --- calendar ---------------------------------------------------------
    ("calendar_today", "de", re.compile(r"\b(welche termine|meine termine|termine heute|kalender)\b", re.IGNORECASE)),
    ("calendar_today", "en", re.compile(r"\b(my (appointments|meetings|events)|calendar|appointments today)\b", re.IGNORECASE)),
    # --- snooze (before complete: "verschiebe" must not match "erledige").
    # "snooze" itself is language-neutral, so both patterns accept the
    # time words of both languages.
    ("snooze_task", "de", re.compile(r"\b(?:verschiebe|schiebe|verlege|snooze)\s+(?:die\s+aufgabe\s+)?(?P<arg>.+?)(?:\s+(?:auf|bis|to|until)\s+(?P<when>morgen|übermorgen|nächste woche|tomorrow|next week))?$", re.IGNORECASE)),
    ("snooze_task", "en", re.compile(r"\b(?:postpone|push)\s+(?:the\s+task\s+)?(?P<arg>.+?)(?:\s+(?:to|until)\s+(?P<when>tomorrow|next week))?$", re.IGNORECASE)),
    # --- complete ----------------------------------------------------------
    ("complete_task", "de", re.compile(r"\b(?:erledige|hake|schließe)\s+(?:die\s+aufgabe\s+)?(?P<arg>.+?)(?:\s+ab)?$", re.IGNORECASE)),
    ("complete_task", "de", re.compile(r"\b(?P<arg>.+?)\s+(?:ist|wurde)\s+erledigt\b", re.IGNORECASE)),
    ("complete_task", "en", re.compile(r"\b(?:complete|finish|check off|mark)\s+(?:the\s+task\s+)?(?P<arg>.+?)(?:\s+(?:as\s+)?done)?$", re.IGNORECASE)),
    # --- create ------------------------------------------------------------
    ("create_task", "de", re.compile(r"\b(?:erstelle|neue|erinnere mich an|notiere)\s+(?:eine\s+)?(?:aufgabe[:\s]+)?(?P<arg>.+)$", re.IGNORECASE)),
    ("create_task", "en", re.compile(r"\b(?:create|add|new|remind me to|note)\s+(?:a\s+)?(?:task[:\s]+)?(?P<arg>.+)$", re.IGNORECASE)),
    # --- search ------------------------------------------------------------
    ("search", "de", re.compile(r"\b(?:suche?|finde)\s+(?:nach\s+)?(?P<arg>.+)$", re.IGNORECASE)),
    ("search", "en", re.compile(r"\b(?:search|find|look)\s+(?:for\s+)?(?P<arg>.+)$", re.IGNORECASE)),
)

_WHEN_OFFSETS = {
    "morgen": 1,
    "tomorrow": 1,
    "übermorgen": 2,
    "nächste woche": 7,
    "next week": 7,
}


@dataclass(frozen=True)
class VoiceIntent:
    """One parsed voice command."""

    intent: str
    argument: str
    language: str
    snooze_until: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent": self.intent,
            "argument": self.argument,
            "language": self.language,
            "snooze_until": self.snooze_until,
        }


def _clean(text: str) -> str:
    cleaned = " ".join(str(text or "").split()).strip().strip(".!?")
    return _FILLER_PREFIX.sub("", cleaned).strip()


def parse_voice_command(text: str, today: str | None = None) -> VoiceIntent:
    """Map one transcribed sentence to an intent (German or English)."""
    cleaned = _clean(text)
    if not cleaned:
        return VoiceIntent(intent="unknown", argument="", language="de")

    effective_today = date.fromisoformat(today) if today else date.today()

    for intent, language, pattern in _PATTERNS:
        match = pattern.search(cleaned)
        if not match:
            continue
        argument = (match.groupdict().get("arg") or "").strip().strip(".!?")
        snooze_until: str | None = None
        if intent == "snooze_task":
            when = str(match.groupdict().get("when") or "").lower()
            offset = _WHEN_OFFSETS.get(when, 1)  # kein Zeitwort -> morgen
            snooze_until = (effective_today + timedelta(days=offset)).isoformat()
        return VoiceIntent(
            intent=intent,
            argument=argument,
            language=language,
            snooze_until=snooze_until,
        )

    return VoiceIntent(intent="unknown", argument=cleaned, language="de")


def match_task_by_title(
    tasks: Iterable[Mapping[str, Any]],
    spoken_title: str,
    *,
    min_ratio: float = 0.55,
) -> Mapping[str, Any] | None:
    """Find the open task that best matches a spoken title (fuzzy)."""
    target = " ".join(str(spoken_title or "").split()).casefold()
    if not target:
        return None

    best: Mapping[str, Any] | None = None
    best_score = 0.0
    for task in tasks:
        title = str(task.get("title") or "").casefold()
        if not title:
            continue
        if target in title or title in target:
            score = 1.0
        else:
            score = difflib.SequenceMatcher(None, target, title).ratio()
        if score > best_score:
            best_score = score
            best = task
    return best if best_score >= min_ratio else None
