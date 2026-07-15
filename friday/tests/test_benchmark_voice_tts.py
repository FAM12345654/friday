"""Offline tests for the local TTS comparison harness."""

from __future__ import annotations

from io import BytesIO
import json
import wave

import pytest

from scripts.benchmark_voice_tts import (
    EngineConfig,
    HttpResponse,
    Prompt,
    benchmark,
    build_endpoint,
    build_payload,
    config_from_args,
    load_prompts,
    parse_args,
    percentile,
    render_csv,
    render_json,
    run_request,
    validate_loopback_base_url,
    wav_duration_seconds,
)


def _wav_bytes(duration_seconds: float = 1.0, sample_rate: int = 8_000) -> bytes:
    output = BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b"\0\0" * int(duration_seconds * sample_rate))
    return output.getvalue()


class _Clock:
    def __init__(self, values) -> None:
        self.values = iter(values)

    def __call__(self) -> float:
        return next(self.values)


@pytest.mark.parametrize(
    "url",
    (
        "http://localhost:5005",
        "http://127.0.0.1:17493/",
        "http://127.99.1.2:5005",
        "https://[::1]:17493",
    ),
)
def test_validate_loopback_base_url_accepts_only_loopback_forms(url: str) -> None:
    assert validate_loopback_base_url(url)


@pytest.mark.parametrize(
    "url",
    (
        "https://example.com",
        "http://192.168.178.42:5005",
        "http://100.122.129.101:17493",
        "http://user:secret@127.0.0.1:5005",
        "ftp://127.0.0.1:5005",
        "http://127.0.0.1:5005/api",
        "http://127.0.0.1:5005?next=https://example.com",
    ),
)
def test_validate_loopback_base_url_rejects_nonlocal_or_ambiguous_urls(url: str) -> None:
    with pytest.raises(ValueError):
        validate_loopback_base_url(url)


def test_builds_orpheus_openai_compatible_request() -> None:
    config = EngineConfig(engine="orpheus", base_url="http://127.0.0.1:5005")

    assert build_endpoint(config).endswith("/v1/audio/speech")
    assert json.loads(build_payload(config, " Hallo   Welt ")) == {
        "model": "orpheus",
        "voice": "jana",
        "input": "Hallo Welt",
        "response_format": "wav",
    }


def test_builds_voicebox_qwen_base_request_and_requires_profile() -> None:
    config = EngineConfig(
        engine="voicebox",
        base_url="http://localhost:17493",
        voicebox_profile_id="friday-de-clone",
    )

    assert build_endpoint(config).endswith("/generate/stream")
    payload = json.loads(build_payload(config, "Guten Morgen"))
    assert payload["engine"] == "qwen"
    assert payload["model_size"] == "0.6B"
    assert payload["profile_id"] == "friday-de-clone"
    assert payload["language"] == "de"

    with pytest.raises(ValueError, match="profile_id"):
        build_payload(
            EngineConfig(engine="voicebox", base_url="http://127.0.0.1:17493"),
            "Hallo",
        )


def test_wav_duration_and_rtf_are_measured_without_audio_files() -> None:
    audio = _wav_bytes(duration_seconds=2.0)
    duration, wav_error = wav_duration_seconds(audio)
    config = EngineConfig(engine="orpheus", base_url="http://127.0.0.1:5005")

    result = run_request(
        config,
        Prompt("one", "Hallo"),
        1,
        transport=lambda *_: HttpResponse(200, audio, "audio/wav"),
        clock=_Clock((10.0, 11.0)),
    )

    assert wav_error is None
    assert duration == pytest.approx(2.0)
    assert result.success is True
    assert result.latency_seconds == pytest.approx(1.0)
    assert result.audio_duration_seconds == pytest.approx(2.0)
    assert result.rtf == pytest.approx(0.5)


def test_invalid_wav_and_http_failure_are_structured_errors() -> None:
    config = EngineConfig(engine="orpheus", base_url="http://localhost:5005")

    invalid = run_request(
        config,
        Prompt("invalid", "Hallo"),
        1,
        transport=lambda *_: HttpResponse(200, b'{"ok":true}', "application/json"),
        clock=_Clock((0.0, 0.2)),
    )
    failed = run_request(
        config,
        Prompt("failed", "Hallo"),
        1,
        transport=lambda *_: HttpResponse(503, b"busy", "text/plain"),
        clock=_Clock((1.0, 1.3)),
    )

    assert invalid.success is False
    assert invalid.error == "Antwort ist kein RIFF/WAVE-Audio"
    assert invalid.rtf is None
    assert failed.success is False
    assert failed.error == "HTTP 503"


def test_benchmark_summary_has_success_latency_rtf_and_errors() -> None:
    audio = _wav_bytes(duration_seconds=1.0)
    responses = iter(
        (
            HttpResponse(200, audio, "audio/wav"),
            HttpResponse(200, audio, "audio/wav"),
            HttpResponse(500, b"error", "text/plain"),
        )
    )
    config = EngineConfig(engine="orpheus", base_url="http://127.0.0.1:5005")
    report = benchmark(
        config,
        (Prompt("one", "Hallo"),),
        repetitions=2,
        warmups=1,
        transport=lambda *_: next(responses),
        clock=_Clock((0.0, 0.1, 1.0, 1.2, 2.0, 2.4)),
    )

    assert len(report.runs) == 2
    assert report.summary["success_count"] == 1
    assert report.summary["failure_count"] == 1
    assert report.summary["latency_p50_seconds"] == pytest.approx(0.2)
    assert report.summary["rtf_p50"] == pytest.approx(0.2)
    assert report.summary["errors"] == {"HTTP 500": 1}


def test_renderers_are_json_and_csv_friendly() -> None:
    audio = _wav_bytes()
    report = benchmark(
        EngineConfig(engine="orpheus", base_url="http://127.0.0.1:5005"),
        (Prompt("one", "Hallo"),),
        repetitions=1,
        warmups=0,
        transport=lambda *_: HttpResponse(200, audio, "audio/wav"),
        clock=_Clock((0.0, 0.1)),
    )

    parsed = json.loads(render_json(report))
    csv_text = render_csv(report)

    assert parsed["summary"]["success_count"] == 1
    assert parsed["runs"][0]["prompt_id"] == "one"
    assert csv_text.startswith("engine,prompt_id,repetition,success,")
    assert "orpheus,one,1,True," in csv_text
    assert "summary_latency_p50_seconds" in csv_text.splitlines()[0]


def test_percentile_uses_linear_interpolation() -> None:
    assert percentile([], 0.95) is None
    assert percentile([2.0], 0.95) == 2.0
    assert percentile([1.0, 2.0, 3.0], 0.50) == 2.0
    assert percentile([1.0, 2.0], 0.95) == pytest.approx(1.95)


def test_load_prompts_uses_bounded_local_json(tmp_path) -> None:
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps(["Hallo", {"id": "custom", "text": "Guten Morgen"}]),
        encoding="utf-8",
    )

    prompts = load_prompts(corpus)

    assert prompts == (
        Prompt("prompt_001", "Hallo"),
        Prompt("custom", "Guten Morgen"),
    )


def test_load_prompts_rejects_csv_formula_like_ids(tmp_path) -> None:
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps([{"id": "=CMD()", "text": "Hallo"}]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Corpus-ID"):
        load_prompts(corpus)


def test_cli_config_fails_closed_before_network_for_invalid_limits() -> None:
    args = parse_args(["--engine", "orpheus", "--timeout", "0"])

    with pytest.raises(ValueError, match="timeout"):
        config_from_args(args)

    voicebox_args = parse_args(["--engine", "voicebox", "--profile-id", ""])
    with pytest.raises(ValueError, match="profile_id"):
        config_from_args(voicebox_args)
