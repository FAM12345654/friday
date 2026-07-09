"""Tests for local Ollama config preview."""

from __future__ import annotations

from friday import config
from friday.app.local_ollama_config_preview import build_local_ollama_config_preview


def test_ollama_config_preview_accepts_local_model_without_mutating_config() -> None:
    before_enabled = config.ENABLE_LOCAL_OLLAMA
    before_model = config.OLLAMA_MODEL

    preview = build_local_ollama_config_preview(
        model=" llama3.1 ",
        base_url="http://localhost:11434/",
    )

    assert preview.normalized_model == "llama3.1"
    assert preview.normalized_base_url == "http://localhost:11434"
    assert preview.base_url_allowed is True
    assert preview.would_enable_ollama is True
    assert preview.external_call_used is False
    assert preview.external_send_enabled is False
    assert preview.cloud_fallback_allowed is False
    assert preview.preview_only is True
    assert config.ENABLE_LOCAL_OLLAMA is before_enabled
    assert config.OLLAMA_MODEL == before_model


def test_ollama_config_preview_blocks_missing_model() -> None:
    preview = build_local_ollama_config_preview(model=" ", base_url="http://localhost:11434")

    assert preview.would_enable_ollama is False
    assert preview.model_configured is False
    assert "Ollama model is not configured" in preview.blocked_reasons


def test_ollama_config_preview_blocks_non_local_url() -> None:
    preview = build_local_ollama_config_preview(model="llama3.1", base_url="https://example.com")

    assert preview.would_enable_ollama is False
    assert preview.base_url_allowed is False
    assert "Ollama base URL is not local" in preview.blocked_reasons


def test_ollama_config_preview_blocks_when_enable_not_requested() -> None:
    preview = build_local_ollama_config_preview(
        model="llama3.1",
        base_url="http://127.0.0.1:11434",
        enable_requested=False,
    )

    assert preview.would_enable_ollama is False
    assert "Ollama enable was not requested" in preview.blocked_reasons


def test_ollama_config_preview_suggests_exact_config_lines() -> None:
    preview = build_local_ollama_config_preview(model="llama3.1")

    assert 'OLLAMA_MODEL = "llama3.1"' in preview.suggested_config_lines
    assert 'OLLAMA_BASE_URL = "http://localhost:11434"' in preview.suggested_config_lines
    assert "ENABLE_LOCAL_OLLAMA = True" in preview.suggested_config_lines
