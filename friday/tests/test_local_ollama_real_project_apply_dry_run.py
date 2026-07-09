"""Tests for local Ollama real project config apply dry run."""

from __future__ import annotations

from pathlib import Path

from friday import config
from friday.app.local_ollama_config_apply_guard import OLLAMA_CONFIG_APPLY_TOKEN
from friday.app import local_ollama_real_project_apply_guard as real_guard
from friday.app.local_ollama_real_project_apply_dry_run import (
    ROLLBACK_CONFIG_LINES,
    build_local_ollama_real_project_apply_dry_run,
)


CONFIG_TEMPLATE = '''"""Temporary Friday config for dry-run tests."""

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


def test_real_project_apply_dry_run_lists_planned_changes_without_writing(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    dry_run = build_local_ollama_real_project_apply_dry_run(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert dry_run.allowed is True
    assert dry_run.status == "ready_for_real_project_config_apply_dry_run"
    assert dry_run.config_write_performed is False
    assert dry_run.preview_only is True
    assert dry_run.persisted is False
    assert dry_run.external_call_used is False
    assert dry_run.external_send_enabled is False
    assert dry_run.cloud_fallback_allowed is False
    assert dry_run.product_flow_connected is False
    assert config_path.read_text(encoding="utf-8") == before

    planned = {change.key: change for change in dry_run.planned_changes}
    assert planned["ENABLE_LOCAL_OLLAMA"].current_line == "ENABLE_LOCAL_OLLAMA = False"
    assert planned["ENABLE_LOCAL_OLLAMA"].planned_line == "ENABLE_LOCAL_OLLAMA = True"
    assert planned["ENABLE_LOCAL_OLLAMA"].changed is True
    assert planned["OLLAMA_MODEL"].current_line == 'OLLAMA_MODEL = ""'
    assert planned["OLLAMA_MODEL"].planned_line == 'OLLAMA_MODEL = "llama3.1"'
    assert dry_run.rollback_config_lines == ROLLBACK_CONFIG_LINES


def test_real_project_apply_dry_run_blocks_wrong_token_without_diff(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    dry_run = build_local_ollama_real_project_apply_dry_run(
        model="llama3.1",
        approval_token="JA",
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert dry_run.allowed is False
    assert dry_run.planned_changes == ()
    assert "Ollama config apply token is invalid" in dry_run.guard_blocked_reasons
    assert config_path.read_text(encoding="utf-8") == before
    assert config.ENABLE_LOCAL_OLLAMA is True


def test_real_project_apply_dry_run_blocks_non_local_url_without_writing(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(tmp_path)
    before = config_path.read_text(encoding="utf-8")
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    dry_run = build_local_ollama_real_project_apply_dry_run(
        model="llama3.1",
        base_url="https://example.com",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert dry_run.allowed is False
    assert "Ollama base URL is not local" in dry_run.guard_blocked_reasons
    assert dry_run.config_write_performed is False
    assert config_path.read_text(encoding="utf-8") == before


def test_real_project_apply_dry_run_blocks_failed_safety_smoke(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(tmp_path)
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    dry_run = build_local_ollama_real_project_apply_dry_run(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=False,
        health_check_passed=True,
    )

    assert dry_run.allowed is False
    assert "Safety smoke must pass before Ollama config apply" in dry_run.guard_blocked_reasons


def test_real_project_apply_dry_run_blocks_missing_config_line(
    tmp_path,
    monkeypatch,
) -> None:
    config_path = _tmp_config(
        tmp_path,
        CONFIG_TEMPLATE.replace('OLLAMA_MODEL = ""\n', ""),
    )
    monkeypatch.setattr(real_guard, "PROJECT_CONFIG_PATH", config_path)

    dry_run = build_local_ollama_real_project_apply_dry_run(
        model="llama3.1",
        approval_token=OLLAMA_CONFIG_APPLY_TOKEN,
        scanner_smoke_passed=True,
        health_check_passed=True,
    )

    assert dry_run.allowed is False
    assert dry_run.planned_changes == ()
    assert "Required Ollama config line is missing" in dry_run.guard_blocked_reasons
    assert "OLLAMA_MODEL" in dry_run.guard_blocked_reasons
