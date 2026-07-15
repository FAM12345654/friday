"""Deterministic planning helpers for copying source events into Google."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable


SOURCE_KEY_PROPERTY = "fridaySourceKey"
SOURCE_POLICY_PROPERTY = "fridaySourcePolicyId"
SOURCE_PROVIDER_PROPERTY = "fridaySourceProvider"
MANAGED_PROPERTY = "fridayManaged"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _event_signature(event: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        _text(event.get("title")).casefold(),
        _text(event.get("start")),
        _text(event.get("end")),
        _text(event.get("location")).casefold(),
    )


def build_source_key(event: dict[str, Any]) -> str:
    """Build a stable, non-sensitive key for one transformed source event."""
    raw = event.get("raw") if isinstance(event.get("raw"), dict) else {}
    identity = {
        "policy_id": _text(event.get("policy_id") or raw.get("policy_id")),
        "provider": _text(event.get("provider") or raw.get("source")),
        "source_id": _text(event.get("id") or raw.get("uid")),
        "start": _text(event.get("start")),
        "end": _text(event.get("end")),
    }
    if not identity["source_id"]:
        identity["source_id"] = "|".join(_event_signature(event))
    payload = json.dumps(identity, ensure_ascii=True, sort_keys=True).encode("utf-8")
    return f"friday-source-v1-{hashlib.sha256(payload).hexdigest()}"


def read_google_source_key(event: dict[str, Any]) -> str:
    """Read Friday's private source key from one Google event payload."""
    raw = event.get("raw") if isinstance(event.get("raw"), dict) else {}
    properties = raw.get("extendedProperties")
    if not isinstance(properties, dict):
        return ""
    private = properties.get("private")
    if not isinstance(private, dict):
        return ""
    return _text(private.get(SOURCE_KEY_PROPERTY))


def build_source_sync_plan(
    source_events: Iterable[dict[str, Any]],
    google_events: Iterable[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Split source events into create and skipped lists without side effects."""
    google_items = [dict(event) for event in google_events]
    existing_keys = {key for event in google_items if (key := read_google_source_key(event))}
    existing_signatures = {_event_signature(event) for event in google_items}
    planned_keys: set[str] = set()
    create: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for source in source_events:
        event = dict(source)
        source_key = build_source_key(event)
        reason = ""
        if source_key in existing_keys:
            reason = "already_synced"
        elif _event_signature(event) in existing_signatures:
            reason = "matching_google_event_exists"
        elif source_key in planned_keys:
            reason = "duplicate_source_event"

        item = {
            "source_key": source_key,
            "policy_id": event.get("policy_id"),
            "source": event.get("policy_label") or event.get("provider"),
            "title": event.get("title"),
            "start": event.get("start"),
            "end": event.get("end"),
            "location": event.get("location"),
        }
        if reason:
            skipped.append({**item, "reason": reason})
            continue
        planned_keys.add(source_key)
        create.append({**item, "event": event})

    return {"create": create, "skipped": skipped}


def build_google_sync_metadata(item: dict[str, Any]) -> dict[str, Any]:
    """Build private Google metadata without copying source secrets."""
    event = item.get("event") if isinstance(item.get("event"), dict) else {}
    return {
        "description": f"Mit Friday aus {item.get('source') or 'Kalenderquelle'} synchronisiert.",
        "extendedProperties": {
            "private": {
                SOURCE_KEY_PROPERTY: _text(item.get("source_key")),
                SOURCE_POLICY_PROPERTY: _text(event.get("policy_id")),
                SOURCE_PROVIDER_PROPERTY: _text(event.get("provider")),
                MANAGED_PROPERTY: "true",
            }
        },
    }


def build_google_sync_event_id(item: dict[str, Any]) -> str:
    """Build a Google-compatible deterministic ID to make source creates idempotent."""
    source_key = _text(item.get("source_key"))
    digest = hashlib.sha256(source_key.encode("utf-8")).hexdigest()
    return f"frd{digest}"


def public_sync_item(item: dict[str, Any]) -> dict[str, Any]:
    """Remove internal event payloads before returning a sync item to clients."""
    return {key: value for key, value in item.items() if key != "event"}
