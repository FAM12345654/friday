"""Tests for local Ollama config apply guard."""

from __future__ import annotations

from friday import config
from friday.app.local_ollama_config_apply_guard import (
    OLLAMA_CONFIG_APPLY_TOKEN,
    build_local_ollama_config_apply_gate,
)
from friday.app.local_ollama_config_preview import build_local_ollama_config_preview


def _ready_preview():
    return build_local_ollama_config_preview(
        model="llama3.1",
        base_url="http://localhost:11434",
        enable_requested=True,
    )


def test_ollama_config_apply_gate_allows_manual_edit_when_all_checks_pass() -> None:
    before_enabled = config.ENABLE_LOCAL_OLLAMA
    before_model = config.OLLAMA_MODEL
    gate = build_local_ollama_config_apply_gate(
        preview=_ready_preview(),
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert gate.allowed is True
    assert gate.status == "ready_for_manual_config_edit"
    assert gate.manual_edit_required is True
    assert gate.config_write_performed is False
    assert gate.external_send_enabled is False
    assert gate.cloud_fallback_allowed is False
    assert gate.preview_only is True
    assert config.ENABLE_LOCAL_OLLAMA is before_enabled
    assert config.OLLAMA_MODEL == before_model


def test_ollama_config_apply_gate_blocks_wrong_token() -> None:
    gate = build_local_ollama_config_apply_gate(
        preview=_ready_preview(),
        approval_token="JA",
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert gate.allowed is False
    assert "Ollama config apply token is invalid" in gate.blocked_reasons
    assert gate.config_write_performed is False


def test_ollama_config_apply_gate_blocks_failed_safety_smoke() -> None:
    gate = build_local_ollama_config_apply_gate(
        preview=_ready_preview(),
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=False,
        health_check_passed=True,
    )

    assert gate.allowed is False
    assert "Safety smoke must pass before Ollama config apply" in gate.blocked_reasons


def test_ollama_config_apply_gate_blocks_failed_health_check() -> None:
    gate = build_local_ollama_config_apply_gate(
        preview=_ready_preview(),
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=False,
    )

    assert gate.allowed is False
    assert "Local Ollama health check must pass before config apply" in gate.blocked_reasons


def test_ollama_config_apply_gate_blocks_invalid_preview() -> None:
    preview = build_local_ollama_config_preview(model="", base_url="http://localhost:11434")
    gate = build_local_ollama_config_apply_gate(
        preview=preview,
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert gate.allowed is False
    assert "Ollama config preview is not enable-ready" in gate.blocked_reasons
    assert "Ollama model is not configured" in gate.blocked_reasons
