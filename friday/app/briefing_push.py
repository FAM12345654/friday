"""Expo push trigger for a newly rendered morning briefing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Callable
from urllib.request import Request, urlopen

from friday import config


EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
EXPO_SUCCESS_STATUS = "o" + "k"
PUSH_DEVICE_FILE = "morning_briefing_device.json"


@dataclass(frozen=True)
class BriefingPushResult:
    sent: bool
    configured: bool
    message: str
    provider: str = "expo"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _device_path() -> Path:
    return config.LOCAL_DATA_DIR / PUSH_DEVICE_FILE


def is_valid_expo_push_token(value: str) -> bool:
    token = value.strip()
    return (
        (token.startswith("ExponentPushToken[") or token.startswith("ExpoPushToken["))
        and token.endswith("]")
        and 20 <= len(token) <= 256
    )


def save_expo_push_token(token: str) -> dict[str, Any]:
    normalized = token.strip()
    if not is_valid_expo_push_token(normalized):
        raise ValueError("Invalid Expo push token.")
    path = _device_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"expo_push_token": normalized}, indent=2), encoding="utf-8")
    temporary.replace(path)
    return {"registered": True, "provider": "expo"}


def load_expo_push_token() -> str:
    path = _device_path()
    if not path.exists():
        return config.MORNING_BRIEFING_EXPO_PUSH_TOKEN
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return config.MORNING_BRIEFING_EXPO_PUSH_TOKEN
    token = str(payload.get("expo_push_token") or "").strip()
    return token if is_valid_expo_push_token(token) else config.MORNING_BRIEFING_EXPO_PUSH_TOKEN


def notify_briefing_ready(
    *,
    briefing_date: str,
    audio_url: str,
    opener: Callable[..., Any] = urlopen,
    timeout_seconds: float = 10,
) -> BriefingPushResult:
    token = load_expo_push_token()
    if not config.ENABLE_MORNING_BRIEFING_PUSH:
        return BriefingPushResult(False, False, "Morning briefing push is disabled.")
    if not token:
        return BriefingPushResult(False, False, "No Expo push token is registered yet.")

    body = json.dumps(
        {
            "to": token,
            "priority": "high",
            "_contentAvailable": True,
            "data": {
                "type": "morning_briefing_ready",
                "date": briefing_date,
                "audio_url": audio_url,
            },
        }
    ).encode("utf-8")
    request = Request(
        EXPO_PUSH_URL,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with opener(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))
    status = ((payload.get("data") or {}).get("status") if isinstance(payload, dict) else None)
    if status != EXPO_SUCCESS_STATUS:
        return BriefingPushResult(False, True, "Expo rejected the briefing-ready notification.")
    return BriefingPushResult(True, True, "Briefing-ready notification sent to Expo.")
