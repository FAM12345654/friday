"""Guarded localhost-only Ollama runtime helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping
from urllib import error, request
from urllib.parse import urlparse

from friday import config
from friday.app.model_output_validator import validate_model_json


@dataclass(frozen=True)
class OllamaHealthResult:
    """Structured health check result for local Ollama."""

    base_url: str
    endpoint: str
    available: bool
    refused: bool
    external_call_used: bool
    error: str | None


@dataclass(frozen=True)
class OllamaGenerationResult:
    """Validated local Ollama generation result."""

    output: dict[str, Any]
    validation_errors: tuple[str, ...]
    external_call_used: bool
    error: str | None


def is_local_ollama_url(base_url: str) -> bool:
    """Return True only for explicit localhost/127.0.0.1 HTTP URLs."""
    parsed = urlparse((base_url or "").strip())
    return parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}


def check_ollama_health(
    base_url: str | None = None,
    timeout_seconds: int | None = None,
) -> OllamaHealthResult:
    """Check local Ollama availability with a strict localhost guard."""
    resolved_base_url = (base_url or config.OLLAMA_BASE_URL).strip().rstrip("/")
    endpoint = f"{resolved_base_url}/api/tags" if resolved_base_url else ""
    if not is_local_ollama_url(resolved_base_url):
        return OllamaHealthResult(
            base_url=resolved_base_url,
            endpoint=endpoint,
            available=False,
            refused=True,
            external_call_used=False,
            error="Ollama Health Check erlaubt nur 127.0.0.1 oder localhost.",
        )

    try:
        with request.urlopen(endpoint, timeout=timeout_seconds or config.OLLAMA_TIMEOUT_SECONDS) as response:
            return OllamaHealthResult(
                base_url=resolved_base_url,
                endpoint=endpoint,
                available=200 <= int(response.status) < 300,
                refused=False,
                external_call_used=True,
                error=None,
            )
    except (OSError, error.URLError, TimeoutError) as exc:
        return OllamaHealthResult(
            base_url=resolved_base_url,
            endpoint=endpoint,
            available=False,
            refused=False,
            external_call_used=True,
            error=str(exc),
        )


def generate_ollama_json(
    prompt: str,
    schema: Mapping[str, Any],
    base_url: str | None = None,
    model: str | None = None,
    timeout_seconds: int | None = None,
) -> OllamaGenerationResult:
    """Call local Ollama and validate the JSON response before returning it."""
    resolved_base_url = (base_url or config.OLLAMA_BASE_URL).strip().rstrip("/")
    resolved_model = (model or config.OLLAMA_MODEL).strip()
    if not is_local_ollama_url(resolved_base_url):
        return OllamaGenerationResult({}, (), False, "Ollama erlaubt nur lokale URLs.")
    if not resolved_model:
        return OllamaGenerationResult({}, (), False, "Ollama Modell ist nicht gesetzt.")

    endpoint = f"{resolved_base_url}/api/generate"
    payload = json.dumps(
        {
            "model": resolved_model,
            "prompt": (prompt or "").strip(),
            "format": "json",
            "stream": False,
        }
    ).encode("utf-8")
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout_seconds or config.OLLAMA_TIMEOUT_SECONDS) as response:
            raw = response.read().decode("utf-8")
    except (OSError, error.URLError, TimeoutError) as exc:
        return OllamaGenerationResult({}, (), True, str(exc))

    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError:
        return OllamaGenerationResult({}, ("Modellantwort ist kein gültiges JSON.",), True, None)

    response_text = envelope.get("response") if isinstance(envelope, dict) else None
    validation = validate_model_json(schema, response_text)
    return OllamaGenerationResult(
        output=validation.data,
        validation_errors=tuple(validation.errors),
        external_call_used=True,
        error=None if validation.is_valid else "Modellantwort wurde durch den Validator blockiert.",
    )
