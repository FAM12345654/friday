"""API mappings for persistent security-ledger overload."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from fastapi import HTTPException


def _load_api_module():
    module_path = Path("friday-api/main.py")
    spec = importlib.util.spec_from_file_location(
        "friday_api_main_for_security_ledger_capacity_test",
        module_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_action_approval_capacity_maps_to_retryable_429(monkeypatch) -> None:
    api = _load_api_module()

    def overloaded(**_kwargs):
        raise api.ActionApprovalCapacityError("approval capacity")

    monkeypatch.setattr(api.action_approvals, "try_issue", overloaded)

    with pytest.raises(HTTPException) as captured:
        api._try_issue_action_approval(action="calendar.create", payload={})

    assert captured.value.status_code == 429
    assert captured.value.headers == {"Retry-After": "30"}


def test_oauth_capacity_maps_to_retryable_429(monkeypatch) -> None:
    api = _load_api_module()

    def overloaded(**_kwargs):
        raise api.OAuthTransactionCapacityError("oauth capacity")

    monkeypatch.setattr(api.oauth_transactions, "put", overloaded)

    with pytest.raises(HTTPException) as captured:
        api._put_oauth_transaction(provider="google", state="s" * 43, context={})

    assert captured.value.status_code == 429
    assert captured.value.headers == {"Retry-After": "30"}


def test_oauth_protection_failure_maps_to_service_unavailable(monkeypatch) -> None:
    api = _load_api_module()

    def unavailable(**_kwargs):
        raise api.OAuthTransactionProtectionError("secure storage unavailable")

    monkeypatch.setattr(api.oauth_transactions, "put", unavailable)

    with pytest.raises(HTTPException) as captured:
        api._put_oauth_transaction(provider="google", state="s" * 43, context={})

    assert captured.value.status_code == 503
