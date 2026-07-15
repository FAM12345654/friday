"""Tests for short-lived, one-time OAuth transaction state."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

import friday.app.oauth_transaction_store as oauth_store_module
from friday.storage.database import get_connection
from friday.storage.database import setup_local_database
from friday.app.oauth_transaction_store import (
    OAuthTransactionCapacityError,
    OAuthTransactionProtectionError,
    OAuthTransactionStore,
    extract_oauth_state,
    generate_oauth_state,
    generate_pkce_code_verifier,
)


def test_oauth_transaction_is_provider_bound_and_one_time(tmp_path) -> None:
    store = OAuthTransactionStore(db_path=tmp_path / "oauth.db")
    state = generate_oauth_state()
    store.put(provider="google", state=state, context={"path": "client.json"})

    assert store.consume(provider="microsoft", state=state) is None
    transaction = store.consume(provider="google", state=state)

    assert transaction is not None
    assert transaction.context == {"path": "client.json"}
    assert store.consume(provider="google", state=state) is None


def test_oauth_transaction_expires(tmp_path) -> None:
    now = [100.0]
    store = OAuthTransactionStore(
        ttl_seconds=30,
        clock=lambda: now[0],
        db_path=tmp_path / "oauth.db",
    )
    state = generate_oauth_state()
    store.put(provider="google", state=state, context={})
    now[0] += 31
    assert store.consume(provider="google", state=state) is None


def test_extract_state_from_query_or_fragment() -> None:
    assert extract_oauth_state("http://localhost/?code=abc&state=query-state") == "query-state"
    assert extract_oauth_state("friday://oauth#code=abc&state=fragment-state") == "fragment-state"
    assert extract_oauth_state("abc") == ""


def test_generated_state_and_pkce_verifier_are_high_entropy_length() -> None:
    assert len(generate_oauth_state()) >= 32
    verifier = generate_pkce_code_verifier()
    assert 43 <= len(verifier) <= 128


def test_oauth_transaction_survives_restart_with_encrypted_context(tmp_path) -> None:
    db_path = tmp_path / "oauth.db"
    state = generate_oauth_state()
    context = {"code_verifier": "sensitive-verifier", "path": "client.json"}
    OAuthTransactionStore(db_path=db_path).put(
        provider="google",
        state=state,
        context=context,
    )

    raw_database = db_path.read_bytes()
    assert state.encode("utf-8") not in raw_database
    assert b"sensitive-verifier" not in raw_database

    transaction = OAuthTransactionStore(db_path=db_path).consume(
        provider="google",
        state=state,
    )
    assert transaction is not None
    assert transaction.context == context


def test_only_one_worker_can_consume_oauth_state(tmp_path) -> None:
    db_path = tmp_path / "oauth.db"
    state = generate_oauth_state()
    OAuthTransactionStore(db_path=db_path).put(
        provider="google",
        state=state,
        context={"path": "client.json"},
    )

    def consume(_index: int):
        return OAuthTransactionStore(db_path=db_path).consume(
            provider="google",
            state=state,
        )

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(consume, range(8)))

    assert sum(item is not None for item in results) == 1


def test_oauth_capacity_fails_closed_without_evicting_existing_state(tmp_path) -> None:
    store = OAuthTransactionStore(db_path=tmp_path / "oauth.db", max_pending=1)
    first_state = generate_oauth_state()
    store.put(provider="google", state=first_state, context={"value": 1})

    with pytest.raises(OAuthTransactionCapacityError, match="OAuth-Anmeldungen"):
        store.put(
            provider="google",
            state=generate_oauth_state(),
            context={"value": 2},
        )

    assert store.consume(provider="google", state=first_state) is not None


def test_swapped_encrypted_context_is_detected_and_consumed_fail_closed(tmp_path) -> None:
    db_path = tmp_path / "oauth.db"
    store = OAuthTransactionStore(db_path=db_path)
    first_state = generate_oauth_state()
    second_state = generate_oauth_state()
    store.put(provider="google", state=first_state, context={"value": 1})
    store.put(provider="google", state=second_state, context={"value": 2})

    first_key = store._key(first_state)
    second_key = store._key(second_state)
    with get_connection(db_path) as connection:
        first = connection.execute(
            "SELECT encrypted_context, encryption_method FROM oauth_transactions WHERE state_key = ?",
            (first_key,),
        ).fetchone()
        second = connection.execute(
            "SELECT encrypted_context, encryption_method FROM oauth_transactions WHERE state_key = ?",
            (second_key,),
        ).fetchone()
        connection.execute(
            "UPDATE oauth_transactions SET encrypted_context = ?, encryption_method = ? WHERE state_key = ?",
            (second["encrypted_context"], second["encryption_method"], first_key),
        )
        connection.execute(
            "UPDATE oauth_transactions SET encrypted_context = ?, encryption_method = ? WHERE state_key = ?",
            (first["encrypted_context"], first["encryption_method"], second_key),
        )

    assert store.consume(provider="google", state=first_state) is None
    assert store.consume(provider="google", state=second_state) is None


def test_backward_clock_jump_invalidates_future_oauth_state(tmp_path) -> None:
    now = [100.0]
    store = OAuthTransactionStore(
        ttl_seconds=30,
        clock=lambda: now[0],
        db_path=tmp_path / "oauth.db",
    )
    state = generate_oauth_state()
    store.put(provider="google", state=state, context={})

    now[0] = 90.0
    assert store.consume(provider="google", state=state) is None


def test_database_setup_creates_both_security_ledgers(tmp_path) -> None:
    db_path = tmp_path / "friday.db"
    setup_local_database(db_path, seed_demo_data=False)

    with get_connection(db_path) as connection:
        tables = {
            str(row["name"])
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {
        "action_approvals",
        "action_approval_claims",
        "oauth_transactions",
    } <= tables


def test_non_dpapi_fallback_uses_fernet_instead_of_base64(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        oauth_store_module,
        "protect_secret",
        lambda _value: ("unsafe-base64", "base64-warning-no-dpapi"),
    )
    db_path = tmp_path / "oauth.db"
    state = generate_oauth_state()
    store = OAuthTransactionStore(db_path=db_path)
    store.put(provider="google", state=state, context={"secret": "pkce-value"})

    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT encrypted_context, encryption_method FROM oauth_transactions"
        ).fetchone()
    assert row["encryption_method"] == "fernet-env-v1"
    assert "pkce-value" not in str(row["encrypted_context"])
    assert store.consume(provider="google", state=state).context == {
        "secret": "pkce-value"
    }


def test_non_dpapi_fallback_without_strong_secret_fails_closed(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        oauth_store_module,
        "protect_secret",
        lambda _value: ("unsafe-base64", "base64-warning-no-dpapi"),
    )
    monkeypatch.delenv("FRIDAY_OAUTH_LEDGER_SECRET", raising=False)
    monkeypatch.delenv("FRIDAY_API_TOKEN", raising=False)
    store = OAuthTransactionStore(db_path=tmp_path / "oauth.db")

    with pytest.raises(OAuthTransactionProtectionError, match="nicht sicher"):
        store.put(
            provider="google",
            state=generate_oauth_state(),
            context={"secret": "pkce-value"},
        )
