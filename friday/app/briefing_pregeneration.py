"""Pre-generate the spoken morning briefing so the alarm plays instantly.

The user's key idea: render the briefing audio ahead of time (e.g. nightly)
and store it locally, so the morning alarm just plays the finished file
instead of waiting for live synthesis. This module reuses the shared building
blocks — ``voice_briefing.build_briefing_text`` for the text and
``voice_synthesis.synthesize_for_language`` for the audio (local Orpheus DE /
Kokoro EN via localhost) — rather than a parallel text builder or TTS client.

Everything is local: the WAV file plus a small status JSON land under
``config.BRIEFING_PREGEN_DIR``. Paths and the synthesizer are injectable so
tests stay hermetic (fake synthesizer + ``tmp_path``, never real ``local_data``).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

from friday import config
from friday.app import open_meteo_weather, voice_synthesis
from friday.app.voice_briefing import build_briefing_text, select_overdue_tasks
from friday.app.voice_synthesis import SynthesisResult

BRIEFING_STATUS_FILE = "briefing_status.json"

# synthesizer(text, language) -> SynthesisResult
Synthesizer = Callable[[str, str], SynthesisResult]


def _pregen_dir(audio_dir: Path | str | None) -> Path:
    return Path(audio_dir) if audio_dir is not None else Path(config.BRIEFING_PREGEN_DIR)


def briefing_file_name(target_date: date) -> str:
    return f"briefing_{target_date.isoformat()}.wav"


@dataclass(frozen=True)
class PregenerationResult:
    """Outcome of one pre-generation run."""

    ok: bool
    date: str
    audio_path: Path | None
    status_path: Path | None
    text: str
    engine: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["audio_path"] = str(self.audio_path) if self.audio_path else None
        payload["status_path"] = str(self.status_path) if self.status_path else None
        return payload


def _default_text_provider(target_date: date, language: str) -> str:
    """Build the briefing text from the live agents (real, non-test path)."""
    # Imported lazily so tests that inject text never construct the agents.
    from friday.agents.calendar_agent import CalendarAgent
    from friday.agents.task_agent import TaskAgent

    day_iso = target_date.isoformat()
    task_agent = TaskAgent()
    tasks_today = task_agent.get_tasks_for_date(day_iso)
    open_tasks = task_agent.get_open_tasks()
    calendar_items = CalendarAgent().get_items_for_date(day_iso)
    weather_text = open_meteo_weather.weather_briefing_text(target_date, language)
    return build_briefing_text(
        day_iso=day_iso,
        tasks_today=tasks_today,
        overdue_tasks=select_overdue_tasks(open_tasks, day_iso),
        calendar_items=calendar_items,
        language=language,
        weather_text=weather_text,
    )


def _write_status(directory: Path, payload: dict[str, Any]) -> Path:
    target = directory / BRIEFING_STATUS_FILE
    temporary = directory / f"{BRIEFING_STATUS_FILE}.tmp"
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(target)
    return target


def read_briefing_status(*, audio_dir: Path | str | None = None) -> dict[str, Any]:
    """Return the last pre-generation status, or a default 'not generated' one."""
    path = _pregen_dir(audio_dir) / BRIEFING_STATUS_FILE
    if not path.exists():
        return {"ok": False, "error": "Es wurde noch kein Briefing vorproduziert."}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"ok": False, "error": "Briefing-Status konnte nicht gelesen werden."}
    return payload if isinstance(payload, dict) else {}


def prune_old_briefings(directory: Path, *, keep_last: int) -> None:
    """Keep only the newest ``keep_last`` briefing WAV files."""
    files = sorted(
        directory.glob("briefing_*.wav"),
        key=lambda path: path.name,
        reverse=True,
    )
    for stale in files[max(keep_last, 0):]:
        stale.unlink(missing_ok=True)


def read_pregenerated_audio(
    target_date: date,
    *,
    audio_dir: Path | str | None = None,
) -> bytes | None:
    """Return the pre-generated WAV bytes for the date, or ``None`` if absent."""
    path = _pregen_dir(audio_dir) / briefing_file_name(target_date)
    if not path.exists():
        return None
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return data or None


def pregenerate_briefing(
    *,
    target_date: date | None = None,
    language: str | None = None,
    briefing_text: str | None = None,
    synthesizer: Synthesizer = voice_synthesis.synthesize_for_language,
    text_provider: Callable[[date, str], str] = _default_text_provider,
    audio_dir: Path | str | None = None,
    keep_last: int | None = None,
) -> PregenerationResult:
    """Render one briefing WAV ahead of time and write a small status JSON.

    The previous WAV is only replaced after a successful synthesis; on failure
    the status records the error and existing audio is left untouched.
    """
    day = target_date or date.today()
    lang = (language or config.BRIEFING_PREGEN_LANGUAGE or "de").lower()[:2]
    keep = keep_last if keep_last is not None else int(config.BRIEFING_PREGEN_KEEP_LAST)
    directory = _pregen_dir(audio_dir)
    directory.mkdir(parents=True, exist_ok=True)

    text = briefing_text if briefing_text is not None else text_provider(day, lang)

    result = synthesizer(text, lang)
    if not result.ok or not result.audio:
        status = {
            "ok": False,
            "date": day.isoformat(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "language": lang,
            "engine": result.engine,
            "error": result.error or "Sprachausgabe lieferte kein Audio.",
        }
        status_path = _write_status(directory, status)
        return PregenerationResult(
            ok=False,
            date=day.isoformat(),
            audio_path=None,
            status_path=status_path,
            text=text,
            engine=result.engine,
            error=status["error"],
        )

    final_path = directory / briefing_file_name(day)
    temporary_path = directory / f"{briefing_file_name(day)}.tmp"
    temporary_path.write_bytes(result.audio)
    temporary_path.replace(final_path)
    prune_old_briefings(directory, keep_last=keep)

    status = {
        "ok": True,
        "date": day.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "language": lang,
        "engine": result.engine,
        "file_name": final_path.name,
        "file_size": final_path.stat().st_size,
        "error": None,
    }
    status_path = _write_status(directory, status)
    return PregenerationResult(
        ok=True,
        date=day.isoformat(),
        audio_path=final_path,
        status_path=status_path,
        text=text,
        engine=result.engine,
    )
