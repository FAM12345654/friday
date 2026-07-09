"""Tests for local guarded account-policy storage."""

from __future__ import annotations

from friday.app.account_policy_store import (
    POLICY_SAVE_TOKEN,
    create_account_policy,
    list_account_policies,
    update_account_policy,
)
from friday.storage.database import setup_local_database


def test_create_account_policy_requires_hard_token(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)

    result = create_account_policy(
        provider="google_calendar",
        label="Google Hauptkalender",
        role="main",
        access="read_write",
        approval_token="ja",
        db_path=db_file,
    )

    assert result.persisted is False
    assert result.blocked_reasons == ("approval_token_invalid",)
    assert list_account_policies(db_file) == []


def test_create_account_policy_persists_filters_and_notes(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)

    result = create_account_policy(
        provider="outlook_graph",
        label="Arbeit Outlook PH",
        role="source",
        access="read",
        include_filters={"title_contains": ["PH"]},
        notes="PH = Dienst = belegt.",
        enabled=True,
        approval_token=POLICY_SAVE_TOKEN,
        db_path=db_file,
    )

    assert result.persisted is True
    policies = list_account_policies(db_file)
    assert len(policies) == 1
    assert policies[0].include_filters == {"title_contains": ["PH"]}
    assert policies[0].notes == "PH = Dienst = belegt."


def test_update_account_policy_requires_token_and_keeps_local_only(tmp_path) -> None:
    db_file = tmp_path / "friday.db"
    setup_local_database(db_file)
    created = create_account_policy(
        provider="google_calendar",
        label="Google",
        role="main",
        access="read_write",
        approval_token=POLICY_SAVE_TOKEN,
        db_path=db_file,
    )
    assert created.policy is not None

    blocked = update_account_policy(
        created.policy.id,
        values={"notes": "Neue Notiz"},
        approval_token="POLICY",
        db_path=db_file,
    )
    allowed = update_account_policy(
        created.policy.id,
        values={"notes": "Neue Notiz"},
        approval_token=POLICY_SAVE_TOKEN,
        db_path=db_file,
    )

    assert blocked.persisted is False
    assert allowed.persisted is True
    assert list_account_policies(db_file)[0].notes == "Neue Notiz"

