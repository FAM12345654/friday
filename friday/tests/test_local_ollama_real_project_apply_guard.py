"""Tests for the read-only real project Ollama apply guard."""

from __future__ import annotations

from pathlib import Path

from friday import config
from friday.app.local_ollama_config_apply_guard import OLLAMA_CONFIG_APPLY_TOKEN
from friday.app import local_ollama_real_project_apply_guard as real_guard


CONFIG_TEMPLATE = '''"""Temporary Friday config for real project apply guard tests."""

ENABLE_REAL_EMAIL = False
ENABLE_REAL_WHATSAPP = False
ENABLE_REAL_SMS = False
ENABLE_REAL_CALENDAR = False
ENABLE_REAL_WEATHER = False
ENABLE_REAL_MUSIC = False
REQUIRE_USER_APPROVAL = True
USE_SQLITE_STORAGE = True

ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
'''


def _tmp_config(tmp_path: Path, text: str = CONFIG_TEMPLATE) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    config_path = tmp_path / "config.py"
    config_path.write_text(text, encoding="utf-8")
    return config_path


def test_real_project_apply_guard_allows_when_all_preconditions_pass(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(tmp_path)
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    guard = real_guard.build_local_ollama_real_project_apply_guard(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert guard.allowed is True
    assert guard.status == "ready_for_real_project_config_apply"
    assert guard.real_project_write_allowed is True
    assert guard.config_write_performed is False
    assert guard.preview_only is True
    assert guard.persisted is False
    assert guard.external_call_used is False
    assert guard.external_send_enabled is False
    assert guard.cloud_fallback_allowed is False
    assert guard.product_flow_connected is False
    assert guard.config_path_is_project_config is True
    assert guard.required_config_lines_present is True
    assert guard.required_config_lines_unique is True
    assert 'OLLAMA_MODEL = "llama3.1"' in guard.suggested_config_lines


def test_real_project_apply_guard_blocks_wrong_token(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    guard = real_guard.build_local_ollama_real_project_apply_guard(
        model="llama3.1",
        approval_token="JA",
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert guard.allowed is False
    assert guard.real_project_write_allowed is False
    assert "Ollama config apply gate is blocked" in guard.blocked_reasons
    assert "Ollama config apply token is invalid" in guard.blocked_reasons
    assert config.ENABLE_LOCAL_OLLAMA is True


def test_real_project_apply_guard_blocks_non_local_url(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    guard = real_guard.build_local_ollama_real_project_apply_guard(
        model="llama3.1",
        base_url="https://example.com",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert guard.allowed is False
    assert "Ollama base URL is not local" in guard.blocked_reasons


def test_real_project_apply_guard_blocks_non_project_config_path(tmp_path, monkeypatch) -> None:
    project_config = _tmp_config(tmp_path / "project")
    other_dir = tmp_path / "other"
    other_dir.mkdir()
    other_config = other_dir / "config.py"
    other_config.write_text(CONFIG_TEMPLATE, encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", project_config)

    guard = real_guard.build_local_ollama_real_project_apply_guard(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
        config_path=other_config,
    )

    assert guard.allowed is False
    assert guard.config_path_is_project_config is False
    assert "Config path is not Friday project config.py" in guard.blocked_reasons


def test_real_project_apply_guard_blocks_missing_required_config_line(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(
        tmp_path,
        CONFIG_TEMPLATE.replace('OLLAMA_MODEL = ""\n', ""),
    )
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    guard = real_guard.build_local_ollama_real_project_apply_guard(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert guard.allowed is False
    assert guard.required_config_lines_present is False
    assert "Required Ollama config line is missing" in guard.blocked_reasons
    assert "OLLAMA_MODEL" in guard.blocked_reasons


def test_real_project_apply_guard_blocks_duplicate_required_config_line(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(
        tmp_path,
        CONFIG_TEMPLATE + 'OLLAMA_MODEL = "duplicate"\n',
    )
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    guard = real_guard.build_local_ollama_real_project_apply_guard(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert guard.allowed is False
    assert guard.required_config_lines_unique is False
    assert "Required Ollama config line is duplicated" in guard.blocked_reasons
    assert "OLLAMA_MODEL" in guard.blocked_reasons


def test_real_project_apply_guard_blocks_invalid_timeout(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    guard = real_guard.build_local_ollama_real_project_apply_guard(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
        timeout_seconds=0,
    )

    assert guard.allowed is False
    assert "Ollama timeout seconds is invalid" in guard.blocked_reasons
