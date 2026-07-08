"""Tests for local model settings preview."""

from __future__ import annotations

from friday.app.local_model_settings import (
    build_default_local_model_settings,
    build_local_model_settings_preview,
)


def test_default_local_model_settings_keep_mock_default() -> None:
    settings = build_default_local_model_settings()

    assert settings.provider == "mock"
    assert settings.mock_is_default is True
    assert settings.ollama_enabled is False
    assert settings.cloud_fallback_allowed is False
    assert settings.product_flow_connected is False
    assert settings.preview_only is True
    assert settings.persisted is False
    assert settings.external_call_used is False


def test_ollama_settings_preview_does_not_connect_product_flow() -> None:
    settings = build_local_model_settings_preview("ollama")

    assert settings.provider == "ollama"
    assert settings.mock_is_default is True
    assert settings.cloud_fallback_allowed is False
    assert settings.product_flow_connected is False
    assert settings.preview_only is True
    assert settings.external_call_used is False
