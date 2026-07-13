"""Local speech-to-text for the Friday voice module.

Uses faster-whisper (MIT, runs fully offline). The dependency is optional:
when the package is missing, transcription returns a structured error with
install instructions instead of crashing the API. The model is loaded lazily
on first use and kept in memory afterwards.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from friday import config


@dataclass(frozen=True)
class TranscriptionResult:
    """Outcome of one local speech-to-text run."""

    ok: bool
    text: str
    language: str
    duration_seconds: float
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "text": self.text,
            "language": self.language,
            "duration_seconds": round(self.duration_seconds, 2),
            "error": self.error,
        }


class FasterWhisperTranscriber:
    """Lazy-loading faster-whisper wrapper (CPU by default)."""

    def __init__(self, model_size: str | None = None, device: str = "auto") -> None:
        self.model_size = (model_size or config.VOICE_STT_MODEL).strip() or "small"
        self.device = device
        self._model: Any = None
        self._load_error: str | None = None
        self._lock = threading.Lock()

    def _load_model(self) -> Any:
        with self._lock:
            if self._model is not None:
                return self._model
            if self._load_error is not None:
                raise RuntimeError(self._load_error)
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                self._load_error = (
                    "faster-whisper ist nicht installiert. Installation: "
                    "pip install -r friday-api/requirements-voice.txt"
                )
                raise RuntimeError(self._load_error) from exc
            try:
                self._model = WhisperModel(
                    self.model_size, device=self.device, compute_type="int8"
                )
            except Exception as exc:  # pragma: no cover - model download/setup boundary
                self._load_error = f"Whisper-Modell konnte nicht geladen werden: {exc}"
                raise RuntimeError(self._load_error) from exc
            return self._model

    def transcribe(self, audio_path: str | Path) -> TranscriptionResult:
        """Transcribe one audio file (wav/m4a/mp3/ogg) to text."""
        path = Path(audio_path)
        if not path.exists() or not path.is_file():
            return TranscriptionResult(
                ok=False,
                text="",
                language="",
                duration_seconds=0.0,
                error="Audiodatei wurde nicht gefunden.",
            )
        try:
            model = self._load_model()
            segments, info = model.transcribe(str(path), vad_filter=True)
            text = " ".join(segment.text.strip() for segment in segments).strip()
            return TranscriptionResult(
                ok=True,
                text=text,
                language=str(getattr(info, "language", "") or ""),
                duration_seconds=float(getattr(info, "duration", 0.0) or 0.0),
            )
        except RuntimeError as exc:
            return TranscriptionResult(
                ok=False, text="", language="", duration_seconds=0.0, error=str(exc)
            )
        except Exception as exc:
            return TranscriptionResult(
                ok=False,
                text="",
                language="",
                duration_seconds=0.0,
                error=f"Transkription fehlgeschlagen: {exc}",
            )


_default_transcriber: FasterWhisperTranscriber | None = None
_default_lock = threading.Lock()


def get_default_transcriber() -> FasterWhisperTranscriber:
    """Return the shared lazily-created transcriber instance."""
    global _default_transcriber
    with _default_lock:
        if _default_transcriber is None:
            _default_transcriber = FasterWhisperTranscriber()
        return _default_transcriber


def transcription_available() -> bool:
    """Report whether the faster-whisper package can be imported."""
    try:
        import faster_whisper  # noqa: F401

        return True
    except ImportError:
        return False
