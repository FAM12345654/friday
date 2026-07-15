"""Local text-to-speech for the Friday voice module.

Speaks through OpenAI-compatible ``/v1/audio/speech`` servers running on
localhost — German through an Orpheus server (human, emotional prosody;
e.g. Orpheus-FastAPI with the "Kartoffel" German fine-tune), English through
a Kokoro server (e.g. kokoro-fastapi). Both are free, subscription-less and
fully local; the same localhost-only guard as the Ollama runtime applies.
The HTTP poster is injectable so tests never touch the network.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable
from urllib import error, request

from friday import config
from friday.app.local_ollama_runtime import is_local_ollama_url

# poster(url, payload_bytes, timeout_seconds) -> (status_code, response_body)
Poster = Callable[[str, bytes, int], tuple[int, bytes]]

SUPPORTED_LANGUAGES = ("de", "en")
MAX_TTS_AUDIO_BYTES = 25 * 1024 * 1024


@dataclass(frozen=True)
class SynthesisResult:
    """Outcome of one local text-to-speech run."""

    ok: bool
    audio: bytes
    media_type: str
    engine: str
    error: str | None = None


def _default_poster(url: str, payload: bytes, timeout_seconds: int) -> tuple[int, bytes]:
    req = request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout_seconds) as response:
            return response.status, response.read()
    except error.HTTPError as exc:
        return exc.code, exc.read()


class SpeechSynthesizer:
    """Client for one OpenAI-compatible local TTS server."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        voice: str,
        engine: str,
        poster: Poster | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.base_url = base_url.strip().rstrip("/")
        self.model = model
        self.voice = voice
        self.engine = engine
        self.poster = poster or _default_poster
        self.timeout_seconds = timeout_seconds or config.VOICE_TTS_TIMEOUT_SECONDS

    def synthesize(self, text: str) -> SynthesisResult:
        cleaned = " ".join(str(text or "").split())
        if not cleaned:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error="Kein Text zum Sprechen.",
            )
        if not is_local_ollama_url(self.base_url):
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error="Sprachausgabe erlaubt nur 127.0.0.1 oder localhost.",
            )
        payload = json.dumps(
            {
                "model": self.model,
                "voice": self.voice,
                "input": cleaned,
                "response_format": "wav",
            }
        ).encode("utf-8")
        try:
            status, body = self.poster(
                f"{self.base_url}/v1/audio/speech", payload, self.timeout_seconds
            )
        except (OSError, error.URLError, TimeoutError) as exc:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error=f"TTS-Server nicht erreichbar ({self.base_url}): {exc}",
            )
        if not (200 <= status < 300) or not body:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error=f"TTS-Server antwortete mit HTTP {status}.",
            )
        if len(body) > MAX_TTS_AUDIO_BYTES:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error="TTS-Antwort überschreitet das Sicherheitslimit.",
            )
        return SynthesisResult(ok=True, audio=body, media_type="audio/wav", engine=self.engine)


class VoiceboxSpeechSynthesizer:
    """Client for Voicebox v0.5+'s synchronous ``/generate/stream`` API."""

    def __init__(
        self,
        *,
        base_url: str,
        profile_id: str,
        language: str,
        engine: str,
        model_size: str,
        poster: Poster | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.base_url = str(base_url or "").strip().rstrip("/")
        self.profile_id = str(profile_id or "").strip()
        self.language = normalize_language(language)
        self.voicebox_engine = str(engine or "").strip()
        self.model_size = str(model_size or "").strip()
        self.engine = f"voicebox-{self.voicebox_engine}-{self.language}"
        self.poster = poster or _default_poster
        self.timeout_seconds = timeout_seconds or config.VOICE_TTS_TIMEOUT_SECONDS

    def synthesize(self, text: str) -> SynthesisResult:
        cleaned = " ".join(str(text or "").split())
        if not cleaned:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error="Kein Text zum Sprechen.",
            )
        if not self.profile_id:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error="Voicebox-Profil ist für diese Sprache nicht konfiguriert.",
            )
        if not is_local_ollama_url(self.base_url):
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error="Voicebox ist nur über 127.0.0.1 oder localhost erlaubt.",
            )
        payload = json.dumps(
            {
                "profile_id": self.profile_id,
                "text": cleaned,
                "language": self.language,
                "engine": self.voicebox_engine,
                "model_size": self.model_size,
                "normalize": True,
                "max_chunk_chars": 800,
                "crossfade_ms": 50,
            }
        ).encode("utf-8")
        try:
            status, body = self.poster(
                f"{self.base_url}/generate/stream",
                payload,
                self.timeout_seconds,
            )
        except (OSError, error.URLError, TimeoutError) as exc:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error=f"Voicebox nicht erreichbar ({self.base_url}): {exc}",
            )
        if not (200 <= status < 300) or not body:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error=f"Voicebox antwortete mit HTTP {status}.",
            )
        if len(body) > MAX_TTS_AUDIO_BYTES:
            return SynthesisResult(
                ok=False, audio=b"", media_type="", engine=self.engine,
                error="Voicebox-Antwort überschreitet das Sicherheitslimit.",
            )
        return SynthesisResult(
            ok=True,
            audio=body,
            media_type="audio/wav",
            engine=self.engine,
        )


def _synthesizer_for_language(
    language: str,
    poster: Poster | None = None,
) -> SpeechSynthesizer | VoiceboxSpeechSynthesizer:
    if (
        language == "de"
        and str(getattr(config, "VOICE_TTS_DE_PROVIDER", "orpheus")).strip()
        == "voicebox"
    ):
        return VoiceboxSpeechSynthesizer(
            base_url=config.VOICEBOX_BASE_URL,
            profile_id=config.VOICEBOX_DE_PROFILE_ID,
            language=language,
            engine=config.VOICEBOX_DE_ENGINE,
            model_size=config.VOICEBOX_DE_MODEL_SIZE,
            poster=poster,
        )
    if language == "de":
        return SpeechSynthesizer(
            base_url=config.VOICE_TTS_DE_BASE_URL,
            model=config.VOICE_TTS_DE_MODEL,
            voice=config.VOICE_TTS_DE_VOICE,
            engine="orpheus-de",
            poster=poster,
        )
    return SpeechSynthesizer(
        base_url=config.VOICE_TTS_EN_BASE_URL,
        model=config.VOICE_TTS_EN_MODEL,
        voice=config.VOICE_TTS_EN_VOICE,
        engine="kokoro-en",
        poster=poster,
    )


def normalize_language(language: Any) -> str:
    """Map a detected/requested language to a supported synthesis language."""
    cleaned = str(language or "").strip().lower()[:2]
    return cleaned if cleaned in SUPPORTED_LANGUAGES else "de"


def synthesize_for_language(
    text: str,
    language: str = "de",
    *,
    poster: Poster | None = None,
) -> SynthesisResult:
    """Speak text with the voice configured for the language (default German)."""
    synthesizer = _synthesizer_for_language(normalize_language(language), poster=poster)
    return synthesizer.synthesize(text)
