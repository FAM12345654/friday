"""Hermetic tests for ahead-of-time briefing pre-generation."""

from __future__ import annotations

import json
from datetime import date

from friday.app import briefing_pregeneration
from friday.app.briefing_pregeneration import (
    pregenerate_briefing,
    read_briefing_status,
    read_pregenerated_audio,
)
from friday.app.voice_synthesis import SynthesisResult

WAV = b"RIFFfakewavdata"


def _ok_synth(text, language):
    assert text
    return SynthesisResult(ok=True, audio=WAV, media_type="audio/wav", engine=f"fake-{language}")


def _down_synth(text, language):
    return SynthesisResult(
        ok=False, audio=b"", media_type="", engine="fake", error="TTS-Server nicht erreichbar."
    )


def test_pregenerate_writes_wav_and_status(tmp_path) -> None:
    result = pregenerate_briefing(
        target_date=date(2026, 7, 15),
        language="de",
        briefing_text="Guten Morgen! Heute ist Mittwoch.",
        synthesizer=_ok_synth,
        audio_dir=tmp_path,
    )

    assert result.ok is True
    assert result.audio_path == tmp_path / "briefing_2026-07-15.wav"
    assert result.audio_path.read_bytes() == WAV

    status = json.loads((tmp_path / "briefing_status.json").read_text(encoding="utf-8"))
    assert status["ok"] is True
    assert status["file_name"] == "briefing_2026-07-15.wav"
    assert status["language"] == "de"
    assert read_pregenerated_audio(date(2026, 7, 15), audio_dir=tmp_path) == WAV


def test_pregenerate_prunes_to_keep_last(tmp_path) -> None:
    for day in range(1, 6):
        (tmp_path / f"briefing_2026-07-0{day}.wav").write_bytes(b"old")

    pregenerate_briefing(
        target_date=date(2026, 7, 15),
        briefing_text="Text.",
        synthesizer=_ok_synth,
        audio_dir=tmp_path,
        keep_last=3,
    )

    remaining = sorted(p.name for p in tmp_path.glob("briefing_*.wav"))
    assert len(remaining) == 3
    # Newest by name are kept: 15, then 05, 04.
    assert "briefing_2026-07-15.wav" in remaining
    assert "briefing_2026-07-01.wav" not in remaining


def test_pregenerate_failure_records_status_and_keeps_old_audio(tmp_path) -> None:
    old = tmp_path / "briefing_2026-07-14.wav"
    old.write_bytes(b"old")

    result = pregenerate_briefing(
        target_date=date(2026, 7, 15),
        briefing_text="Text.",
        synthesizer=_down_synth,
        audio_dir=tmp_path,
    )

    assert result.ok is False
    assert result.audio_path is None
    assert "nicht erreichbar" in (result.error or "")
    assert old.read_bytes() == b"old"
    assert not (tmp_path / "briefing_2026-07-15.wav").exists()

    status = read_briefing_status(audio_dir=tmp_path)
    assert status["ok"] is False


def test_read_pregenerated_audio_missing_returns_none(tmp_path) -> None:
    assert read_pregenerated_audio(date(2026, 7, 15), audio_dir=tmp_path) is None
    status = read_briefing_status(audio_dir=tmp_path)
    assert status["ok"] is False
    assert "noch kein Briefing" in status["error"]
