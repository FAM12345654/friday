"""Local account-policy persistence for Friday integrations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from typing import Any

from friday.storage.database import get_connection


POLICY_SAVE_TOKEN = "POLICY SPEICHERN"
POLICY_DELETE_TOKEN = "POLICY SPEICHERN"

VALID_POLICY_PROVIDERS = {
    "google_calendar",
    "outlook_graph",
    "outlook_ics",
    "imap_email",
    "whatsapp_bridge",
}
VALID_POLICY_ROLES = {"main", "source"}
VALID_POLICY_ACCESS = {"read", "read_write"}


@dataclass(frozen=True)
class AccountPolicy:
    """One local policy that controls how Friday uses an account."""

    id: int | None
    provider: str
    label: str
    role: str
    access: str
    include_filters: dict[str, Any]
    exclude_filters: dict[str, Any]
    notes: str
    enabled: bool
    created_at: str
    updated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AccountPolicyWriteResult:
    """Result of a guarded account-policy write."""

    allowed: bool
    persisted: bool
    message: str
    blocked_reasons: tuple[str, ...]
    policy: AccountPolicy | None = None
    preview_only: bool = False
    external_call_used: bool = False


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _normalize_provider(provider: str) -> str:
    value = _clean(provider).lower()
    if value not in VALID_POLICY_PROVIDERS:
        raise ValueError("Unbekannter Account-Provider.")
    return value


def _normalize_role(role: str) -> str:
    value = _clean(role).lower()
    if value not in VALID_POLICY_ROLES:
        raise ValueError("Ungueltige Account-Rolle.")
    return value


def _normalize_access(access: str) -> str:
    value = _clean(access).lower()
    if value not in VALID_POLICY_ACCESS:
        raise ValueError("Ungueltiger Account-Zugriff.")
    return value


def _normalize_filters(value: dict[str, Any] | str | None) -> dict[str, Any]:
    if value is None or value == "":
        return {}
    if isinstance(value, str):
        parsed = json.loads(value)
    else:
        parsed = value
    if not isinstance(parsed, dict):
        raise ValueError("Filter muessen ein Objekt sein.")
    normalized: dict[str, Any] = {}
    for key, raw_value in parsed.items():
        key_text = _clean(key)
        if isinstance(raw_value, list):
            normalized[key_text] = [_clean(item) for item in raw_value if _clean(item)]
        elif raw_value is None:
            normalized[key_text] = []
        else:
            normalized[key_text] = _clean(raw_value)
    return normalized


def _filters_to_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _row_to_policy(row: Any) -> AccountPolicy:
    return AccountPolicy(
        id=int(row["id"]),
        provider=str(row["provider"]),
        label=str(row["label"]),
        role=str(row["role"]),
        access=str(row["access"]),
        include_filters=json.loads(row["include_filters"] or "{}"),
        exclude_filters=json.loads(row["exclude_filters"] or "{}"),
        notes=str(row["notes"] or ""),
        enabled=bool(row["enabled"]),
        created_at=str(row["created_at"]),
        updated_at=row["updated_at"],
    )


def list_account_policies(db_path: Path | str | None = None) -> list[AccountPolicy]:
    """Return all local account policies."""
    try:
        with get_connection(db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, provider, label, role, access, include_filters, exclude_filters,
                       notes, enabled, created_at, updated_at
                FROM account_policies
                ORDER BY id
                """
            ).fetchall()
    except sqlite3.OperationalError:
        return []
    return [_row_to_policy(row) for row in rows]


def get_account_policy(policy_id: int, db_path: Path | str | None = None) -> AccountPolicy | None:
    """Return one local account policy by id."""
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, provider, label, role, access, include_filters, exclude_filters,
                   notes, enabled, created_at, updated_at
            FROM account_policies
            WHERE id = ?
            """,
            (policy_id,),
        ).fetchone()
    return None if row is None else _row_to_policy(row)


def create_account_policy(
    *,
    provider: str,
    label: str,
    role: str,
    access: str,
    include_filters: dict[str, Any] | str | None = None,
    exclude_filters: dict[str, Any] | str | None = None,
    notes: str | None = "",
    enabled: bool = True,
    approval_token: str,
    db_path: Path | str | None = None,
) -> AccountPolicyWriteResult:
    """Create one account policy only after the hard policy token."""
    if approval_token != POLICY_SAVE_TOKEN:
        return AccountPolicyWriteResult(
            allowed=False,
            persisted=False,
            message="Policy wurde nicht gespeichert: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    clean_label = _clean(label)
    if not clean_label:
        raise ValueError("Policy-Label ist erforderlich.")
    created_at = _now_iso()
    policy_provider = _normalize_provider(provider)
    policy_role = _normalize_role(role)
    policy_access = _normalize_access(access)
    include_json = _filters_to_json(_normalize_filters(include_filters))
    exclude_json = _filters_to_json(_normalize_filters(exclude_filters))

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO account_policies
            (provider, label, role, access, include_filters, exclude_filters, notes, enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                policy_provider,
                clean_label,
                policy_role,
                policy_access,
                include_json,
                exclude_json,
                str(notes or ""),
                1 if enabled else 0,
                created_at,
                created_at,
            ),
        )
        policy_id = int(cursor.lastrowid)
    policy = get_account_policy(policy_id, db_path=db_path)
    return AccountPolicyWriteResult(
        allowed=True,
        persisted=True,
        message="Policy wurde lokal gespeichert.",
        blocked_reasons=(),
        policy=policy,
    )


def update_account_policy(
    policy_id: int,
    *,
    values: dict[str, Any],
    approval_token: str,
    db_path: Path | str | None = None,
) -> AccountPolicyWriteResult:
    """Update one account policy only after the hard policy token."""
    if approval_token != POLICY_SAVE_TOKEN:
        return AccountPolicyWriteResult(
            allowed=False,
            persisted=False,
            message="Policy wurde nicht gespeichert: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    current = get_account_policy(policy_id, db_path=db_path)
    if current is None:
        return AccountPolicyWriteResult(
            allowed=False,
            persisted=False,
            message="Policy wurde nicht gefunden.",
            blocked_reasons=("not_found",),
        )
    merged = current.to_dict()
    merged.update({key: value for key, value in values.items() if value is not None})
    updated_at = _now_iso()
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE account_policies
            SET provider = ?, label = ?, role = ?, access = ?, include_filters = ?,
                exclude_filters = ?, notes = ?, enabled = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                _normalize_provider(str(merged["provider"])),
                _clean(merged["label"]),
                _normalize_role(str(merged["role"])),
                _normalize_access(str(merged["access"])),
                _filters_to_json(_normalize_filters(merged.get("include_filters"))),
                _filters_to_json(_normalize_filters(merged.get("exclude_filters"))),
                str(merged.get("notes") or ""),
                1 if bool(merged.get("enabled")) else 0,
                updated_at,
                policy_id,
            ),
        )
    return AccountPolicyWriteResult(
        allowed=True,
        persisted=True,
        message="Policy wurde lokal aktualisiert.",
        blocked_reasons=(),
        policy=get_account_policy(policy_id, db_path=db_path),
    )


def delete_account_policy(
    policy_id: int,
    *,
    approval_token: str,
    db_path: Path | str | None = None,
) -> AccountPolicyWriteResult:
    """Delete one account policy only after the hard policy token."""
    if approval_token != POLICY_DELETE_TOKEN:
        return AccountPolicyWriteResult(
            allowed=False,
            persisted=False,
            message="Policy wurde nicht geloescht: Token fehlt.",
            blocked_reasons=("approval_token_invalid",),
        )
    current = get_account_policy(policy_id, db_path=db_path)
    if current is None:
        return AccountPolicyWriteResult(
            allowed=False,
            persisted=False,
            message="Policy wurde nicht gefunden.",
            blocked_reasons=("not_found",),
        )
    with get_connection(db_path) as connection:
        connection.execute("DELETE FROM account_policies WHERE id = ?", (policy_id,))
    return AccountPolicyWriteResult(
        allowed=True,
        persisted=True,
        message="Policy wurde lokal geloescht.",
        blocked_reasons=(),
        policy=current,
    )
