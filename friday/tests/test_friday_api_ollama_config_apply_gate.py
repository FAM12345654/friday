"""Tests for Friday API Ollama config apply gate endpoint."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_ollama_apply_gate_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_api_ollama_config_apply_gate_is_guard_only() -> None:
    api = _load_api_module()

    response = api.get_ollama_config_apply_gate(
        api.OllamaConfigApplyGateRequest(
            model="llama3.1",
            base_url="http://localhost:11434",
            approval_token="OLLAMA AKTIVIEREN",
            scanner_smoke_passed=True,
            health_check_passed=True,
        )
    )

    assert response["ok"] is True
    payload = response["data"]
    assert payload["allowed"] is True
    assert payload["manual_edit_required"] is True
    assert payload["config_write_performed"] is False
    assert payload["external_send_enabled"] is False
    assert payload["preview_only"] is True
