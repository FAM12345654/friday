"""Local read-only WhatsApp inbox mirror storage for Friday."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import secrets
from pathlib import Path
from typing import Any

from friday import config
from friday.storage.database import get_connection, initialize_database
from friday.storage.repositories import BlockedSenderRepository


WHATSAPP_MESSAGE_ID_OFFSET = 900_000_000
BRIDGE_TOKEN_FILE_NAME = "bridge_token.txt"
WHATSAPP_AGENT_NOTES_FILE_NAME = "agent_notes.json"


@dataclass(frozen=True)
class WhatsAppIngestResult:
    """Result of storing one mirrored WhatsApp message."""

    stored: bool
    duplicate: bool
    message_id: int | None
    message: str


@dataclass(frozen=True)
class WhatsAppProcessResult:
    """Result of processing mirrored WhatsApp messages into review suggestions."""

    processed_count: int
    message_suggestions_created: int
    task_suggestions_created: int


def get_whatsapp_local_data_dir() -> Path:
    """Return the local private folder for WhatsApp bridge state."""
    return config.LOCAL_DATA_DIR / "whatsapp"


def get_whatsapp_bridge_token_path() -> Path:
    """Return the local bridge token path."""
    return get_whatsapp_local_data_dir() / BRIDGE_TOKEN_FILE_NAME


def get_whatsapp_agent_notes_path() -> Path:
    """Return the local WhatsApp agent-notes JSON path."""
    return get_whatsapp_local_data_dir() / WHATSAPP_AGENT_NOTES_FILE_NAME


def load_whatsapp_agent_notes(notes_path: Path | str | None = None) -> dict[str, Any]:
    """Load local AI-readable WhatsApp notes without exposing bridge secrets."""
    path = Path(notes_path) if notes_path is not None else get_whatsapp_agent_notes_path()
    if not path.exists() or not path.is_file():
        return {"agent_notes": "", "agent_notes_configured": False, "updated_at": None}
    data = json.loads(path.read_text(encoding="utf-8"))
    notes = str(data.get("agent_notes") or "").strip()
    return {
        "agent_notes": notes,
        "agent_notes_configured": bool(notes),
        "updated_at": data.get("updated_at"),
    }


def save_whatsapp_agent_notes(
    agent_notes: str | None,
    notes_path: Path | str | None = None,
) -> dict[str, Any]:
    """Persist local WhatsApp agent notes without any provider action."""
    path = Path(notes_path) if notes_path is not None else get_whatsapp_agent_notes_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    notes = str(agent_notes or "").strip()
    payload = {
        "agent_notes": notes,
        "agent_notes_configured": bool(notes),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "external_call_used": False,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def ensure_whatsapp_bridge_token(token_path: Path | None = None) -> str:
    """Create and return a local bridge token without logging it."""
    path = token_path or get_whatsapp_bridge_token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    token = secrets.token_urlsafe(32)
    path.write_text(token, encoding="utf-8")
    return token


def read_whatsapp_bridge_token(token_path: Path | None = None) -> str | None:
    """Read the local bridge token if it exists."""
    path = token_path or get_whatsapp_bridge_token_path()
    if not path.exists():
        return None
    token = path.read_text(encoding="utf-8").strip()
    return token or None


def bridge_token_matches(provided_token: str | None, token_path: Path | None = None) -> bool:
    """Return whether the provided local bridge token is accepted."""
    expected = read_whatsapp_bridge_token(token_path=token_path)
    if expected is None:
        return True
    return secrets.compare_digest(provided_token or "", expected)


def hash_whatsapp_identifier(value: str | None) -> str:
    """Hash one WhatsApp identifier so raw phone numbers are never stored."""
    normalized = (value or "").strip().lower()
    if not normalized:
        normalized = "unknown"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def mask_whatsapp_hash(value: str | None) -> str:
    """Return a display-safe masked hash fragment."""
    digest = hash_whatsapp_identifier(value) if value and len(value) != 64 else (value or "")
    if not digest:
        return "hash:unknown"
    return f"hash:{digest[:12]}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row)


def _public_row(row: Any) -> dict[str, Any]:
    item = _row_to_dict(row)
    item["sender_number_masked"] = mask_whatsapp_hash(item.get("sender_number_hash"))
    item.pop("sender_number_hash", None)
    item["source"] = "whatsapp"
    item["synthetic_message_id"] = WHATSAPP_MESSAGE_ID_OFFSET + int(item["id"])
    return item


def insert_whatsapp_message(
    *,
    chat_id: str,
    sender_name: str | None,
    sender_number: str | None,
    body: str,
    received_at: str | None = None,
    db_path: Path | str | None = None,
) -> WhatsAppIngestResult:
    """Insert one mirrored WhatsApp message with hashed identifiers."""
    initialize_database(db_path)
    safe_chat_id = hash_whatsapp_identifier(chat_id)
    safe_sender_hash = hash_whatsapp_identifier(sender_number)
    normalized_body = body or ""
    normalized_received_at = (received_at or "").strip() or _now_iso()
    is_spam = BlockedSenderRepository(db_path).is_sender_blocked(
        source="whatsapp",
        sender=safe_sender_hash,
    )

    with get_connection(db_path) as connection:
        existing = connection.execute(
            """
            SELECT id FROM whatsapp_messages
            WHERE chat_id = ? AND received_at = ?
            LIMIT 1
            """,
            (safe_chat_id, normalized_received_at),
        ).fetchone()
        if existing is not None:
            return WhatsAppIngestResult(
                stored=False,
                duplicate=True,
                message_id=int(existing["id"]),
                message="WhatsApp-Nachricht war bereits lokal vorhanden.",
            )

        cursor = connection.execute(
            """
            INSERT INTO whatsapp_messages (
                chat_id,
                sender_name,
                sender_number_hash,
                body,
                received_at,
                processed,
                suggestion_created,
                is_spam
            )
            VALUES (?, ?, ?, ?, ?, 0, 0, ?)
            """,
            (
                safe_chat_id,
                (sender_name or "WhatsApp").strip() or "WhatsApp",
                safe_sender_hash,
                normalized_body,
                normalized_received_at,
                1 if is_spam else 0,
            ),
        )
        return WhatsAppIngestResult(
            stored=True,
            duplicate=False,
            message_id=int(cursor.lastrowid),
            message="WhatsApp-Nachricht wurde lokal gespiegelt.",
        )


def read_recent_whatsapp_messages(
    *,
    limit: int = 10,
    include_spam: bool = False,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Return recent mirrored WhatsApp messages with masked identifiers."""
    initialize_database(db_path)
    safe_limit = max(1, min(int(limit or 10), 50))
    with get_connection(db_path) as connection:
        where = "" if include_spam else "WHERE is_spam = 0"
        rows = connection.execute(
            f"""
            SELECT id, chat_id, sender_name, sender_number_hash, body, received_at, processed, suggestion_created, is_spam
            FROM whatsapp_messages
            {where}
            ORDER BY received_at DESC, id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()
        return [_public_row(row) for row in rows]


def get_unprocessed_whatsapp_messages(
    *,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Return mirrored WhatsApp messages that still need review suggestions."""
    initialize_database(db_path)
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT id, chat_id, sender_name, sender_number_hash, body, received_at, processed, suggestion_created, is_spam
            FROM whatsapp_messages
            WHERE processed = 0 AND is_spam = 0
            ORDER BY received_at, id
            """
        ).fetchall()
        return [_public_row(row) for row in rows]


def mark_whatsapp_message_processed(
    *,
    message_id: int,
    suggestion_created: bool,
    db_path: Path | str | None = None,
) -> None:
    """Mark one mirrored WhatsApp message as processed locally."""
    initialize_database(db_path)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE whatsapp_messages
            SET processed = 1,
                suggestion_created = ?
            WHERE id = ?
            """,
            (1 if suggestion_created else 0, int(message_id)),
        )


def get_whatsapp_bridge_status(db_path: Path | str | None = None) -> dict[str, Any]:
    """Return password-free/read-only bridge status."""
    initialize_database(db_path)
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT COUNT(*) AS count, MAX(received_at) AS last_received_at
            FROM whatsapp_messages
            """
        ).fetchone()
    count = int(row["count"] or 0)
    last_received_at = row["last_received_at"]
    return {
        "read_enabled": config.ENABLE_WHATSAPP_BRIDGE_READ,
        "real_whatsapp_enabled": config.ENABLE_REAL_WHATSAPP,
        "connected": bool(config.ENABLE_WHATSAPP_BRIDGE_READ and last_received_at),
        "message_count": count,
        "last_received_at": last_received_at,
        "read_only": True,
        "send_via_bridge": False,
        "token_configured": read_whatsapp_bridge_token() is not None,
        "agent_notes_configured": load_whatsapp_agent_notes()["agent_notes_configured"],
    }
