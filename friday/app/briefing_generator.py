"""Generate and render Friday's nightly English morning briefing."""

from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import numpy as np
import soundfile as sf

from friday import config
from friday.agents.calendar_agent import CalendarAgent
from friday.agents.task_agent import TaskAgent
from friday.app.open_meteo_weather import WeatherBriefing, fetch_open_meteo_weather


BRIEFING_AUDIO_PATTERN = "briefing_*.mp3"
BRIEFING_STATUS_FILE = "briefing_status.json"
KOKORO_SAMPLE_RATE = 24_000


def _audio_dir() -> Path:
    return Path(config.MORNING_BRIEFING_AUDIO_DIR)


def _spoken_title(item: Mapping[str, Any], fallback: str) -> str:
    return str(item.get("title") or item.get("summary") or fallback).strip()


def _appointment_sort_key(item: Mapping[str, Any]) -> str:
    return str(item.get("start") or item.get("start_time") or "99:99")


def _spoken_appointment(item: Mapping[str, Any]) -> str:
    title = _spoken_title(item, "Untitled appointment")
    start = str(item.get("start") or item.get("start_time") or "time unavailable")
    try:
        parsed = datetime.fromisoformat(start.replace("Z", "+00:00"))
        start = parsed.strftime("%I:%M %p").lstrip("0")
    except ValueError:
        if len(start) >= 5 and ":" in start:
            start = start[:5]
    return f"{title} at {start}"


def generate_briefing_script(
    target_date: date,
    *,
    tasks: Iterable[Mapping[str, Any]] | None = None,
    appointments: Iterable[Mapping[str, Any]] | None = None,
    weather: WeatherBriefing | str | None = None,
) -> str:
    """Build the complete briefing script in English."""

    task_items = list(tasks) if tasks is not None else TaskAgent().get_open_tasks()
    appointment_items = (
        list(appointments)
        if appointments is not None
        else CalendarAgent().get_items_for_date(target_date.isoformat())
    )

    top_tasks = task_items[:3]
    if top_tasks:
        task_text = "; ".join(_spoken_title(item, "Untitled task") for item in top_tasks)
    else:
        task_text = "You have no priority tasks scheduled"

    ordered_appointments = sorted(appointment_items, key=_appointment_sort_key)
    if ordered_appointments:
        appointment_text = "; ".join(_spoken_appointment(item) for item in ordered_appointments)
    else:
        appointment_text = "You have no appointments scheduled"

    if weather is None:
        try:
            weather = fetch_open_meteo_weather(target_date)
        except Exception:
            weather_text = "Weather information is currently unavailable."
        else:
            weather_text = weather.to_english()
    elif isinstance(weather, WeatherBriefing):
        weather_text = weather.to_english()
    else:
        weather_text = str(weather).strip()

    return (
        "Good morning. Here are your most important tasks today: "
        f"{task_text}. Your appointments: {appointment_text}. "
        f"The weather: {weather_text}"
    )


def _default_pipeline_factory(lang_code: str):
    from kokoro import KPipeline

    return KPipeline(lang_code=lang_code)


def render_briefing_audio(
    script: str,
    target_date: date,
    *,
    pipeline_factory: Callable[[str], Any] = _default_pipeline_factory,
) -> Path:
    """Render one MP3 and replace older briefings only after success."""

    text = script.strip()
    if not text:
        raise ValueError("Briefing script must not be empty.")

    output_dir = _audio_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    final_path = output_dir / f"briefing_{target_date.isoformat()}.mp3"
    temporary_path = output_dir / "briefing_render.tmp"

    try:
        pipeline = pipeline_factory(config.MORNING_BRIEFING_LANG_CODE)
        chunks: list[np.ndarray] = []
        for _graphemes, _phonemes, audio in pipeline(
            text,
            voice=config.MORNING_BRIEFING_VOICE,
            speed=1,
            split_pattern=r"\n+",
        ):
            chunk = np.asarray(audio, dtype=np.float32).reshape(-1)
            if chunk.size:
                chunks.append(chunk)
        if not chunks:
            raise RuntimeError("Kokoro returned no audio samples.")

        sf.write(
            temporary_path,
            np.concatenate(chunks),
            KOKORO_SAMPLE_RATE,
            format="MP3",
            subtype="MPEG_LAYER_III",
        )
        if not temporary_path.exists() or temporary_path.stat().st_size <= 0:
            raise RuntimeError("Kokoro MP3 output is empty.")

        for old_path in output_dir.glob(BRIEFING_AUDIO_PATTERN):
            old_path.unlink()
        temporary_path.replace(final_path)
        return final_path
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def current_briefing_audio() -> Path | None:
    files = sorted(_audio_dir().glob(BRIEFING_AUDIO_PATTERN), key=lambda path: path.stat().st_mtime, reverse=True)
    return files[0] if files else None


def write_briefing_status(payload: Mapping[str, Any]) -> Path:
    output_dir = _audio_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / BRIEFING_STATUS_FILE
    temporary = output_dir / f"{BRIEFING_STATUS_FILE}.tmp"
    temporary.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)
    return target


def read_briefing_status() -> dict[str, Any]:
    path = _audio_dir() / BRIEFING_STATUS_FILE
    if not path.exists():
        return {
            "success": False,
            "error": "No morning briefing has been generated yet.",
            "language": "en-US",
            "lang_code": config.MORNING_BRIEFING_LANG_CODE,
            "voice_id": config.MORNING_BRIEFING_VOICE,
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "success": False,
            "error": "Morning briefing status could not be read.",
            "language": "en-US",
            "lang_code": config.MORNING_BRIEFING_LANG_CODE,
            "voice_id": config.MORNING_BRIEFING_VOICE,
        }
    return payload if isinstance(payload, dict) else {}


def build_briefing_status(
    *,
    target_date: date,
    success: bool,
    audio_path: Path | None,
    error: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "date": target_date.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "file_name": audio_path.name if audio_path else None,
        "file_size": audio_path.stat().st_size if audio_path and audio_path.exists() else 0,
        "success": success,
        "error": error,
        "language": "en-US",
        "lang_code": config.MORNING_BRIEFING_LANG_CODE,
        "voice_id": config.MORNING_BRIEFING_VOICE,
    }
    if extra:
        payload.update(dict(extra))
    return payload
