"""Tests for the local STT wrapper (fake faster_whisper, no model download)."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass

import pytest

from friday.app.voice_transcription import FasterWhisperTranscriber


@dataclass
class _Segment:
    text: str


@dataclass
class _Info:
    language: str
    duration: float


class _FakeWhisperModel:
    def __init__(self, model_size, device="auto", compute_type="int8") -> None:
        self.model_size = model_size

    def transcribe(self, path, vad_filter=True):
        segments = [_Segment(text=" Guten Morgen "), _Segment(text="Friday. ")]
        return iter(segments), _Info(language="de", duration=2.5)


@pytest.fixture()
def fake_faster_whisper(monkeypatch: pytest.MonkeyPatch):
    module = types.ModuleType("faster_whisper")
    module.WhisperModel = _FakeWhisperModel
    monkeypatch.setitem(sys.modules, "faster_whisper", module)
    return module


def test_transcribe_joins_segments(tmp_path, fake_faster_whisper) -> None:
    audio = tmp_path / "speech.m4a"
    audio.write_bytes(b"fake-audio")

    result = FasterWhisperTranscriber(model_size="small").transcribe(audio)
    assert result.ok
    assert result.text == "Guten Morgen Friday."
    assert result.language == "de"
    assert result.duration_seconds == 2.5


def test_missing_file_is_clean_error(fake_faster_whisper) -> None:
    result = FasterWhisperTranscriber().transcribe("/does/not/exist.wav")
    assert not result.ok
    assert "nicht gefunden" in result.error


def test_missing_package_gives_install_hint(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"fake-audio")
    # Simulate faster-whisper not being installed.
    monkeypatch.setitem(sys.modules, "faster_whisper", None)

    result = FasterWhisperTranscriber().transcribe(audio)
    assert not result.ok
    assert "requirements-voice" in result.error


def test_model_loaded_once(tmp_path, fake_faster_whisper, monkeypatch: pytest.MonkeyPatch) -> None:
    constructions = []

    class CountingModel(_FakeWhisperModel):
        def __init__(self, *args, **kwargs) -> None:
            constructions.append(1)
            super().__init__(*args, **kwargs)

    fake_faster_whisper.WhisperModel = CountingModel
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"fake-audio")

    transcriber = FasterWhisperTranscriber()
    transcriber.transcribe(audio)
    transcriber.transcribe(audio)
    assert sum(constructions) == 1


def test_to_dict_shape(tmp_path, fake_faster_whisper) -> None:
    audio = tmp_path / "speech.wav"
    audio.write_bytes(b"fake-audio")
    payload = FasterWhisperTranscriber().transcribe(audio).to_dict()
    assert payload["ok"] is True
    assert set(payload) == {"ok", "text", "language", "duration_seconds", "error"}
