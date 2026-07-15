"""Regression tests for guarded API activation writers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from friday.app.email_activation_gate import EmailActivationGate
from friday.app.whatsapp_bridge_activation_gate import (
    WhatsAppBridgeApplyResult,
    apply_whatsapp_bridge_read_activation_to_config,
)


def _load_api_module():
    module_path = Path(__file__).resolve().parents[2] / "friday-api" / "main.py"
    spec = importlib.util.spec_from_file_location("friday_api_activation_writes", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _passing_smoke():
    return SimpleNamespace(passed=True, checks=())


def test_email_activation_api_executes_writer_and_updates_runtime(monkeypatch) -> None:
    api = _load_api_module()
    captured = {}

    def _apply(**kwargs):
        captured.update(kwargs)
        return EmailActivationGate(
            allowed=True,
            status="email_activation_applied",
            approval_token_required="EMAIL AKTIVIEREN",
            account_connected=True,
            last_test_ok=True,
            scanner_smoke_passed=True,
            config_write_performed=True,
            blocked_reasons=(),
            preview_only=False,
            persisted=True,
            external_send_enabled=True,
        )

    monkeypatch.setattr(api, "_run_server_safety_smoke", _passing_smoke)
    monkeypatch.setattr(api, "apply_email_activation_to_config", _apply)
    monkeypatch.setattr(api.config, "ENABLE_REAL_EMAIL", False)

    response = TestClient(api.app).post(
        "/api/accounts/email/activation-gate",
        json={"approval_token": "EMAIL AKTIVIEREN", "execute_write": True},
    )

    assert response.status_code == 200
    assert response.json()["data"]["config_write_performed"] is True
    assert captured["execute_write"] is True
    assert api.config.ENABLE_REAL_EMAIL is True


def test_whatsapp_activation_api_executes_guarded_writer(monkeypatch) -> None:
    api = _load_api_module()
    captured = {}

    def _apply(**kwargs):
        captured.update(kwargs)
        return WhatsAppBridgeApplyResult(
            allowed=True,
            applied=True,
            message="applied",
            backup_path="config.py.whatsapp_bridge_backup",
            blocked_reasons=(),
        )

    monkeypatch.setattr(api, "_run_server_safety_smoke", _passing_smoke)
    monkeypatch.setattr(api, "apply_whatsapp_bridge_read_activation_to_config", _apply)

    response = TestClient(api.app).post(
        "/api/whatsapp/activation-gate",
        json={
            "approval_token": "WHATSAPP BRIDGE AKTIVIEREN",
            "execute_write": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["applied"] is True
    assert captured["execute_write"] is True


def test_whatsapp_activation_writer_rolls_back_failed_validation(
    tmp_path, monkeypatch
) -> None:
    package_dir = tmp_path / "friday"
    package_dir.mkdir()
    config_path = package_dir / "config.py"
    original = (
        "ENABLE_WHATSAPP_BRIDGE_READ = False\n"
        "ENABLE_REAL_WHATSAPP = False\n"
    )
    config_path.write_text(original, encoding="utf-8")
    from friday.app import whatsapp_bridge_activation_gate as gate_module

    monkeypatch.setattr(gate_module.config, "PACKAGE_DIR", package_dir)
    monkeypatch.setattr(gate_module.config, "ENABLE_WHATSAPP_BRIDGE_READ", False)
    monkeypatch.setattr(gate_module.config, "ENABLE_REAL_WHATSAPP", False)

    result = apply_whatsapp_bridge_read_activation_to_config(
        approval_token="WHATSAPP BRIDGE AKTIVIEREN",
        scanner_smoke_passed=True,
        config_path=config_path,
        execute_write=True,
        post_write_validation=lambda _path: False,
    )

    assert result.allowed is False
    assert result.applied is False
    assert "post_write_validation_failed" in result.blocked_reasons
    assert config_path.read_text(encoding="utf-8") == original
