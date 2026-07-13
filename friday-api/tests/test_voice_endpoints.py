"""Endpoint tests for the voice API (fake STT/TTS, no models, no network)."""

from __future__ import annotations

import base64

import pytest
from fastapi.testclient import TestClient

import main
from friday.app import voice_synthesis, voice_transcription
from friday.app.voice_synthesis import SynthesisResult
from friday.app.voice_transcription import TranscriptionResult

WAV = b"RIFF-fake-wav-bytes"


class FakeTranscriber:
    def __init__(self, text: str = "Was steht heute an?", language: str = "de") -> None:
        self.text = text
        self.language = language

    def transcribe(self, path) -> TranscriptionResult:
        return TranscriptionResult(
            ok=True, text=self.text, language=self.language, duration_seconds=1.2
        )


class FailingTranscriber:
    def transcribe(self, path) -> TranscriptionResult:
        return TranscriptionResult(
            ok=False, text="", language="", duration_seconds=0.0,
            error="faster-whisper ist nicht installiert. requirements-voice",
        )


def _fake_tts_ok(text, language, poster=None):
    return SynthesisResult(ok=True, audio=WAV, media_type="audio/wav", engine=f"fake-{language}")


def _fake_tts_down(text, language, poster=None):
    return SynthesisResult(ok=False, audio=b"", media_type="", engine="fake", error="TTS-Server nicht erreichbar")


@pytest.fixture()
def client():
    with TestClient(main.app) as test_client:
        yield test_client


def test_voice_status_shape(client) -> None:
    data = client.get("/api/voice/status").json()["data"]
    assert set(data) == {"stt_available", "stt_model", "tts_de", "tts_en"}
    assert data["tts_de"]["voice"]


def test_transcribe_endpoint(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_transcription, "get_default_transcriber", lambda: FakeTranscriber())
    response = client.post(
        "/api/voice/transcribe",
        files={"audio": ("speech.m4a", b"fake-bytes", "audio/m4a")},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["text"] == "Was steht heute an?"
    assert data["language"] == "de"


def test_transcribe_unavailable_maps_to_503(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_transcription, "get_default_transcriber", lambda: FailingTranscriber())
    response = client.post(
        "/api/voice/transcribe",
        files={"audio": ("speech.m4a", b"fake-bytes", "audio/m4a")},
    )
    assert response.status_code == 503
    assert "requirements-voice" in response.json()["detail"]


def test_transcribe_rejects_empty_upload(client) -> None:
    response = client.post(
        "/api/voice/transcribe",
        files={"audio": ("speech.m4a", b"", "audio/m4a")},
    )
    assert response.status_code == 400


def test_speak_returns_wav(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_synthesis, "synthesize_for_language", _fake_tts_ok)
    response = client.post("/api/voice/speak", json={"text": "Hallo", "language": "de"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("audio/wav")
    assert response.content == WAV


def test_speak_maps_tts_failure_to_502(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_synthesis, "synthesize_for_language", _fake_tts_down)
    response = client.post("/api/voice/speak", json={"text": "Hallo"})
    assert response.status_code == 502


def test_command_task_lifecycle_with_speech(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_synthesis, "synthesize_for_language", _fake_tts_ok)

    created = client.post(
        "/api/voice/command",
        json={"text": "Erstelle Aufgabe: Voice-Test-Aufgabe", "speak": True},
    ).json()["data"]
    assert created["intent"]["intent"] == "create_task"
    assert "Voice-Test-Aufgabe" in created["reply_text"]
    assert base64.b64decode(created["audio_base64"]) == WAV
    assert created["tts_error"] is None
    task_id = created["data"]["task"]["id"]

    try:
        done = client.post(
            "/api/voice/command",
            json={"text": "Voice-Test-Aufgabe ist erledigt"},
        ).json()["data"]
        assert done["intent"]["intent"] == "complete_task"
        assert "erledigt" in done["reply_text"]
    finally:
        client.delete(f"/api/tasks/{task_id}")


def test_command_survives_tts_outage(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_synthesis, "synthesize_for_language", _fake_tts_down)
    data = client.post(
        "/api/voice/command",
        json={"text": "blubb-unbekannt", "speak": True},
    ).json()["data"]
    assert data["reply_text"]
    assert data["audio_base64"] is None
    assert "nicht erreichbar" in data["tts_error"]


def test_command_audio_full_pipeline(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(voice_transcription, "get_default_transcriber", lambda: FakeTranscriber())
    monkeypatch.setattr(voice_synthesis, "synthesize_for_language", _fake_tts_ok)
    response = client.post(
        "/api/voice/command-audio",
        files={"audio": ("speech.m4a", b"fake-bytes", "audio/m4a")},
    )
    data = response.json()["data"]
    assert data["transcription"]["text"] == "Was steht heute an?"
    assert data["intent"]["intent"] == "briefing"
    assert data["reply_text"].startswith("Guten Morgen")
    assert base64.b64decode(data["audio_base64"]) == WAV


def test_morning_briefing_endpoint(client, monkeypatch: pytest.MonkeyPatch) -> None:
    plain = client.get("/api/voice/morning-briefing").json()["data"]
    assert plain["language"] == "de"
    assert plain["text"].startswith("Guten Morgen")
    assert "audio_base64" not in plain

    monkeypatch.setattr(voice_synthesis, "synthesize_for_language", _fake_tts_ok)
    spoken = client.get(
        "/api/voice/morning-briefing", params={"language": "en", "speak": "true"}
    ).json()["data"]
    assert spoken["text"].startswith("Good morning")
    assert base64.b64decode(spoken["audio_base64"]) == WAV
