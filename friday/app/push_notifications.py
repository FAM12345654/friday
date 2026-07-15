"""Expo push notifications for Friday (opt-in).

Device tokens are stored locally. Actually sending goes through Expo's push
service (``https://exp.host``) and is therefore an external call — it stays
disabled unless ``config.ENABLE_PUSH_NOTIFICATIONS`` is True. The HTTP
poster is injectable so tests never touch the network.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from friday import config
from friday.storage.database import get_connection, setup_local_database

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
EXPO_TOKEN_PATTERN = re.compile(r"^(ExponentPushToken|ExpoPushToken)\[[A-Za-z0-9_-]+\]$")
MAX_BATCH = 100

# poster(url, payload_bytes, timeout_seconds) -> (status_code, response_body)
Poster = Callable[[str, bytes, int], tuple[int, bytes]]


@dataclass(frozen=True)
class PushSendResult:
    ok: bool
    sent: int
    message: str
    external_call_used: bool


def is_valid_expo_token(token: str) -> bool:
    return bool(EXPO_TOKEN_PATTERN.match(str(token or "").strip()))


def register_push_token(
    token: str,
    platform: str = "unknown",
    *,
    db_path: Path | str | None = None,
) -> bool:
    """Store one device token locally. Returns False for invalid tokens."""
    cleaned = str(token or "").strip()
    if not is_valid_expo_token(cleaned):
        return False
    setup_local_database(db_path)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO push_tokens (token, platform, created_at)
            VALUES (:token, :platform, :created_at)
            ON CONFLICT (token) DO UPDATE SET platform = excluded.platform
            """,
            {
                "token": cleaned,
                "platform": str(platform or "unknown").strip().lower() or "unknown",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
    return True


def remove_push_token(token: str, *, db_path: Path | str | None = None) -> bool:
    setup_local_database(db_path)
    with get_connection(db_path) as connection:
        result = connection.execute(
            "DELETE FROM push_tokens WHERE token = :token",
            {"token": str(token or "").strip()},
        )
        return result.rowcount > 0


def list_push_tokens(*, db_path: Path | str | None = None) -> list[dict[str, Any]]:
    setup_local_database(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            "SELECT id, token, platform, created_at FROM push_tokens ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]


def build_due_task_notifications(
    tasks: Iterable[Mapping[str, Any]],
    today_iso: str,
) -> list[dict[str, str]]:
    """Build notification payloads for tasks due today or overdue."""
    due_today: list[str] = []
    overdue: list[str] = []
    for task in tasks:
        status = str(task.get("status") or "").lower()
        if status in {"done", "archived"}:
            continue
        snoozed_until = str(task.get("snoozed_until") or "").strip()
        if snoozed_until and snoozed_until > today_iso:
            continue
        due = str(task.get("due_date") or "").strip()
        if not due:
            continue
        title = str(task.get("title") or "Aufgabe").strip()
        if due == today_iso:
            due_today.append(title)
        elif due < today_iso:
            overdue.append(title)

    notifications: list[dict[str, str]] = []
    if due_today:
        notifications.append(
            {
                "title": f"Friday: {len(due_today)} Aufgabe(n) heute fällig",
                "body": ", ".join(due_today[:5]),
            }
        )
    if overdue:
        notifications.append(
            {
                "title": f"Friday: {len(overdue)} überfällige Aufgabe(n)",
                "body": ", ".join(overdue[:5]),
            }
        )
    return notifications


def _default_poster(url: str, payload: bytes, timeout_seconds: int) -> tuple[int, bytes]:
    from urllib import error, request

    req = request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            return response.status, response.read()
    except error.HTTPError as exc:
        return exc.code, exc.read()


def build_expo_push_messages(
    notifications: Iterable[Mapping[str, str]],
    recipient_tokens: Iterable[str],
) -> list[dict[str, str]]:
    """Build the exact, bounded Expo request vector from approved inputs."""
    items = [dict(item) for item in notifications if str(item.get("title") or "").strip()]
    tokens = [str(token).strip() for token in recipient_tokens if is_valid_expo_token(str(token))]
    return [
        {
            "to": token,
            "title": str(item["title"]),
            "body": str(item.get("body", "")),
            "sound": "default",
        }
        for item in items
        for token in tokens
    ][:MAX_BATCH]


def send_push_notifications(
    notifications: Iterable[Mapping[str, str]],
    *,
    db_path: Path | str | None = None,
    recipient_tokens: Iterable[str] | None = None,
    poster: Poster | None = None,
    timeout_seconds: int = 10,
) -> PushSendResult:
    """Send notifications to all registered devices via Expo push."""
    if not getattr(config, "ENABLE_PUSH_NOTIFICATIONS", False):
        return PushSendResult(
            ok=False,
            sent=0,
            message="Push-Benachrichtigungen sind deaktiviert (ENABLE_PUSH_NOTIFICATIONS).",
            external_call_used=False,
        )

    items = [dict(item) for item in notifications if str(item.get("title") or "").strip()]
    tokens = (
        [str(token) for token in recipient_tokens]
        if recipient_tokens is not None
        else [row["token"] for row in list_push_tokens(db_path=db_path)]
    )
    messages = build_expo_push_messages(items, tokens)
    if not messages:
        return PushSendResult(
            ok=True,
            sent=0,
            message="Nichts zu senden (keine Nachrichten oder keine Geräte).",
            external_call_used=False,
        )

    active_poster = poster or _default_poster
    status, _body = active_poster(
        EXPO_PUSH_URL, json.dumps(messages).encode("utf-8"), timeout_seconds
    )
    if 200 <= status < 300:
        return PushSendResult(
            ok=True,
            sent=len(messages),
            message=f"{len(messages)} Push-Nachricht(en) an Expo übergeben.",
            external_call_used=True,
        )
    return PushSendResult(
        ok=False,
        sent=0,
        message=f"Expo-Push fehlgeschlagen (HTTP {status}).",
        external_call_used=True,
    )
