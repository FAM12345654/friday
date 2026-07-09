"""Tests for Friday API Ollama config preview endpoint."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location("friday_api_main_for_ollama_config_test", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_api_ollama_config_preview_is_read_only_and_local() -> None:
    api = _load_api_module()

    response = api.get_ollama_config_preview(
        model="llama3.1",
        base_url="http://localhost:11434",
        enable_requested=True,
    )

    assert response["ok"] is True
    payload = response["data"]
    assert payload["normalized_model"] == "llama3.1"
    assert payload["base_url_allowed"] is True
    assert payload["would_enable_ollama"] is True
    assert payload["external_call_used"] is False
    assert payload["external_send_enabled"] is False
    assert payload["preview_only"] is True
