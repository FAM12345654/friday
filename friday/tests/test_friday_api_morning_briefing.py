"""Endpoint and scheduler tests for the nightly morning briefing."""

from __future__ import annotations

from datetime import date
import importlib.util
from pathlib import Path

from fastapi.testclient import TestClient

from friday import config
from friday.app.briefing_generator import build_briefing_status, write_briefing_status
from friday.app.morning_briefing_scheduler import MORNING_BRIEFING_JOB_ID


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_morning_briefing_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_audio_and_status_endpoints(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "MORNING_BRIEFING_AUDIO_DIR", tmp_path)
    audio = tmp_path / "briefing_2026-07-15.mp3"
    audio.write_bytes(b"ID3-test-audio")
    write_briefing_status(
        build_briefing_status(target_date=date(2026, 7, 15), success=True, audio_path=audio)
    )
    api = _load_api_module()

    with TestClient(api.app) as client:
        status_response = client.get("/morning-routine/briefing-status")
        audio_response = client.get("/morning-routine/briefing-audio")
        assert api.morning_briefing_scheduler.get_job(MORNING_BRIEFING_JOB_ID) is not None

    assert status_response.status_code == 200
    assert status_response.json()["voice_id"] == "af_heart"
    assert status_response.json()["language"] == "en-US"
    assert audio_response.status_code == 200
    assert audio_response.content == b"ID3-test-audio"


def test_audio_endpoint_returns_404_without_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "MORNING_BRIEFING_AUDIO_DIR", tmp_path)
    api = _load_api_module()

    with TestClient(api.app) as client:
        response = client.get("/morning-routine/briefing-audio")

    assert response.status_code == 404


def test_notify_ready_requires_internal_token(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "MORNING_BRIEFING_AUDIO_DIR", tmp_path)
    monkeypatch.setattr(config, "MORNING_BRIEFING_INTERNAL_TOKEN", "private-token")
    api = _load_api_module()

    with TestClient(api.app) as client:
        response = client.post("/morning-routine/notify-ready")

    assert response.status_code == 403


def test_push_token_endpoint_registers_without_returning_token(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "LOCAL_DATA_DIR", tmp_path)
    api = _load_api_module()

    with TestClient(api.app) as client:
        response = client.post(
            "/morning-routine/push-token",
            json={"expo_push_token": "ExponentPushToken[mobile-device-token]"},
        )

    assert response.status_code == 200
    assert response.json() == {"registered": True, "provider": "expo"}
    assert "mobile-device-token" not in response.text
