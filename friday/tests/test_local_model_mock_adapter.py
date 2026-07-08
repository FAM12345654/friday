"""Tests for the local model mock adapter."""

from __future__ import annotations

from friday.app.local_model_mock import (
    LocalModelMockAdapter,
)


def test_local_model_mock_adapter_is_available_without_external_call() -> None:
    adapter = LocalModelMockAdapter()
    readiness = adapter.get_readiness_status()
    assert adapter.is_available() is True
    assert readiness.mode_supported is True
    assert readiness.fallback_status == "local_rule_based"
    assert readiness.fallback_path_defined is True


def test_local_model_mock_adapter_returns_deterministic_mock_result() -> None:
    adapter = LocalModelMockAdapter()
    result = adapter.generate("Hallo")

    assert result.provider == "mock-local"
    assert result.model == "mock-readiness"
    assert result.is_mock is True
    assert result.external_call_used is False
    assert "Lokale Mock-Antwort" in result.response
    assert result.prompt == "Hallo"


def test_local_model_mock_adapter_handles_empty_prompt() -> None:
    adapter = LocalModelMockAdapter()
    result = adapter.generate("   ")

    assert result.prompt == ""
    assert result.is_mock is True
    assert result.external_call_used is False
    assert "Leere Eingabe erkannt." in result.response


def test_local_model_mock_adapter_readiness_flags_show_local_policy() -> None:
    adapter = LocalModelMockAdapter()
    readiness = adapter.get_readiness_status()

    assert readiness.provider_config_present is True
    assert readiness.approval_flow_available is True
    assert readiness.safety_flags_locked is True
    assert readiness.fallback_status == adapter.get_fallback_status()
