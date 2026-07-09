"""Deterministic account-policy engine for Friday."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Iterable

from friday.app.account_policy_store import AccountPolicy


@dataclass(frozen=True)
class PolicyResolutionResult:
    """Result of resolving one write target policy."""

    ok: bool
    policy: AccountPolicy | None
    message: str
    blocked_reasons: tuple[str, ...]


def _normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _event_title(event: dict[str, Any]) -> str:
    return str(event.get("title") or event.get("summary") or "")


def _event_calendar_id(event: dict[str, Any]) -> str:
    return str(event.get("calendar_id") or event.get("calendarId") or "")


def _contains_with_word_tolerance(text: str, needle: str) -> bool:
    haystack = _normalize_text(text)
    query = _normalize_text(needle)
    if not query:
        return False
    if query in haystack:
        return True
    return re.search(rf"(^|\W){re.escape(query)}(\W|$)", haystack) is not None


def _matches_filters(event: dict[str, Any], filters: dict[str, Any]) -> bool:
    if not filters:
        return True

    title_contains = _as_list(filters.get("title_contains"))
    if title_contains and not any(
        _contains_with_word_tolerance(_event_title(event), item)
        for item in title_contains
    ):
        return False

    calendar_ids = {_normalize_text(item) for item in _as_list(filters.get("calendar_ids")) if str(item).strip()}
    if calendar_ids and _normalize_text(_event_calendar_id(event)) not in calendar_ids:
        return False

    return True


def _matches_any_exclude(event: dict[str, Any], filters: dict[str, Any]) -> bool:
    if not filters:
        return False

    title_contains = _as_list(filters.get("title_contains"))
    if title_contains and any(
        _contains_with_word_tolerance(_event_title(event), item)
        for item in title_contains
    ):
        return True

    calendar_ids = {_normalize_text(item) for item in _as_list(filters.get("calendar_ids")) if str(item).strip()}
    if calendar_ids and _normalize_text(_event_calendar_id(event)) in calendar_ids:
        return True

    return False


def filter_events(events: Iterable[dict[str, Any]], policy: AccountPolicy) -> list[dict[str, Any]]:
    """Filter events deterministically according to one account policy."""
    if not policy.enabled:
        return []
    filtered: list[dict[str, Any]] = []
    for event in events:
        if not _matches_filters(event, policy.include_filters):
            continue
        if _matches_any_exclude(event, policy.exclude_filters):
            continue
        filtered.append(dict(event))
    return filtered


def _event_date(event: dict[str, Any]) -> str:
    """Return the local calendar date for one event-like dict."""
    for key in ("date", "start", "start_time"):
        value = str(event.get(key) or "").strip()
        if not value:
            continue
        if "T" in value:
            return value.split("T", 1)[0]
        if len(value) >= 10:
            return value[:10]
    return ""


def _normalize_time(value: Any) -> str:
    """Normalize HH:MM or HH:MM:SS into HH:MM:SS for local display values."""
    text = str(value or "").strip()
    if re.fullmatch(r"\d{2}:\d{2}", text):
        return f"{text}:00"
    if re.fullmatch(r"\d{2}:\d{2}:\d{2}", text):
        return text
    return ""


def apply_transforms(events: Iterable[dict[str, Any]], policy: AccountPolicy) -> list[dict[str, Any]]:
    """Apply deterministic per-policy event transforms after filtering.

    Currently supported:
    - {"fixed_daily_window": {"start": "08:00", "end": "18:00"}}

    The transform is explicitly per policy. Events from policies without this
    setting are returned unchanged.
    """
    if policy.provider != "outlook_ics":
        return [dict(event) for event in events]

    transform = policy.transform or {}
    if not isinstance(transform, dict):
        return [dict(event) for event in events]

    fixed_window = transform.get("fixed_daily_window")
    if not isinstance(fixed_window, dict):
        return [dict(event) for event in events]

    start_time = _normalize_time(fixed_window.get("start"))
    end_time = _normalize_time(fixed_window.get("end"))
    if not start_time or not end_time:
        return [dict(event) for event in events]

    transformed: list[dict[str, Any]] = []
    for event in events:
        copied = dict(event)
        event_date = _event_date(copied)
        if not event_date:
            transformed.append(copied)
            continue
        copied["start"] = f"{event_date}T{start_time}"
        copied["end"] = f"{event_date}T{end_time}"
        copied["time_window_source"] = "policy_transform.fixed_daily_window"
        transformed.append(copied)
    return transformed


def build_ai_context(policies: Iterable[AccountPolicy]) -> str:
    """Build a compact context block from active policy notes for local AI agents."""
    lines: list[str] = []
    for policy in policies:
        if not policy.enabled or not policy.notes.strip():
            continue
        lines.append(
            f"- Konto '{policy.label}' ({policy.provider}, Rolle: {policy.role}): {policy.notes.strip()}"
        )
    if not lines:
        return "Keine aktiven Account-Policy-Notizen."
    return "Account-Policy-Kontext:\n" + "\n".join(lines)


def resolve_write_target(policies: Iterable[AccountPolicy]) -> PolicyResolutionResult:
    """Return exactly one enabled main policy as write target."""
    candidates = [
        policy for policy in policies
        if policy.enabled and policy.role == "main" and policy.access == "read_write"
    ]
    if not candidates:
        return PolicyResolutionResult(
            ok=False,
            policy=None,
            message="Kein Haupt-Kalender mit Schreibzugriff konfiguriert.",
            blocked_reasons=("main_policy_missing",),
        )
    if len(candidates) > 1:
        return PolicyResolutionResult(
            ok=False,
            policy=None,
            message="Mehr als ein Haupt-Kalender mit Schreibzugriff konfiguriert.",
            blocked_reasons=("multiple_main_policies",),
        )
    return PolicyResolutionResult(
        ok=True,
        policy=candidates[0],
        message="Haupt-Kalender gefunden.",
        blocked_reasons=(),
    )
