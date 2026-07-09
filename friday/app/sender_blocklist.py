"""Local sender blocklist helpers for Friday message previews."""

from __future__ import annotations

from pathlib import Path

from friday.storage.repositories import BlockedSenderRepository


def is_sender_blocked(
    source: str,
    sender: str | None,
    *,
    db_path: Path | str | None = None,
) -> bool:
    """Return whether a sender is blocked in the local-only blocklist."""
    return BlockedSenderRepository(db_path).is_sender_blocked(source=source, sender=sender)


def block_sender(
    source: str,
    sender: str | None,
    *,
    label: str | None = None,
    db_path: Path | str | None = None,
) -> dict:
    """Block one sender locally without touching any provider mailbox."""
    return BlockedSenderRepository(db_path).block_sender(
        source=source,
        sender=sender,
        label=label,
    )


def list_blocked_senders(*, db_path: Path | str | None = None) -> list[dict]:
    """Return locally blocked senders."""
    return BlockedSenderRepository(db_path).list_blocked_senders()


def unblock_sender(blocked_sender_id: int, *, db_path: Path | str | None = None) -> dict | None:
    """Remove one local sender block and restore matching local previews."""
    return BlockedSenderRepository(db_path).unblock_sender(blocked_sender_id)
