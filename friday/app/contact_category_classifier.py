"""Local deterministic contact category classifier."""

from __future__ import annotations

from dataclasses import asdict, dataclass


CANONICAL_CONTACT_CATEGORIES: tuple[str, ...] = (
    "familie",
    "arbeit",
    "freund",
    "kunde",
    "dienstleister",
    "sonstiges",
    "unbekannt",
)

CONTACT_CATEGORY_ALIASES: dict[str, str] = {
    "family": "familie",
    "familie": "familie",
    "mutter": "familie",
    "vater": "familie",
    "bruder": "familie",
    "schwester": "familie",
    "work": "arbeit",
    "arbeit": "arbeit",
    "kollege": "arbeit",
    "kollegin": "arbeit",
    "chef": "arbeit",
    "mitarbeiter": "arbeit",
    "friend": "freund",
    "freund": "freund",
    "freundin": "freund",
    "kunde": "kunde",
    "kundin": "kunde",
    "customer": "kunde",
    "dienstleister": "dienstleister",
    "lieferant": "dienstleister",
    "provider": "dienstleister",
    "other": "sonstiges",
    "sonstiges": "sonstiges",
    "unknown": "unbekannt",
    "unbekannt": "unbekannt",
}


@dataclass(frozen=True)
class ContactCategoryPreview:
    """Preview-only local contact category result."""

    display_name: str
    category: str
    confidence: str
    reasons: tuple[str, ...]
    preview_only: bool
    persisted: bool
    external_lookup_used: bool

    def to_dict(self) -> dict:
        return asdict(self)


def normalize_contact_category(value: str | None) -> str:
    """Normalize aliases to a stable German category."""
    normalized = (value or "").strip().lower()
    if not normalized:
        return "unbekannt"
    return CONTACT_CATEGORY_ALIASES.get(normalized, "sonstiges")


def classify_contact_category(
    *,
    display_name: str,
    context_text: str | None = None,
    model_raw_category: str | None = None,
) -> ContactCategoryPreview:
    """Classify a contact locally without external lookup or persistence."""
    clean_name = (display_name or "").strip()
    combined = f"{clean_name} {context_text or ''}".lower()
    reasons: list[str] = []

    if model_raw_category:
        category = normalize_contact_category(model_raw_category)
        if category != "sonstiges":
            reasons.append("Modell-Rohkategorie wurde auf erlaubte Kategorie normalisiert.")
            return ContactCategoryPreview(clean_name, category, "medium", tuple(reasons), True, False, False)

    for keyword, category in CONTACT_CATEGORY_ALIASES.items():
        if keyword and keyword in combined and category not in {"sonstiges", "unbekannt"}:
            reasons.append(f"Lokales Keyword erkannt: {keyword}")
            return ContactCategoryPreview(clean_name, category, "medium", tuple(reasons), True, False, False)

    return ContactCategoryPreview(
        display_name=clean_name,
        category="unbekannt" if not clean_name else "sonstiges",
        confidence="low",
        reasons=("Keine eindeutige lokale Kategorie erkannt.",),
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
