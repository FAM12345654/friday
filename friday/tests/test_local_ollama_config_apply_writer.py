"""Tests for the guarded local Ollama config writer."""

from __future__ import annotations

from pathlib import Path

from friday import config
from friday.app.local_ollama_config_apply_guard import OLLAMA_CONFIG_APPLY_TOKEN
from friday.app.local_ollama_config_apply_writer import apply_local_ollama_config


CONFIG_TEMPLATE = '''"""Temporary Friday config for writer tests."""

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
    config_dir = tmp_path / "friday"
    config_dir.mkdir()
    config_path = config_dir / "config.py"
    config_path.write_text(text, encoding="utf-8")
    return config_path


def test_apply_local_ollama_config_writes_only_allowed_lines_to_tmp_config(tmp_path) -> None:
    config_path = _tmp_config(tmp_path)

    result = apply_local_ollama_config(
        config_path=config_path,
        model=" llama3.1 ",
        base_url="http://localhost:11434/",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is True
    assert result.persisted is True
    assert result.config_write_performed is True
    assert result.preview_only is False
    assert result.external_call_used is False
    assert result.external_send_enabled is False
    assert result.cloud_fallback_allowed is False
    assert result.product_flow_connected is False
    assert result.backup_path is not None
    assert Path(result.backup_path).exists()

    written = config_path.read_text(encoding="utf-8")
    assert "ENABLE_LOCAL_OLLAMA = True" in written
    assert 'OLLAMA_BASE_URL = "http://localhost:11434"' in written
    assert 'OLLAMA_MODEL = "llama3.1"' in written
    assert "OLLAMA_TIMEOUT_SECONDS = 5" in written
    assert "ENABLE_REAL_EMAIL = False" in written
    assert "ENABLE_REAL_WHATSAPP = False" in written


def test_apply_local_ollama_config_blocks_wrong_token_without_writing(tmp_path) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")

    result = apply_local_ollama_config(
        config_path=config_path,
        model="llama3.1",
        approval_token="JA",
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is False
    assert result.config_write_performed is False
    assert "guard_blocked" in result.blocked_reasons
    assert "Ollama config apply token is invalid" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before


def test_apply_local_ollama_config_blocks_non_local_url_without_writing(tmp_path) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")

    result = apply_local_ollama_config(
        config_path=config_path,
        model="llama3.1",
        base_url="https://example.com",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is False
    assert "Ollama base URL is not local" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before


def test_apply_local_ollama_config_blocks_missing_model_without_writing(tmp_path) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")

    result = apply_local_ollama_config(
        config_path=config_path,
        model=" ",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is False
    assert "Ollama model is not configured" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before


def test_apply_local_ollama_config_blocks_missing_required_line(tmp_path) -> None:
    config_path = _tmp_config(
        tmp_path,
        CONFIG_TEMPLATE.replace('OLLAMA_MODEL = ""\n', ""),
    )
    before = config_path.read_text(encoding="utf-8")

    result = apply_local_ollama_config(
        config_path=config_path,
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is False
    assert "required_config_line_missing" in result.blocked_reasons
    assert "OLLAMA_MODEL" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before


def test_apply_local_ollama_config_blocks_duplicate_required_line(tmp_path) -> None:
    config_path = _tmp_config(
        tmp_path,
        CONFIG_TEMPLATE + 'OLLAMA_MODEL = "duplicate"\n',
    )
    before = config_path.read_text(encoding="utf-8")

    result = apply_local_ollama_config(
        config_path=config_path,
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is False
    assert "required_config_line_duplicate" in result.blocked_reasons
    assert "OLLAMA_MODEL" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before


def test_apply_local_ollama_config_blocks_real_project_config_by_default() -> None:
    before_enabled = config.ENABLE_LOCAL_OLLAMA
    before_model = config.OLLAMA_MODEL

    result = apply_local_ollama_config(
        config_path=config.PACKAGE_DIR / "config.py",
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is False
    assert "project_config_write_blocked" in result.blocked_reasons
    assert result.config_write_performed is False
    assert config.ENABLE_LOCAL_OLLAMA is before_enabled
    assert config.OLLAMA_MODEL == before_model
