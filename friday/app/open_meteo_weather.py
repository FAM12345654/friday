"""Small Open-Meteo forecast client for the English morning briefing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import json
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from friday import config


OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODE_DESCRIPTIONS = {
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


@dataclass(frozen=True)
class WeatherBriefing:
    date: str
    temperature_min_c: float
    temperature_max_c: float
    description: str
    precipitation_probability: int
    rain_warning: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_english(self) -> str:
        text = (
            f"{self.description}, with temperatures between "
            f"{self.temperature_min_c:.0f} and {self.temperature_max_c:.0f} degrees Celsius"
        )
        if self.rain_warning:
            return f"{text}. Rain warning: precipitation probability is {self.precipitation_probability} percent."
        return f"{text}. No significant rain warning."


def fetch_open_meteo_weather(
    target_date: date,
    *,
    opener: Callable[..., Any] = urlopen,
    timeout_seconds: float = 10,
) -> WeatherBriefing:
    query = urlencode(
        {
            "latitude": config.OPEN_METEO_LATITUDE,
            "longitude": config.OPEN_METEO_LONGITUDE,
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": config.MORNING_BRIEFING_TIMEZONE,
            "start_date": target_date.isoformat(),
            "end_date": target_date.isoformat(),
        }
    )
    request = Request(f"{OPEN_METEO_FORECAST_URL}?{query}", headers={"User-Agent": "Friday/1.0"})
    with opener(request, timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))

    daily = payload.get("daily") or {}
    weather_code = int((daily.get("weather_code") or [-1])[0])
    precipitation = int(round(float((daily.get("precipitation_probability_max") or [0])[0] or 0)))
    return WeatherBriefing(
        date=target_date.isoformat(),
        temperature_min_c=float((daily.get("temperature_2m_min") or [0])[0]),
        temperature_max_c=float((daily.get("temperature_2m_max") or [0])[0]),
        description=WEATHER_CODE_DESCRIPTIONS.get(weather_code, "mixed weather conditions"),
        precipitation_probability=precipitation,
        rain_warning=precipitation >= 40 or weather_code in {61, 63, 65, 80, 81, 82, 95, 96, 99},
    )
