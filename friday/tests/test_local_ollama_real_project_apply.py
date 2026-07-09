"""Tests for the guarded local Ollama real project apply helper."""

from __future__ import annotations

from pathlib import Path

from friday import config
from friday.app.local_ollama_config_apply_guard import OLLAMA_CONFIG_APPLY_TOKEN
from friday.app import local_ollama_real_project_apply_guard as real_guard
from friday.app.local_ollama_real_project_apply import execute_local_ollama_real_project_apply


CONFIG_TEMPLATE = '''"""Temporary Friday config for real apply tests."""

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


def _validation_passes(_: Path) -> bool:
    return True


def _validation_fails(_: Path) -> bool:
    return False


def test_real_project_apply_blocks_by_default_without_writing(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    result = execute_local_ollama_real_project_apply(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert result.allowed is False
    assert result.persisted is False
    assert result.config_write_performed is False
    assert "real_project_apply_execution_not_requested" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before
    assert config.ENABLE_LOCAL_OLLAMA is True


def test_real_project_apply_requires_post_write_validation(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    result = execute_local_ollama_real_project_apply(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
        execute_write=True,
    )

    assert result.allowed is False
    assert "post_write_validation_required" in result.blocked_reasons
    assert result.config_write_performed is False
    assert config_path.read_text(encoding="utf-8") == before


def test_real_project_apply_writes_tmp_config_when_all_gates_pass(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    result = execute_local_ollama_real_project_apply(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
        execute_write=True,
        post_write_validation=_validation_passes,
    )

    assert result.allowed is True
    assert result.persisted is True
    assert result.status == "real_project_config_apply_completed"
    assert result.config_write_performed is True
    assert result.post_write_validation_passed is True
    assert result.rollback_performed is False
    assert result.preview_only is False
    assert result.external_call_used is False
    assert result.external_send_enabled is False
    assert result.cloud_fallback_allowed is False
    assert result.product_flow_connected is False
    assert result.backup_path is not None
    assert Path(result.backup_path).exists()

    written = config_path.read_text(encoding="utf-8")
    assert "ENABLE_LOCAL_OLLAMA = True" in written
    assert 'OLLAMA_MODEL = "llama3.1"' in written
    assert "ENABLE_REAL_EMAIL = False" in written
    assert "ENABLE_REAL_WHATSAPP = False" in written


def test_real_project_apply_rolls_back_when_validation_fails(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    result = execute_local_ollama_real_project_apply(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
        execute_write=True,
        post_write_validation=_validation_fails,
    )

    assert result.allowed is False
    assert result.persisted is False
    assert result.config_write_performed is True
    assert result.rollback_performed is True
    assert "post_write_validation_failed" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before


def test_real_project_apply_rolls_back_when_validation_raises(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    def _raises(_: Path) -> bool:
        raise RuntimeError("validation boom")

    result = execute_local_ollama_real_project_apply(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
        execute_write=True,
        post_write_validation=_raises,
    )

    assert result.allowed is False
    assert result.rollback_performed is True
    assert "post_write_validation_error" in result.blocked_reasons
    assert "RuntimeError" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before


def test_real_project_apply_blocks_wrong_token_without_writing(tmp_path, monkeypatch) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    result = execute_local_ollama_real_project_apply(
        model="llama3.1",
        approval_token="JA",
        scanner_smoke_passed=True,
        health_check_passed=True,
        execute_write=True,
        post_write_validation=_validation_passes,
    )

    assert result.allowed is False
    assert "dry_run_blocked" in result.blocked_reasons
    assert "Ollama config apply token is invalid" in result.blocked_reasons
    assert result.config_write_performed is False
    assert config_path.read_text(encoding="utf-8") == before
