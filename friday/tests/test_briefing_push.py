"""Tests for the guarded Expo briefing-ready push trigger."""

from __future__ import annotations

import json

from friday import config
from friday.app.briefing_push import load_expo_push_token, notify_briefing_ready, save_expo_push_token


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps({"data": {"status": "ok"}}).encode("utf-8")


def test_push_waits_for_registered_expo_token(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_MORNING_BRIEFING_PUSH", True)
    monkeypatch.setattr(config, "MORNING_BRIEFING_EXPO_PUSH_TOKEN", "")

    result = notify_briefing_ready(briefing_date="2026-07-15", audio_url="/audio")

    assert result.sent is False
    assert result.configured is False


def test_push_sends_silent_data_to_expo_when_configured(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_MORNING_BRIEFING_PUSH", True)
    monkeypatch.setattr(config, "MORNING_BRIEFING_EXPO_PUSH_TOKEN", "ExponentPushToken[test]")
    captured = {}

    def _open(request, **_kwargs):
        captured.update(json.loads(request.data.decode("utf-8")))
        return _Response()

    result = notify_briefing_ready(
        briefing_date="2026-07-15",
        audio_url="/morning-routine/briefing-audio",
        opener=_open,
    )

    assert result.sent is True
    assert captured["_contentAvailable"] is True
    assert captured["data"]["type"] == "morning_briefing_ready"


def test_push_token_store_keeps_one_valid_device(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "LOCAL_DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "MORNING_BRIEFING_EXPO_PUSH_TOKEN", "")

    result = save_expo_push_token("ExponentPushToken[first-device]")
    save_expo_push_token("ExpoPushToken[replacement-device]")

    assert result["registered"] is True
    assert load_expo_push_token() == "ExpoPushToken[replacement-device]"
    assert len(list(tmp_path.glob("morning_briefing_device.json"))) == 1
