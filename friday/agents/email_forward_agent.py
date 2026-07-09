"""Build local email forwarding previews with mailto deep links."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True)
class EmailForwardPreview:
    """Preview-only email forwarding result."""

    draft_text: str
    target: str
    deep_link: str | None
    channel: str = "email"
    sent: bool = False
    preview_only: bool = True
    message: str = "E-Mail-App kann geoeffnet werden. Friday sendet nichts."


def build_email_forward_preview(
    *,
    draft_text: str,
    email_address: str | None,
    subject: str = "Friday Aufgaben-Weiterleitung",
) -> EmailForwardPreview:
    """Return a mailto preview without sending anything."""
    target = (email_address or "").strip()
    clean_draft = (draft_text or "").strip()
    if "@" not in target:
        return EmailForwardPreview(
            draft_text=clean_draft,
            target=target,
            deep_link=None,
            message="Keine gueltige E-Mail-Adresse gespeichert. Es wurde nichts gesendet.",
        )

    encoded_subject = quote(subject.strip() or "Friday Aufgaben-Weiterleitung", safe="")
    encoded_body = quote(clean_draft, safe="")
    return EmailForwardPreview(
        draft_text=clean_draft,
        target=target,
        deep_link=f"mailto:{quote(target, safe='@.+-_')}?subject={encoded_subject}&body={encoded_body}",
    )


__all__ = ["EmailForwardPreview", "build_email_forward_preview"]
