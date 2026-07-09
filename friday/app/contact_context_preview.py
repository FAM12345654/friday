"""Contact context preview model helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ContactType = Literal[
    "kunde",
    "kollege",
    "mitarbeiter",
    "arbeit",
    "familie",
    "freund",
    "dienstleister",
    "sonstiges",
    "unbekannt",
]

VALID_CONTACT_TYPES: set[str] = {
    "kunde",
    "kollege",
    "mitarbeiter",
    "arbeit",
    "familie",
    "freund",
    "dienstleister",
    "sonstiges",
    "unbekannt",
}


@dataclass(frozen=True)
class ContactContextPreview:
    display_name: str
    normalized_name: str
    contact_type: ContactType
    nickname: str | None
    relationship_context: str | None
    source_context: str
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def normalize_contact_name(name: str) -> str:
    """Normalize display names for preview-only comparison."""
    return " ".join((name or "").strip().lower().split())


def normalize_contact_type(contact_type: str | None) -> ContactType:
    """Return a stable local contact type."""
    normalized = (contact_type or "").strip().lower()
    if normalized in VALID_CONTACT_TYPES:
        return normalized  # type: ignore[return-value]
    if not normalized:
        return "unbekannt"
    return "sonstiges"


def build_contact_context_preview(
    display_name: str,
    contact_type: str | None = None,
    nickname: str | None = None,
    relationship_context: str | None = None,
    source_context: str = "manuell",
) -> ContactContextPreview:
    clean_name = (display_name or "").strip()
    return ContactContextPreview(
        display_name=clean_name,
        normalized_name=normalize_contact_name(clean_name),
        contact_type=normalize_contact_type(contact_type),
        nickname=(nickname or "").strip() or None,
        relationship_context=(relationship_context or "").strip() or None,
        source_context=(source_context or "manuell").strip() or "manuell",
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
