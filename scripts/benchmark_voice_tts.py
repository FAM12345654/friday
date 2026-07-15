"""Benchmark Friday's German Orpheus path against a local Voicebox pilot.

The harness intentionally benchmarks one engine per process.  On an 8 GB GPU,
run Orpheus first, stop/unload it, then run Voicebox.  It never installs models,
persists audio, follows redirects, or connects to a non-loopback address.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import asdict, dataclass
from io import BytesIO, StringIO
import ipaddress
import json
from pathlib import Path
import re
import sys
import time
from typing import Callable, Sequence
from urllib import error, request
from urllib.parse import urlsplit
import wave


MAX_AUDIO_BYTES = 25 * 1024 * 1024
MAX_CORPUS_BYTES = 1 * 1024 * 1024
MAX_PROMPTS = 100
MAX_PROMPT_CHARS = 5_000
MAX_REPETITIONS = 20
MAX_WARMUPS = 10
MAX_TIMEOUT_SECONDS = 300.0
PROMPT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")

DEFAULT_PROMPTS = (
    ("short_ack", "Alles klar, ich kümmere mich darum."),
    ("calendar", "Dein nächster Termin beginnt morgen um 9 Uhr 30."),
    ("numbers", "Die Rechnung über 1.249,50 Euro ist am 17. Juli fällig."),
    ("names", "Bitte erinnere Philip an das Meeting mit Dr. Müller-Schönberg."),
    ("compound", "Die Datenschutzfolgeabschätzung ist vollständig vorbereitet."),
    ("code_switch", "Der Friday Mobile Build und das API Gateway sind erreichbar."),
    (
        "briefing",
        "Guten Morgen. Heute stehen drei Aufgaben an: das Angebot prüfen, den "
        "Kalender aktualisieren und Anna wegen des Liefertermins zurückrufen.",
    ),
    ("question", "Soll ich den Entwurf öffnen oder möchtest du ihn später prüfen?"),
)


@dataclass(frozen=True)
class Prompt:
    """One stable benchmark prompt."""

    prompt_id: str
    text: str


@dataclass(frozen=True)
class EngineConfig:
    """Request configuration for one local TTS engine."""

    engine: str
    base_url: str
    timeout_seconds: float = 60.0
    orpheus_model: str = "orpheus"
    orpheus_voice: str = "jana"
    voicebox_profile_id: str = ""
    voicebox_engine: str = "qwen"
    voicebox_model_size: str = "0.6B"


@dataclass(frozen=True)
class HttpResponse:
    """Bounded HTTP result used by the benchmark and its offline tests."""

    status: int
    body: bytes
    content_type: str = ""


@dataclass(frozen=True)
class RunResult:
    """Measurements for one complete WAV request."""

    engine: str
    prompt_id: str
    repetition: int
    success: bool
    latency_seconds: float
    audio_duration_seconds: float | None
    rtf: float | None
    wav_readable: bool
    http_status: int | None
    content_type: str
    bytes_received: int
    error: str | None
    wav_parse_error: str | None


@dataclass(frozen=True)
class BenchmarkReport:
    """Serializable benchmark output."""

    schema_version: int
    engine: str
    endpoint: str
    repetitions: int
    warmups: int
    prompt_count: int
    summary: dict[str, object]
    runs: tuple[RunResult, ...]


Transport = Callable[[str, bytes, float], HttpResponse]
Clock = Callable[[], float]


class _NoRedirectHandler(request.HTTPRedirectHandler):
    """Block redirects so a loopback server cannot redirect externally."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def validate_loopback_base_url(value: str) -> str:
    """Return a normalized HTTP(S) loopback base URL or raise ``ValueError``."""

    cleaned = str(value or "").strip().rstrip("/")
    try:
        parsed = urlsplit(cleaned)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Endpoint enthält einen ungültigen Port.") from exc

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Endpoint muss HTTP oder HTTPS verwenden.")
    if not parsed.hostname:
        raise ValueError("Endpoint benötigt einen Hostnamen.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Endpoint darf keine Zugangsdaten enthalten.")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Endpoint muss eine reine Basis-URL ohne Pfad oder Query sein.")

    hostname = parsed.hostname.lower()
    is_loopback = hostname == "localhost"
    if not is_loopback:
        try:
            is_loopback = ipaddress.ip_address(hostname).is_loopback
        except ValueError:
            is_loopback = False
    if not is_loopback:
        raise ValueError("Nur localhost- oder Loopback-Endpunkte sind erlaubt.")

    if port is not None and not 1 <= port <= 65_535:
        raise ValueError("Endpoint enthält einen ungültigen Port.")
    return cleaned


def build_endpoint(config: EngineConfig) -> str:
    """Build and revalidate the exact endpoint for one engine."""

    base_url = validate_loopback_base_url(config.base_url)
    if config.engine == "orpheus":
        return f"{base_url}/v1/audio/speech"
    if config.engine == "voicebox":
        return f"{base_url}/generate/stream"
    raise ValueError(f"Unbekannte Engine: {config.engine}")


def build_payload(config: EngineConfig, text: str) -> bytes:
    """Build the engine-specific JSON request body."""

    cleaned = " ".join(str(text or "").split())
    if not cleaned:
        raise ValueError("Benchmark-Text darf nicht leer sein.")
    if len(cleaned) > MAX_PROMPT_CHARS:
        raise ValueError(f"Benchmark-Text darf höchstens {MAX_PROMPT_CHARS} Zeichen haben.")

    if config.engine == "orpheus":
        payload = {
            "model": config.orpheus_model,
            "voice": config.orpheus_voice,
            "input": cleaned,
            "response_format": "wav",
        }
    elif config.engine == "voicebox":
        if not config.voicebox_profile_id.strip():
            raise ValueError("Voicebox benötigt eine lokale profile_id.")
        payload = {
            "profile_id": config.voicebox_profile_id.strip(),
            "text": cleaned,
            "language": "de",
            "engine": config.voicebox_engine,
            "model_size": config.voicebox_model_size,
            "normalize": True,
            "max_chunk_chars": 800,
            "crossfade_ms": 50,
        }
    else:
        raise ValueError(f"Unbekannte Engine: {config.engine}")
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def _read_bounded(response) -> bytes:  # noqa: ANN001
    content_length = response.headers.get("Content-Length")
    if content_length:
        try:
            declared_length = int(content_length)
        except ValueError:
            declared_length = None
        if declared_length is not None and declared_length > MAX_AUDIO_BYTES:
            raise ValueError("TTS-Antwort überschreitet das Sicherheitslimit.")
    body = response.read(MAX_AUDIO_BYTES + 1)
    if len(body) > MAX_AUDIO_BYTES:
        raise ValueError("TTS-Antwort überschreitet das Sicherheitslimit.")
    return body


def local_http_transport(url: str, payload: bytes, timeout_seconds: float) -> HttpResponse:
    """POST JSON to one loopback URL without proxies or redirects."""

    parsed = urlsplit(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    validate_loopback_base_url(base)
    opener = request.build_opener(request.ProxyHandler({}), _NoRedirectHandler())
    req = request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "audio/wav"},
        method="POST",
    )
    try:
        with opener.open(req, timeout=timeout_seconds) as response:
            final = urlsplit(response.geturl())
            validate_loopback_base_url(f"{final.scheme}://{final.netloc}")
            return HttpResponse(
                status=int(response.status),
                body=_read_bounded(response),
                content_type=str(response.headers.get("Content-Type") or ""),
            )
    except error.HTTPError as exc:
        body = exc.read(min(MAX_AUDIO_BYTES, 64 * 1024))
        return HttpResponse(
            status=int(exc.code),
            body=body,
            content_type=str(exc.headers.get("Content-Type") or ""),
        )


def wav_duration_seconds(data: bytes) -> tuple[float | None, str | None]:
    """Return PCM WAV duration when readable by the standard library."""

    try:
        with wave.open(BytesIO(data), "rb") as wav_file:
            frame_rate = wav_file.getframerate()
            frame_count = wav_file.getnframes()
            if frame_rate <= 0 or frame_count <= 0:
                raise ValueError("WAV enthält keine abspielbaren Frames.")
            return frame_count / frame_rate, None
    except (EOFError, ValueError, wave.Error) as exc:
        return None, str(exc)


def _is_wav(data: bytes) -> bool:
    return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE"


def run_request(
    config: EngineConfig,
    prompt: Prompt,
    repetition: int,
    *,
    transport: Transport = local_http_transport,
    clock: Clock = time.perf_counter,
) -> RunResult:
    """Execute and measure one complete request."""

    endpoint = build_endpoint(config)
    payload = build_payload(config, prompt.text)
    started = clock()
    try:
        response = transport(endpoint, payload, config.timeout_seconds)
        elapsed = max(0.0, clock() - started)
    except (OSError, TimeoutError, ValueError, error.URLError) as exc:
        elapsed = max(0.0, clock() - started)
        return RunResult(
            engine=config.engine,
            prompt_id=prompt.prompt_id,
            repetition=repetition,
            success=False,
            latency_seconds=elapsed,
            audio_duration_seconds=None,
            rtf=None,
            wav_readable=False,
            http_status=None,
            content_type="",
            bytes_received=0,
            error=f"{type(exc).__name__}: {exc}",
            wav_parse_error=None,
        )

    valid_status = 200 <= response.status < 300
    valid_wav = _is_wav(response.body)
    duration, wav_error = wav_duration_seconds(response.body) if valid_wav else (None, None)
    rtf = elapsed / duration if duration and duration > 0 else None
    success = valid_status and valid_wav
    failure = None
    if not valid_status:
        failure = f"HTTP {response.status}"
    elif not response.body:
        failure = "Leere TTS-Antwort"
    elif not valid_wav:
        failure = "Antwort ist kein RIFF/WAVE-Audio"

    return RunResult(
        engine=config.engine,
        prompt_id=prompt.prompt_id,
        repetition=repetition,
        success=success,
        latency_seconds=elapsed,
        audio_duration_seconds=duration,
        rtf=rtf,
        wav_readable=duration is not None,
        http_status=response.status,
        content_type=response.content_type,
        bytes_received=len(response.body),
        error=failure,
        wav_parse_error=wav_error,
    )


def percentile(values: Sequence[float], percent: float) -> float | None:
    """Linear-interpolated percentile for a small deterministic sample."""

    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percent
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize(runs: Sequence[RunResult]) -> dict[str, object]:
    """Build p50/p95 and error metrics from measured runs."""

    successful = [item for item in runs if item.success]
    latencies = [item.latency_seconds for item in successful]
    rtfs = [item.rtf for item in successful if item.rtf is not None]
    errors = Counter(item.error or "unknown" for item in runs if not item.success)
    total = len(runs)
    return {
        "run_count": total,
        "success_count": len(successful),
        "failure_count": total - len(successful),
        "success_rate": (len(successful) / total) if total else 0.0,
        "latency_p50_seconds": percentile(latencies, 0.50),
        "latency_p95_seconds": percentile(latencies, 0.95),
        "rtf_p50": percentile(rtfs, 0.50),
        "rtf_p95": percentile(rtfs, 0.95),
        "wav_readable_count": sum(1 for item in runs if item.wav_readable),
        "errors": dict(sorted(errors.items())),
    }


def benchmark(
    config: EngineConfig,
    prompts: Sequence[Prompt],
    *,
    repetitions: int,
    warmups: int,
    transport: Transport = local_http_transport,
    clock: Clock = time.perf_counter,
) -> BenchmarkReport:
    """Benchmark one engine; warmups are executed but excluded from results."""

    if not 1 <= repetitions <= MAX_REPETITIONS:
        raise ValueError(f"repetitions muss zwischen 1 und {MAX_REPETITIONS} liegen.")
    if not 0 <= warmups <= MAX_WARMUPS:
        raise ValueError(f"warmups muss zwischen 0 und {MAX_WARMUPS} liegen.")
    if not prompts:
        raise ValueError("Mindestens ein Benchmark-Text ist erforderlich.")
    if len(prompts) > MAX_PROMPTS:
        raise ValueError(f"Höchstens {MAX_PROMPTS} Benchmark-Texte sind erlaubt.")

    endpoint = build_endpoint(config)
    for warmup in range(warmups):
        run_request(
            config,
            prompts[warmup % len(prompts)],
            -(warmup + 1),
            transport=transport,
            clock=clock,
        )

    runs: list[RunResult] = []
    for prompt in prompts:
        for repetition in range(1, repetitions + 1):
            runs.append(
                run_request(
                    config,
                    prompt,
                    repetition,
                    transport=transport,
                    clock=clock,
                )
            )
    return BenchmarkReport(
        schema_version=1,
        engine=config.engine,
        endpoint=endpoint,
        repetitions=repetitions,
        warmups=warmups,
        prompt_count=len(prompts),
        summary=summarize(runs),
        runs=tuple(runs),
    )


def render_json(report: BenchmarkReport) -> str:
    """Render a stable JSON document."""

    payload = asdict(report)
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_csv(report: BenchmarkReport) -> str:
    """Render one CSV row per request with report metrics repeated per row."""

    output = StringIO(newline="")
    run_fields = list(asdict(report.runs[0]).keys()) if report.runs else [
        "engine",
        "prompt_id",
        "repetition",
        "success",
    ]
    summary_fields = [f"summary_{key}" for key in report.summary]
    fieldnames = run_fields + summary_fields
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for item in report.runs:
        row = asdict(item)
        for key, value in report.summary.items():
            row[f"summary_{key}"] = (
                json.dumps(value, ensure_ascii=False, sort_keys=True)
                if isinstance(value, dict)
                else value
            )
        writer.writerow(row)
    return output.getvalue()


def load_prompts(path: str | Path | None) -> tuple[Prompt, ...]:
    """Load a bounded local JSON corpus or return the built-in corpus."""

    if path is None:
        return tuple(Prompt(prompt_id, text) for prompt_id, text in DEFAULT_PROMPTS)
    corpus_path = Path(path)
    if corpus_path.stat().st_size > MAX_CORPUS_BYTES:
        raise ValueError("Corpus überschreitet das 1-MB-Limit.")
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Corpus muss eine JSON-Liste sein.")
    prompts: list[Prompt] = []
    for index, item in enumerate(data, start=1):
        if isinstance(item, str):
            prompt = Prompt(f"prompt_{index:03d}", item)
        elif isinstance(item, dict):
            prompt = Prompt(str(item.get("id") or f"prompt_{index:03d}"), str(item.get("text") or ""))
        else:
            raise ValueError("Corpus-Einträge müssen Text oder Objekte mit id/text sein.")
        if not PROMPT_ID_PATTERN.fullmatch(prompt.prompt_id):
            raise ValueError(
                "Corpus-ID muss 1 bis 64 Zeichen aus Buchstaben, Zahlen, Punkt, "
                "Unterstrich oder Bindestrich enthalten."
            )
        build_payload(
            EngineConfig(engine="orpheus", base_url="http://127.0.0.1"),
            prompt.text,
        )
        prompts.append(prompt)
    if not prompts or len(prompts) > MAX_PROMPTS:
        raise ValueError(f"Corpus muss 1 bis {MAX_PROMPTS} Texte enthalten.")
    return tuple(prompts)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark exactly one local German TTS engine. Run Orpheus and "
            "Voicebox separately on an 8 GB GPU."
        )
    )
    parser.add_argument("--engine", required=True, choices=("orpheus", "voicebox"))
    parser.add_argument("--base-url", help="Loopback base URL; defaults by engine.")
    parser.add_argument("--profile-id", default="", help="Required for Voicebox.")
    parser.add_argument(
        "--voicebox-engine",
        default="qwen",
        choices=("qwen",),
        help="Pinned to the qwen Base cloning engine for this pilot.",
    )
    parser.add_argument("--model-size", choices=("0.6B", "1.7B"), default="0.6B")
    parser.add_argument("--orpheus-model", default="orpheus")
    parser.add_argument("--orpheus-voice", default="jana")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--corpus", help="Optional bounded local JSON corpus.")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    parser.add_argument("--output", help="Optional output file; stdout when omitted.")
    return parser.parse_args(argv)


def config_from_args(args: argparse.Namespace) -> EngineConfig:
    if not 0 < args.timeout <= MAX_TIMEOUT_SECONDS:
        raise ValueError(f"timeout muss größer 0 und höchstens {MAX_TIMEOUT_SECONDS:g} sein.")
    if len(args.profile_id) > 128:
        raise ValueError("profile-id darf höchstens 128 Zeichen haben.")
    if len(args.orpheus_model) > 128 or len(args.orpheus_voice) > 128:
        raise ValueError("Orpheus-Modell und Stimme dürfen höchstens 128 Zeichen haben.")
    default_url = (
        "http://127.0.0.1:5005"
        if args.engine == "orpheus"
        else "http://127.0.0.1:17493"
    )
    config = EngineConfig(
        engine=args.engine,
        base_url=validate_loopback_base_url(args.base_url or default_url),
        timeout_seconds=args.timeout,
        orpheus_model=args.orpheus_model,
        orpheus_voice=args.orpheus_voice,
        voicebox_profile_id=args.profile_id,
        voicebox_engine=args.voicebox_engine,
        voicebox_model_size=args.model_size,
    )
    build_payload(config, "Sicherheitstest")
    return config


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = config_from_args(args)
        prompts = load_prompts(args.corpus)
        report = benchmark(
            config,
            prompts,
            repetitions=args.repetitions,
            warmups=args.warmups,
        )
        rendered = render_json(report) if args.format == "json" else render_csv(report)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8", newline="")
        else:
            sys.stdout.write(rendered)
        return 0 if report.summary["failure_count"] == 0 else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"Benchmark abgebrochen: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
