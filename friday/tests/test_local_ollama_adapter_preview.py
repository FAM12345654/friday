"""Tests for the preview-only local Ollama adapter."""

from __future__ import annotations

import pytest

import friday.config as config
from friday.app.local_ollama_adapter_preview import (
    OllamaAdapterPreviewConfig,
    OllamaLocalAdapterPreview,
    default_ollama_preview_config,
    validate_ollama_preview_config,
)


def test_default_ollama_preview_config_reflects_enabled_local_config() -> None:
    preview_config = default_ollama_preview_config()

    assert preview_config.enabled is True
    assert preview_config.base_url == config.OLLAMA_BASE_URL
    assert preview_config.model == "qwen3:8b"
    assert preview_config.timeout_seconds == 30
    assert preview_config.allow_cloud_fallback is False


def test_ollama_preview_health_check_does_not_use_network() -> None:
    adapter = OllamaLocalAdapterPreview()
    health = adapter.health_check()

    assert health.enabled is True
    assert health.available is False
    assert health.preview_only is True
    assert health.external_call_used is False
    assert health.cloud_fallback_used is False


def test_ollama_preview_builds_request_without_execution() -> None:
    adapter = OllamaLocalAdapterPreview(
        OllamaAdapterPreviewConfig(
            enabled=True,
            base_url="http://127.0.0.1:11434",
            model="llama-local",
            timeout_seconds=5,
            allow_cloud_fallback=False,
        )
    )

    request = adapter.build_json_request_preview(
        prompt="Bitte als JSON zusammenfassen",
        schema={"type": "object"},
    )

    assert request.endpoint == "http://127.0.0.1:11434/api/generate"
    assert request.payload["model"] == "llama-local"
    assert request.payload["prompt"] == "Bitte als JSON zusammenfassen"
    assert request.payload["format"] == "json"
    assert request.would_call_local is True
    assert request.executed is False
    assert request.external_call_used is False
    assert request.product_flow_connected is False


def test_ollama_preview_request_remains_non_executing_even_when_enabled() -> None:
    adapter = OllamaLocalAdapterPreview(
        OllamaAdapterPreviewConfig(
            enabled=True,
            base_url="http://localhost:11434/",
            model="",
            timeout_seconds=5,
            allow_cloud_fallback=False,
        )
    )

    request = adapter.build_json_request_preview(
        prompt="  Bitte JSON  ",
        schema={"required": ["summary"]},
    )

    assert request.endpoint == "http://localhost:11434/api/generate"
    assert request.payload["model"] == "not-configured"
    assert request.payload["prompt"] == "Bitte JSON"
    assert request.payload["stream"] is False
    assert request.payload["schema"] == {"required": ["summary"]}
    assert request.would_call_local is False
    assert request.executed is False
    assert request.preview_only is True
    assert request.external_call_used is False
    assert request.cloud_fallback_used is False
    assert request.product_flow_connected is False


def test_ollama_preview_rejects_too_short_timeout() -> None:
    with pytest.raises(ValueError):
        validate_ollama_preview_config(
            OllamaAdapterPreviewConfig(
                enabled=True,
                base_url="http://localhost:11434",
                model="local",
                timeout_seconds=0,
                allow_cloud_fallback=False,
            )
        )


def test_ollama_preview_rejects_non_local_base_url() -> None:
    with pytest.raises(ValueError):
        validate_ollama_preview_config(
            OllamaAdapterPreviewConfig(
                enabled=True,
                base_url="https://example.com",
                model="remote",
                timeout_seconds=5,
                allow_cloud_fallback=False,
            )
        )


def test_ollama_preview_rejects_cloud_fallback() -> None:
    with pytest.raises(ValueError):
        validate_ollama_preview_config(
            OllamaAdapterPreviewConfig(
                enabled=True,
                base_url="http://localhost:11434",
                model="local",
                timeout_seconds=5,
                allow_cloud_fallback=True,
            )
        )


def test_ollama_preview_enabled_health_still_skips_live_check() -> None:
    adapter = OllamaLocalAdapterPreview(
        OllamaAdapterPreviewConfig(
            enabled=True,
            base_url="http://localhost:11434",
            model="local",
            timeout_seconds=5,
            allow_cloud_fallback=False,
        )
    )
    health = adapter.health_check()

    assert health.enabled is True
    assert health.available is False
    assert health.external_call_used is False
    assert "kein Live-Check" in health.message
