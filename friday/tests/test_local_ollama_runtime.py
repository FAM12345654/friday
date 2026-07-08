"""Tests for guarded local Ollama runtime helpers."""

from __future__ import annotations

import json
from types import SimpleNamespace

from friday.app.local_ollama_runtime import (
    check_ollama_health,
    generate_ollama_json,
    is_local_ollama_url,
)


class _Response:
    status = 200

    def __init__(self, body: str = "{}") -> None:
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self.body.encode("utf-8")


def test_is_local_ollama_url_allows_only_local_http() -> None:
    assert is_local_ollama_url("http://127.0.0.1:11434") is True
    assert is_local_ollama_url("http://localhost:11434") is True
    assert is_local_ollama_url("https://example.com") is False


def test_check_ollama_health_refuses_non_local_url() -> None:
    result = check_ollama_health("https://example.com", timeout_seconds=1)

    assert result.available is False
    assert result.refused is True
    assert result.external_call_used is False


def test_check_ollama_health_handles_unreachable_port(monkeypatch) -> None:
    def _raise(*args, **kwargs):
        raise OSError("connection refused")

    monkeypatch.setattr("friday.app.local_ollama_runtime.request.urlopen", _raise)
    result = check_ollama_health("http://127.0.0.1:11434", timeout_seconds=1)

    assert result.available is False
    assert result.refused is False
    assert result.external_call_used is True
    assert "connection refused" in (result.error or "")


def test_generate_ollama_json_validates_response(monkeypatch) -> None:
    envelope = json.dumps({"response": json.dumps({"summary": "ok"})})
    monkeypatch.setattr(
        "friday.app.local_ollama_runtime.request.urlopen",
        lambda *args, **kwargs: _Response(envelope),
    )

    result = generate_ollama_json(
        prompt="Hallo",
        schema={"required": ["summary"], "properties": {"summary": "str"}},
        base_url="http://127.0.0.1:11434",
        model="local",
        timeout_seconds=1,
    )

    assert result.output == {"summary": "ok"}
    assert result.validation_errors == ()
    assert result.external_call_used is True
    assert result.error is None
