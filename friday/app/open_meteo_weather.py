"""Open-Meteo forecast client for the Friday morning briefing (opt-in).

Open-Meteo needs no API key, but fetching a forecast is still an external
HTTP call. It therefore stays behind ``config.ENABLE_WEATHER_BRIEFING`` and is
only queried when that flag is on. The HTTP opener is injectable so tests
never touch the network, and every failure path degrades gracefully to
``None`` so the spoken briefing simply omits the weather sentence.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from friday import config

OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# opener(request, timeout=...) -> context manager with .read(); defaults to urlopen.
Opener = Callable[..., Any]

WEATHER_CODE_DESCRIPTIONS_EN = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "freezing fog",
    51: "light drizzle",
    53: "drizzle",
    55: "heavy drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    71: "light snow",
    73: "snow",
    75: "heavy snow",
    80: "rain showers",
    81: "rain showers",
    82: "heavy rain showers",
    95: "thunderstorms",
    96: "thunderstorms with hail",
    99: "severe thunderstorms with hail",
}

WEATHER_CODE_DESCRIPTIONS_DE = {
    0: "klarer Himmel",
    1: "überwiegend klar",
    2: "teilweise bewölkt",
    3: "bedeckt",
    45: "Nebel",
    48: "gefrierender Nebel",
    51: "leichter Nieselregen",
    53: "Nieselregen",
    55: "starker Nieselregen",
    61: "leichter Regen",
    63: "Regen",
    65: "starker Regen",
    71: "leichter Schneefall",
    73: "Schneefall",
    75: "starker Schneefall",
    80: "Regenschauer",
    81: "Regenschauer",
    82: "kräftige Regenschauer",
    95: "Gewitter",
    96: "Gewitter mit Hagel",
    99: "schwere Gewitter mit Hagel",
}

_RAIN_CODES = {61, 63, 65, 80, 81, 82, 95, 96, 99}


@dataclass(frozen=True)
class WeatherBriefing:
    """One day's forecast, spoken in German (primary) or English."""

    date: str
    temperature_min_c: float
    temperature_max_c: float
    description_en: str
    description_de: str
    precipitation_probability: int
    rain_warning: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_english(self) -> str:
        text = (
            f"{self.description_en}, with temperatures between "
            f"{self.temperature_min_c:.0f} and {self.temperature_max_c:.0f} degrees Celsius"
        )
        if self.rain_warning:
            return (
                f"{text}. Rain warning: precipitation probability is "
                f"{self.precipitation_probability} percent."
            )
        return f"{text}. No significant rain warning."

    def to_german(self) -> str:
        text = (
            f"{self.description_de}, bei Temperaturen zwischen "
            f"{self.temperature_min_c:.0f} und {self.temperature_max_c:.0f} Grad Celsius"
        )
        if self.rain_warning:
            return (
                f"{text}. Regenwarnung: Die Regenwahrscheinlichkeit liegt bei "
                f"{self.precipitation_probability} Prozent."
            )
        return f"{text}. Keine nennenswerte Regenwarnung."

    def to_language(self, language: str) -> str:
        return self.to_english() if str(language).lower().startswith("en") else self.to_german()


def fetch_open_meteo_weather(
    target_date: date,
    *,
    opener: Opener = urlopen,
    timeout_seconds: float | None = None,
) -> WeatherBriefing:
    """Fetch one day's forecast. Raises on network/parse errors."""
    timeout = timeout_seconds if timeout_seconds is not None else config.WEATHER_BRIEFING_TIMEOUT_SECONDS
    query = urlencode(
        {
            "latitude": config.OPEN_METEO_LATITUDE,
            "longitude": config.OPEN_METEO_LONGITUDE,
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max"
            ),
            "timezone": config.WEATHER_BRIEFING_TIMEZONE,
            "start_date": target_date.isoformat(),
            "end_date": target_date.isoformat(),
        }
    )
    request = Request(
        f"{OPEN_METEO_FORECAST_URL}?{query}", headers={"User-Agent": "Friday/1.0"}
    )
    with opener(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))

    daily = payload.get("daily") or {}
    weather_code = int((daily.get("weather_code") or [-1])[0])
    precipitation = int(round(float((daily.get("precipitation_probability_max") or [0])[0] or 0)))
    return WeatherBriefing(
        date=target_date.isoformat(),
        temperature_min_c=float((daily.get("temperature_2m_min") or [0])[0]),
        temperature_max_c=float((daily.get("temperature_2m_max") or [0])[0]),
        description_en=WEATHER_CODE_DESCRIPTIONS_EN.get(weather_code, "mixed weather conditions"),
        description_de=WEATHER_CODE_DESCRIPTIONS_DE.get(weather_code, "wechselhaftes Wetter"),
        precipitation_probability=precipitation,
        rain_warning=precipitation >= 40 or weather_code in _RAIN_CODES,
    )


def weather_briefing_text(
    target_date: date,
    language: str = "de",
    *,
    opener: Opener = urlopen,
    timeout_seconds: float | None = None,
) -> str | None:
    """Spoken weather sentence for the briefing, or ``None`` when unavailable.

    Returns ``None`` when the feature is disabled or the forecast cannot be
    fetched, so the caller can silently drop the weather sentence.
    """
    if not getattr(config, "ENABLE_WEATHER_BRIEFING", False):
        return None
    try:
        briefing = fetch_open_meteo_weather(
            target_date, opener=opener, timeout_seconds=timeout_seconds
        )
    except Exception:
        # Degrade gracefully: no weather sentence, no user-facing error.
        return None
    return briefing.to_language(language)
