"""Tests for encrypted local Outlook ICS account URL storage."""

from __future__ import annotations

from friday.app.account_policy_store import POLICY_SAVE_TOKEN
from friday.app.calendar_ics_account_store import (
    build_outlook_ics_account,
    decrypt_outlook_ics_url,
    load_outlook_ics_account,
    outlook_ics_account_status,
    save_outlook_ics_account,
)
import pytest


def test_outlook_ics_account_store_encrypts_url_and_returns_url_free_status(tmp_path) -> None:
    account_path = tmp_path / "accounts" / "outlook_ics_accounts.json"
    account = build_outlook_ics_account(
        policy_id=7,
        ics_url="https://example.invalid/private-calendar.ics",
    )

    result = save_outlook_ics_account(
        account,
        approval_token=POLICY_SAVE_TOKEN,
        account_path=account_path,
    )
    loaded = load_outlook_ics_account(7, account_path=account_path)
    status = outlook_ics_account_status(7, account_path=account_path)
    raw_file = account_path.read_text(encoding="utf-8")

    assert result["persisted"] is True
    assert loaded is not None
    assert decrypt_outlook_ics_url(loaded) == "https://example.invalid/private-calendar.ics"
    assert "example.invalid" not in raw_file
    assert status["connected"] is True
    assert "ics_url" not in status


def test_outlook_ics_account_store_rejects_soft_token(tmp_path) -> None:
    account = build_outlook_ics_account(
        policy_id=7,
        ics_url="https://example.invalid/private-calendar.ics",
    )

    result = save_outlook_ics_account(
        account,
        approval_token="JA",
        account_path=tmp_path / "accounts" / "outlook_ics_accounts.json",
    )

    assert result["persisted"] is False
    assert "approval_token_invalid" in result["blocked_reasons"]


@pytest.mark.parametrize("url", ("http://example.com/feed.ics", "file:///tmp/feed.ics", "https://127.0.0.1/feed.ics"))
def test_outlook_ics_account_rejects_ssrf_urls(url: str) -> None:
    with pytest.raises(ValueError):
        build_outlook_ics_account(policy_id=7, ics_url=url)
