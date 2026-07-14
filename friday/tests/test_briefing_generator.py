"""Tests for nightly English briefing generation and atomic MP3 replacement."""

from __future__ import annotations

from datetime import date
import json

import numpy as np

from friday import config
from friday.app.briefing_generator import generate_briefing_script, render_briefing_audio
from friday.app.open_meteo_weather import WeatherBriefing, fetch_open_meteo_weather


class _FakePipeline:
    def __init__(self, expected_voice: str) -> None:
        self.expected_voice = expected_voice

    def __call__(self, text, *, voice, speed, split_pattern):
        assert text.startswith("Good morning.")
        assert voice == self.expected_voice
        assert speed == 1
        assert split_pattern == r"\n+"
        return iter([("Good morning", "phonemes", np.zeros(2400, dtype=np.float32))])


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_generate_briefing_script_is_english_and_ordered() -> None:
    script = generate_briefing_script(
        date(2026, 7, 15),
        tasks=[{"title": "Prepare customer proposal"}, {"title": "Call the project team"}],
        appointments=[
            {"title": "Lunch", "start": "2026-07-15T12:00:00+02:00"},
            {"title": "Team meeting", "start": "2026-07-15T09:00:00+02:00"},
        ],
        weather=WeatherBriefing("2026-07-15", 17, 25, "partly cloudy", 55, True),
    )

    assert script.startswith("Good morning. Here are your most important tasks today:")
    assert script.index("Team meeting") < script.index("Lunch")
    assert "The weather:" in script
    assert "Rain warning" in script


def test_render_replaces_old_audio_and_keeps_exactly_one_file(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "MORNING_BRIEFING_AUDIO_DIR", tmp_path)
    old = tmp_path / "briefing_2026-07-14.mp3"
    old.write_bytes(b"old")

    result = render_briefing_audio(
        "Good morning. This is Friday.",
        date(2026, 7, 15),
        pipeline_factory=lambda lang_code: _FakePipeline(config.MORNING_BRIEFING_VOICE),
    )

    assert result.exists()
    assert result.stat().st_size > 0
    assert list(tmp_path.glob("briefing_*.mp3")) == [result]


def test_render_failure_preserves_previous_audio(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "MORNING_BRIEFING_AUDIO_DIR", tmp_path)
    old = tmp_path / "briefing_2026-07-14.mp3"
    old.write_bytes(b"old")

    def _failed_pipeline(_lang_code):
        raise RuntimeError("model unavailable")

    try:
        render_briefing_audio(
            "Good morning.",
            date(2026, 7, 15),
            pipeline_factory=_failed_pipeline,
        )
    except RuntimeError:
        pass
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("Rendering was expected to fail.")

    assert old.read_bytes() == b"old"
    assert list(tmp_path.glob("briefing_*.mp3")) == [old]


def test_open_meteo_weather_builds_rain_warning() -> None:
    payload = {
        "daily": {
            "weather_code": [63],
            "temperature_2m_max": [24.2],
            "temperature_2m_min": [16.8],
            "precipitation_probability_max": [70],
        }
    }

    result = fetch_open_meteo_weather(
        date(2026, 7, 15),
        opener=lambda *_args, **_kwargs: _Response(payload),
    )

    assert result.description == "rain"
    assert result.rain_warning is True
    assert "70 percent" in result.to_english()
