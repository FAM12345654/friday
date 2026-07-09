"""Build local WhatsApp forwarding previews with wa.me deep links."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import quote


@dataclass(frozen=True)
class WhatsAppForwardPreview:
    """Preview-only WhatsApp forwarding result."""

    draft_text: str
    target: str
    normalized_target: str | None
    deep_link: str | None
    channel: str = "whatsapp"
    sent: bool = False
    preview_only: bool = True
    message: str = "WhatsApp kann geoeffnet werden. Friday sendet nichts."


def normalize_whatsapp_target(value: str | None) -> str | None:
    """Normalize international WhatsApp targets for wa.me links."""
    raw = (value or "").strip()
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if raw.startswith("00") and len(digits) >= 9:
        digits = digits[2:]
    if raw.startswith("0") and not raw.startswith("00"):
        return None
    if len(digits) < 8:
        return None
    return digits


def build_whatsapp_forward_preview(
    *,
    draft_text: str,
    whatsapp_target: str | None,
) -> WhatsAppForwardPreview:
    """Return a WhatsApp deep-link preview without sending anything."""
    clean_draft = (draft_text or "").strip()
    target = (whatsapp_target or "").strip()
    normalized = normalize_whatsapp_target(target)
    if normalized is None:
        return WhatsAppForwardPreview(
            draft_text=clean_draft,
            target=target,
            normalized_target=None,
            deep_link=None,
            message="WhatsApp-Ziel ist nicht im internationalen Format gespeichert. Es wurde nichts gesendet.",
        )

    return WhatsAppForwardPreview(
        draft_text=clean_draft,
        target=target,
        normalized_target=normalized,
        deep_link=f"https://wa.me/{normalized}?text={quote(clean_draft, safe='')}",
    )


__all__ = [
    "WhatsAppForwardPreview",
    "build_whatsapp_forward_preview",
    "normalize_whatsapp_target",
]
