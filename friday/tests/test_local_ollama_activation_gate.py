"""Tests for the local Ollama activation gate."""

from __future__ import annotations

from friday import config
from friday.app.local_ollama_activation_gate import build_local_ollama_activation_gate
from friday.app.local_ollama_runtime import OllamaHealthResult


def test_ollama_activation_gate_defaults_to_mock_when_disabled() -> None:
    gate = build_local_ollama_activation_gate()

    assert gate.status == "mock_active_ollama_disabled"
    assert gate.active_provider == "mock"
    assert gate.mock_fallback_active is True
    assert gate.ollama_enabled is False
    assert gate.product_flow_connected is True
    assert gate.external_send_enabled is False
    assert gate.cloud_fallback_allowed is False
    assert "ENABLE_LOCAL_OLLAMA is False" in gate.blocked_reasons


def test_ollama_activation_gate_blocks_non_local_url(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", True)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")
    monkeypatch.setattr(config, "OLLAMA_BASE_URL", "https://example.com")

    gate = build_local_ollama_activation_gate(run_health_check=True)

    assert gate.status == "blocked_non_local_url"
    assert gate.active_provider == "mock"
    assert gate.base_url_allowed is False
    assert gate.external_call_used is False
    assert "Ollama base URL is not local" in gate.blocked_reasons


def test_ollama_activation_gate_reports_missing_model(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", True)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "")

    gate = build_local_ollama_activation_gate()

    assert gate.status == "mock_active_model_missing"
    assert gate.model_configured is False
    assert "Ollama model is not configured" in gate.blocked_reasons


def test_ollama_activation_gate_requires_explicit_health_check(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", True)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")
    monkeypatch.setattr(config, "OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    gate = build_local_ollama_activation_gate(run_health_check=False)

    assert gate.status == "mock_active_health_not_checked"
    assert gate.active_provider == "mock"
    assert gate.external_call_used is False
    assert "Ollama health check was not requested" in gate.blocked_reasons


def test_ollama_activation_gate_allows_ready_local_ollama_after_health_check(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", True)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")
    monkeypatch.setattr(config, "OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    def _health(base_url: str, timeout_seconds: int) -> OllamaHealthResult:
        return OllamaHealthResult(
            base_url=base_url,
            endpoint=f"{base_url}/api/tags",
            available=True,
            refused=False,
            external_call_used=True,
            error=None,
        )

    gate = build_local_ollama_activation_gate(run_health_check=True, health_check=_health)

    assert gate.status == "ollama_ready_for_local_drafts"
    assert gate.active_provider == "ollama"
    assert gate.mock_fallback_active is False
    assert gate.health_available is True
    assert gate.external_call_used is True
    assert gate.blocked_reasons == ()
    assert gate.external_send_enabled is False


def test_ollama_activation_gate_falls_back_when_health_fails(monkeypatch) -> None:
    monkeypatch.setattr(config, "ENABLE_LOCAL_OLLAMA", True)
    monkeypatch.setattr(config, "OLLAMA_MODEL", "local")
    monkeypatch.setattr(config, "OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    def _health(base_url: str, timeout_seconds: int) -> OllamaHealthResult:
        return OllamaHealthResult(
            base_url=base_url,
            endpoint=f"{base_url}/api/tags",
            available=False,
            refused=False,
            external_call_used=True,
            error="connection refused",
        )

    gate = build_local_ollama_activation_gate(run_health_check=True, health_check=_health)

    assert gate.status == "mock_active_ollama_unavailable"
    assert gate.active_provider == "mock"
    assert gate.health_error == "connection refused"
    assert "Ollama health check is not available" in gate.blocked_reasons
