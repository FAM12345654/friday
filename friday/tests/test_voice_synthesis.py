"""Tests for local TTS synthesis routing (fake poster, no network)."""

from __future__ import annotations

import json

from friday.app.voice_synthesis import (
    SpeechSynthesizer,
    normalize_language,
    synthesize_for_language,
)

WAV = b"RIFF....WAVEfmt fake-audio"


def _capture_poster(captured: dict, status: int = 200, body: bytes = WAV):
    def poster(url, payload, timeout):
        captured["url"] = url
        captured["payload"] = json.loads(payload)
        captured["timeout"] = timeout
        return status, body

    return poster


def test_synthesize_posts_openai_style_payload() -> None:
    captured: dict = {}
    synthesizer = SpeechSynthesizer(
        base_url="http://localhost:5005",
        model="orpheus",
        voice="jana",
        engine="orpheus-de",
        poster=_capture_poster(captured),
    )
    result = synthesizer.synthesize("Guten Morgen!  ")
    assert result.ok
    assert result.audio == WAV
    assert result.media_type == "audio/wav"
    assert captured["url"] == "http://localhost:5005/v1/audio/speech"
    assert captured["payload"] == {
        "model": "orpheus",
        "voice": "jana",
        "input": "Guten Morgen!",
        "response_format": "wav",
    }


def test_refuses_non_local_server() -> None:
    synthesizer = SpeechSynthesizer(
        base_url="https://api.example.com",
        model="m",
        voice="v",
        engine="x",
        poster=_capture_poster({}),
    )
    result = synthesizer.synthesize("Hallo")
    assert not result.ok
    assert "localhost" in result.error


def test_empty_text_rejected_without_network() -> None:
    calls: dict = {}
    synthesizer = SpeechSynthesizer(
        base_url="http://localhost:5005",
        model="m",
        voice="v",
        engine="x",
        poster=_capture_poster(calls),
    )
    result = synthesizer.synthesize("   ")
    assert not result.ok
    assert calls == {}


def test_http_error_maps_to_message() -> None:
    synthesizer = SpeechSynthesizer(
        base_url="http://localhost:5005",
        model="m",
        voice="v",
        engine="x",
        poster=_capture_poster({}, status=503, body=b""),
    )
    result = synthesizer.synthesize("Hallo")
    assert not result.ok
    assert "503" in result.error


def test_unreachable_server_maps_to_message() -> None:
    def broken_poster(url, payload, timeout):
        raise OSError("connection refused")

    synthesizer = SpeechSynthesizer(
        base_url="http://localhost:5005",
        model="m",
        voice="v",
        engine="x",
        poster=broken_poster,
    )
    result = synthesizer.synthesize("Hallo")
    assert not result.ok
    assert "nicht erreichbar" in result.error


def test_language_routing_de_and_en() -> None:
    captured_de: dict = {}
    result_de = synthesize_for_language("Hallo", "de", poster=_capture_poster(captured_de))
    assert result_de.engine == "orpheus-de"
    assert captured_de["payload"]["voice"] == "jana"

    captured_en: dict = {}
    result_en = synthesize_for_language("Hello", "en", poster=_capture_poster(captured_en))
    assert result_en.engine == "kokoro-en"
    assert captured_en["payload"]["model"] == "kokoro"


def test_normalize_language() -> None:
    assert normalize_language("de") == "de"
    assert normalize_language("de-DE") == "de"
    assert normalize_language("en-US") == "en"
    assert normalize_language("fr") == "de"
    assert normalize_language(None) == "de"
