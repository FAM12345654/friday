"""Persistent, one-time approvals bound to an exact external action payload."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from friday import config
from friday.storage.database import get_connection


DEFAULT_APPROVAL_TTL_SECONDS = 5 * 60
MAX_PENDING_APPROVALS = 200
MAX_FUTURE_CLOCK_SKEW_SECONDS = 5


class ActionApprovalCapacityError(RuntimeError):
    """Raised instead of silently evicting another still-valid approval."""


def _payload_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(payload),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ActionApproval:
    approval_id: str
    action: str
    expires_in_seconds: int

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.approval_id,
            "action": self.action,
            "expires_in_seconds": self.expires_in_seconds,
            "one_time": True,
            "payload_bound": True,
        }


class ActionApprovalStore:
    """SQLite-backed approval ledger safe across threads and API workers."""

    def __init__(
        self,
        *,
        ttl_seconds: int = DEFAULT_APPROVAL_TTL_SECONDS,
        clock: Callable[[], float] | None = None,
        db_path: Path | str | None = None,
        max_pending: int = MAX_PENDING_APPROVALS,
    ) -> None:
        self.ttl_seconds = max(30, int(ttl_seconds))
        # A persistent ledger requires a process-independent wall clock.
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
    def _key(approval_id: str) -> str:
        return hashlib.sha256(str(approval_id).encode("utf-8")).hexdigest()

    @staticmethod
    def _operation_key(action: str, payload_digest: str) -> str:
        return hashlib.sha256(f"{action}:{payload_digest}".encode("utf-8")).hexdigest()

    def _ensure_schema(self, db_path: Path) -> None:
        if db_path in self._schema_paths:
            return
        with self._schema_lock:
            if db_path in self._schema_paths:
                return
            with get_connection(db_path) as connection:
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS action_approvals (
                        approval_key TEXT PRIMARY KEY,
                        action TEXT NOT NULL,
                        payload_digest TEXT NOT NULL,
                        operation_key TEXT NOT NULL,
                        created_at REAL NOT NULL,
                        expires_at REAL NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_action_approvals_expires
                        ON action_approvals(expires_at);

                    CREATE TABLE IF NOT EXISTS action_approval_claims (
                        operation_key TEXT PRIMARY KEY,
                        claimed_at REAL NOT NULL,
                        expires_at REAL NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_action_approval_claims_expires
                        ON action_approval_claims(expires_at);
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
            DELETE FROM action_approvals
            WHERE expires_at <= ? OR created_at > ?
            """,
            (now, now + MAX_FUTURE_CLOCK_SKEW_SECONDS),
        )
        connection.execute(
            "DELETE FROM action_approval_claims WHERE expires_at <= ?",
            (now,),
        )

    def issue(self, *, action: str, payload: Mapping[str, Any]) -> ActionApproval:
        approval = self.try_issue(action=action, payload=payload)
        if approval is None:
            raise RuntimeError("Diese Aktion wurde vor kurzem bereits freigegeben.")
        return approval

    def try_issue(
        self,
        *,
        action: str,
        payload: Mapping[str, Any],
    ) -> ActionApproval | None:
        clean_action = str(action or "").strip().lower()
        if not clean_action:
            raise ValueError("Approval-Aktion fehlt.")
        approval_id = secrets.token_urlsafe(32)
        now = self._clock()
        payload_digest = _payload_digest(payload)
        operation_key = self._operation_key(clean_action, payload_digest)
        db_path = self.db_path
        self._ensure_schema(db_path)
        with get_connection(db_path) as connection:
            self._prepare_connection(connection)
            connection.execute("BEGIN IMMEDIATE")
            self._purge_expired(connection, now)
            claimed = connection.execute(
                "SELECT 1 FROM action_approval_claims WHERE operation_key = ?",
                (operation_key,),
            ).fetchone()
            if claimed is not None:
                return None
            pending_count = int(
                connection.execute("SELECT COUNT(*) FROM action_approvals").fetchone()[0]
            )
            if pending_count >= self.max_pending:
                raise ActionApprovalCapacityError(
                    "Zu viele offene Einmalfreigaben. Bitte später erneut versuchen."
                )
            connection.execute(
                """
                INSERT INTO action_approvals (
                    approval_key, action, payload_digest, operation_key,
                    created_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    self._key(approval_id),
                    clean_action,
                    payload_digest,
                    operation_key,
                    now,
                    now + self.ttl_seconds,
                ),
            )
        return ActionApproval(
            approval_id=approval_id,
            action=clean_action,
            expires_in_seconds=self.ttl_seconds,
        )

    def consume(
        self,
        *,
        approval_id: str,
        action: str,
        payload: Mapping[str, Any],
    ) -> bool:
        clean_id = str(approval_id or "").strip()
        clean_action = str(action or "").strip().lower()
        if not clean_id or not clean_action:
            return False
        now = self._clock()
        key = self._key(clean_id)
        candidate_digest = _payload_digest(payload)
        db_path = self.db_path
        self._ensure_schema(db_path)
        with get_connection(db_path) as connection:
            self._prepare_connection(connection)
            connection.execute("BEGIN IMMEDIATE")
            self._purge_expired(connection, now)
            item = connection.execute(
                """
                SELECT action, payload_digest, operation_key
                FROM action_approvals
                WHERE approval_key = ?
                """,
                (key,),
            ).fetchone()
            if item is None or str(item["action"]) != clean_action:
                return False
            # A same-action payload mismatch consumes the bearer capability.
            connection.execute(
                "DELETE FROM action_approvals WHERE approval_key = ?",
                (key,),
            )
            stored_digest = str(item["payload_digest"])
            if not hmac.compare_digest(stored_digest, candidate_digest):
                return False
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO action_approval_claims (
                    operation_key, claimed_at, expires_at
                ) VALUES (?, ?, ?)
                """,
                (str(item["operation_key"]), now, now + self.ttl_seconds),
            )
            return cursor.rowcount == 1


action_approvals = ActionApprovalStore()
