"""Tests for preview-only local model health checks."""

from __future__ import annotations

from dataclasses import replace

from friday.app.local_model_health_preview import build_ollama_health_check_preview
from friday.app.local_model_settings import build_local_model_settings_preview


def test_ollama_health_preview_blocks_default_disabled_settings() -> None:
    settings = build_local_model_settings_preview("ollama")

    preview = build_ollama_health_check_preview(settings)

    assert preview.executed is False
    assert preview.preview_only is True
    assert preview.external_call_used is False
    assert "ollama_disabled" in preview.blocked_reasons


def test_ollama_health_preview_allows_only_127_localhost_without_execution() -> None:
    settings = replace(
        build_local_model_settings_preview("ollama"),
        ollama_enabled=True,
        base_url="http://127.0.0.1:11434",
        model="local",
    )

    preview = build_ollama_health_check_preview(settings)

    assert preview.would_check_localhost is True
    assert preview.endpoint == "http://127.0.0.1:11434/api/tags"
    assert preview.executed is False
    assert preview.external_call_used is False
    assert preview.product_flow_connected is False


def test_ollama_health_preview_blocks_non_127_localhost() -> None:
    settings = replace(
        build_local_model_settings_preview("ollama"),
        ollama_enabled=True,
        base_url="http://localhost:11434",
        model="local",
    )

    preview = build_ollama_health_check_preview(settings)

    assert preview.would_check_localhost is False
    assert "base_url_not_127_localhost" in preview.blocked_reasons


def test_ollama_health_preview_blocks_cloud_fallback() -> None:
    settings = replace(
        build_local_model_settings_preview("ollama"),
        ollama_enabled=True,
        base_url="http://127.0.0.1:11434",
        cloud_fallback_allowed=True,
    )

    preview = build_ollama_health_check_preview(settings)

    assert preview.would_check_localhost is False
    assert "cloud_fallback_requested" in preview.blocked_reasons
