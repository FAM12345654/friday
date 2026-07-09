"""Side-effect-free messaging audit preview model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


MessagingChannel = Literal["email", "whatsapp"]
MessagingAuditMode = Literal["preview", "mock", "live"]
MessagingAuditStatus = Literal[
    "draft_created",
    "link_built",
    "drafted",
    "simulated",
    "approval_rejected",
    "approval_accepted",
    "sent",
    "failed",
]


@dataclass(frozen=True)
class MessagingAuditPreview:
    """Read-only preview of a future messaging audit event."""

    created_at: str
    task_id: int | None
    task_title: str
    contact_id: int | None
    contact_name: str
    channel: MessagingChannel
    target: str
    draft_text: str
    approval_token: str | None
    mode: MessagingAuditMode
    status: MessagingAuditStatus
    provider: str | None = None
    external_message_id: str | None = None
    notes: str = "Preview only. Nothing was sent or persisted."
    persisted: bool = False
    external_send_enabled: bool = False


def build_messaging_audit_preview(
    *,
    task_id: int | None,
    task_title: str,
    contact_id: int | None,
    contact_name: str,
    channel: MessagingChannel,
    target: str,
    draft_text: str,
    approval_token: str | None,
    mode: MessagingAuditMode = "preview",
    status: MessagingAuditStatus = "drafted",
    provider: str | None = None,
    external_message_id: str | None = None,
    created_at: str | None = None,
) -> MessagingAuditPreview:
    """Build a read-only audit preview without side effects."""

    _validate_channel(channel)
    _validate_mode(mode)
    _validate_status(status)
    normalized_draft = draft_text.strip()
    if not normalized_draft:
        raise ValueError("draft_text must not be empty.")
    if mode != "live" and external_message_id:
        raise ValueError("external_message_id is only allowed for live mode previews.")

    return MessagingAuditPreview(
        created_at=created_at or datetime.now(timezone.utc).isoformat(),
        task_id=task_id,
        task_title=task_title.strip() or "-",
        contact_id=contact_id,
        contact_name=contact_name.strip() or "-",
        channel=channel,
        target=target.strip() or "-",
        draft_text=normalized_draft,
        approval_token=approval_token.strip() if approval_token else None,
        mode=mode,
        status=status,
        provider=provider.strip() if provider else None,
        external_message_id=external_message_id,
    )


def _validate_channel(channel: str) -> None:
    if channel not in {"email", "whatsapp"}:
        raise ValueError("Unsupported messaging channel.")


def _validate_mode(mode: str) -> None:
    if mode not in {"preview", "mock", "live"}:
        raise ValueError("Unsupported audit mode.")


def _validate_status(status: str) -> None:
    allowed = {
        "draft_created",
        "link_built",
        "drafted",
        "simulated",
        "approval_rejected",
        "approval_accepted",
        "sent",
        "failed",
    }
    if status not in allowed:
        raise ValueError("Unsupported audit status.")
