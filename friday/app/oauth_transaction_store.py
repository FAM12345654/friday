"""Persistent, encrypted, one-time OAuth transaction state."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.parse import parse_qs, urlsplit

from cryptography.fernet import Fernet, InvalidToken

from friday import config
from friday.app.email_account_store import protect_secret, unprotect_secret
from friday.storage.database import get_connection


DEFAULT_TTL_SECONDS = 10 * 60
MAX_PENDING_TRANSACTIONS = 100
MAX_FUTURE_CLOCK_SKEW_SECONDS = 5


class OAuthTransactionCapacityError(RuntimeError):
    """Raised instead of silently evicting a still-valid OAuth transaction."""


class OAuthTransactionProtectionError(RuntimeError):
    """Raised when persistent OAuth context cannot be encrypted safely."""


def _fernet_from_environment() -> Fernet:
    secret = (
        os.getenv("FRIDAY_OAUTH_LEDGER_SECRET", "").strip()
        or os.getenv("FRIDAY_API_TOKEN", "").strip()
    )
    if len(secret) < 32:
        raise OAuthTransactionProtectionError(
            "OAuth-Zustand kann ohne DPAPI oder starkes Ledger-Secret nicht sicher gespeichert werden."
        )
    material = hashlib.sha256(
        b"friday-oauth-ledger-v1\0" + secret.encode("utf-8")
    ).digest()
    return Fernet(base64.urlsafe_b64encode(material))


def _protect_oauth_context(context_bytes: bytes) -> tuple[str, str]:
    protected, method = protect_secret(context_bytes)
    if method != "base64-warning-no-dpapi":
        return protected, method
    token = _fernet_from_environment().encrypt(context_bytes)
    return token.decode("ascii"), "fernet-env-v1"


def _unprotect_oauth_context(protected: str, method: str) -> bytes:
    if method == "fernet-env-v1":
        try:
            return _fernet_from_environment().decrypt(protected.encode("ascii"))
        except (InvalidToken, UnicodeEncodeError) as exc:
            raise OAuthTransactionProtectionError(
                "OAuth-Zustand konnte nicht sicher entschlüsselt werden."
            ) from exc
    return unprotect_secret(protected, method)


@dataclass(frozen=True)
class OAuthTransaction:
    provider: str
    state: str
    context: dict[str, Any]
    expires_at: float


def generate_oauth_state() -> str:
    return secrets.token_urlsafe(32)


def generate_pkce_code_verifier() -> str:
    # token_urlsafe(64) stays within OAuth's 43..128 character requirement.
    return secrets.token_urlsafe(64)


def extract_oauth_state(authorization_response: str) -> str:
    raw = str(authorization_response or "").strip()
    if not raw:
        return ""
    parsed = urlsplit(raw)
    for encoded in (parsed.query, parsed.fragment):
        values = parse_qs(encoded).get("state")
        if values and values[0]:
            return str(values[0])
    return ""


class OAuthTransactionStore:
    """SQLite-backed OAuth state ledger safe across API workers and restarts."""

    def __init__(
        self,
        *,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        clock: Callable[[], float] | None = None,
        db_path: Path | str | None = None,
        max_pending: int = MAX_PENDING_TRANSACTIONS,
    ) -> None:
        self.ttl_seconds = max(30, int(ttl_seconds))
        self._clock = clock or time.time
        self._configured_db_path = Path(db_path) if db_path is not None else None
        self.max_pending = max(1, int(max_pending))
        self._schema_paths: set[Path] = set()
        self._schema_lock = threading.Lock()

    @property
    def db_path(self) -> Path:
        if self._configured_db_path is not None:
            return self._configured_db_path
        override = os.getenv("FRIDAY_SECURITY_LEDGER_DB_PATH", "").strip()
        return Path(override) if override else config.get_database_path()

    @staticmethod
    def _key(state: str) -> str:
        return hashlib.sha256(str(state).encode("utf-8")).hexdigest()

    def _ensure_schema(self, db_path: Path) -> None:
        if db_path in self._schema_paths:
            return
        with self._schema_lock:
            if db_path in self._schema_paths:
                return
            with get_connection(db_path) as connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS oauth_transactions (
                        state_key TEXT PRIMARY KEY,
                        provider TEXT NOT NULL,
                        encrypted_context TEXT NOT NULL,
                        encryption_method TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        expires_at REAL NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_oauth_transactions_expires
                        ON oauth_transactions(expires_at);
                    """
                )
            self._schema_paths.add(db_path)

    @staticmethod
    def _prepare_connection(connection: sqlite3.Connection) -> None:
        connection.execute("PRAGMA busy_timeout = 10000")

    @staticmethod
    def _purge_expired(connection: sqlite3.Connection, now: float) -> None:
        connection.execute(
            """
            DELETE FROM oauth_transactions
            WHERE expires_at <= ? OR created_at > ?
            """,
            (now, now + MAX_FUTURE_CLOCK_SKEW_SECONDS),
        )

    def put(self, *, provider: str, state: str, context: Mapping[str, Any]) -> None:
        clean_provider = str(provider or "").strip().lower()
        clean_state = str(state or "").strip()
        if not clean_provider or len(clean_state) < 32:
            raise ValueError("OAuth-Transaktion ist ungültig.")
        state_key = self._key(clean_state)
        context_bytes = json.dumps(
            {
                "version": 1,
                "provider": clean_provider,
                "state_key": state_key,
                "context": dict(context),
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        encrypted_context, encryption_method = _protect_oauth_context(context_bytes)
        now = self._clock()
        db_path = self.db_path
        self._ensure_schema(db_path)
        with get_connection(db_path) as connection:
            self._prepare_connection(connection)
            connection.execute("BEGIN IMMEDIATE")
            self._purge_expired(connection, now)
            exists = connection.execute(
                "SELECT 1 FROM oauth_transactions WHERE state_key = ?",
                (state_key,),
            ).fetchone()
            pending_count = int(
                connection.execute("SELECT COUNT(*) FROM oauth_transactions").fetchone()[0]
            )
            if exists is None and pending_count >= self.max_pending:
                raise OAuthTransactionCapacityError(
                    "Zu viele offene OAuth-Anmeldungen. Bitte später erneut versuchen."
                )
            connection.execute(
                """
                INSERT INTO oauth_transactions (
                    state_key, provider, encrypted_context, encryption_method,
                    created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(state_key) DO UPDATE SET
                    provider = excluded.provider,
                    encrypted_context = excluded.encrypted_context,
                    encryption_method = excluded.encryption_method,
                    created_at = excluded.created_at,
                    expires_at = excluded.expires_at
                """,
                (
                    state_key,
                    clean_provider,
                    encrypted_context,
                    encryption_method,
                    now,
                    now + self.ttl_seconds,
                ),
            )

    def consume(self, *, provider: str, state: str) -> OAuthTransaction | None:
        clean_provider = str(provider or "").strip().lower()
        clean_state = str(state or "").strip()
        if not clean_provider or not clean_state:
            return None
        now = self._clock()
        key = self._key(clean_state)
        db_path = self.db_path
        self._ensure_schema(db_path)
        with get_connection(db_path) as connection:
            self._prepare_connection(connection)
            connection.execute("BEGIN IMMEDIATE")
            self._purge_expired(connection, now)
            item = connection.execute(
                """
                SELECT provider, encrypted_context, encryption_method, expires_at
                FROM oauth_transactions
                WHERE state_key = ?
                """,
                (key,),
            ).fetchone()
            if item is None or str(item["provider"]) != clean_provider:
                return None
            connection.execute(
                "DELETE FROM oauth_transactions WHERE state_key = ?",
                (key,),
            )
        try:
            context_raw = _unprotect_oauth_context(
                str(item["encrypted_context"]),
                str(item["encryption_method"]),
            )
            envelope = json.loads(context_raw.decode("utf-8"))
        except (
            OSError,
            OAuthTransactionProtectionError,
            UnicodeDecodeError,
            ValueError,
            json.JSONDecodeError,
        ):
            return None
        if not isinstance(envelope, dict):
            return None
        if (
            envelope.get("version") != 1
            or envelope.get("provider") != clean_provider
            or envelope.get("state_key") != key
            or not isinstance(envelope.get("context"), dict)
        ):
            return None
        return OAuthTransaction(
            provider=clean_provider,
            state=clean_state,
            context=dict(envelope["context"]),
            expires_at=float(item["expires_at"]),
        )

    def discard(self, *, provider: str, state: str) -> None:
        self.consume(provider=provider, state=state)


oauth_transactions = OAuthTransactionStore()
