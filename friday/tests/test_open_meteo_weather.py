"""Hermetic tests for the opt-in Open-Meteo weather briefing."""

from __future__ import annotations

import json
from datetime import date

from friday import config
from friday.app import open_meteo_weather
from friday.app.open_meteo_weather import fetch_open_meteo_weather, weather_briefing_text


class _Response:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def _payload() -> dict:
    return {
        "daily": {
            "weather_code": [63],
            "temperature_2m_max": [24.2],
            "temperature_2m_min": [16.8],
            "precipitation_probability_max": [70],
        }
    }


def test_fetch_builds_rain_warning_in_both_languages() -> None:
    result = fetch_open_meteo_weather(
        date(2026, 7, 15),
        opener=lambda *_a, **_k: _Response(_payload()),
    )

    assert result.description_en == "rain"
    assert result.description_de == "Regen"
    assert result.rain_warning is True
    assert "70 percent" in result.to_english()
    assert "70 Prozent" in result.to_german()
    assert result.to_language("en").startswith("rain")
    assert result.to_language("de").startswith("Regen")


def test_weather_text_disabled_returns_none(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_WEATHER_BRIEFING", False)
    # Opener must never be called when the feature is off.
    def _boom(*_a, **_k):  # pragma: no cover - guard
        raise AssertionError("weather must not be fetched when disabled")

    assert weather_briefing_text(date(2026, 7, 15), "de", opener=_boom) is None


def test_weather_text_enabled_returns_german_sentence(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_WEATHER_BRIEFING", True)
    text = weather_briefing_text(
        date(2026, 7, 15), "de", opener=lambda *_a, **_k: _Response(_payload())
    )
    assert text is not None
    assert "Grad Celsius" in text


def test_weather_text_unreachable_degrades_to_none(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_WEATHER_BRIEFING", True)

    def _fail(*_a, **_k):
        raise OSError("network down")

    assert weather_briefing_text(date(2026, 7, 15), "de", opener=_fail) is None
