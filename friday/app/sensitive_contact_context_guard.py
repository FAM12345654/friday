"""Local sensitive contact-context guard.

This module performs deterministic local checks only.
It does not call models, providers, network APIs, files, or databases.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SensitiveContactCategory = Literal[
    "politics",
    "religion",
    "ethnicity",
    "health",
    "sexual_orientation",
    "trade_union",
    "criminal_record",
    "financial_private",
    "intimate_private",
]


SENSITIVE_CATEGORY_TERMS: dict[SensitiveContactCategory, tuple[str, ...]] = {
    "politics": (
        "parteimitglied",
        "politische partei",
        "waehlt ",
        "wählt ",
        "fpö",
        "spö",
        "övp",
        "gruene",
        "grüne",
        "neos",
    ),
    "religion": (
        "christ",
        "muslim",
        "jude",
        "juedin",
        "jüdin",
        "religion",
        "kirche",
        "moschee",
        "synagoge",
    ),
    "ethnicity": (
        "ethnie",
        "herkunft",
        "race",
        "rasse",
        "migrationshintergrund",
    ),
    "health": (
        "diagnose",
        "krankheit",
        "depression",
        "diabetes",
        "krebs",
        "therapie",
        "medikament",
    ),
    "sexual_orientation": (
        "homosexuell",
        "lesbisch",
        "schwul",
        "bisexuell",
        "trans",
        "sexleben",
        "sexuelle orientierung",
    ),
    "trade_union": (
        "gewerkschaft",
        "betriebsrat",
        "gewerkschaftsmitglied",
    ),
    "criminal_record": (
        "vorstrafe",
        "strafregister",
        "verurteilt",
        "haftstrafe",
        "straftat",
    ),
    "financial_private": (
        "privatinsolvenz",
        "schulden",
        "kontostand",
        "kreditprobleme",
        "gehaltsschulden",
    ),
    "intimate_private": (
        "affäre",
        "affaere",
        "beziehungskrise",
        "scheidung",
        "intimes",
    ),
}


@dataclass(frozen=True)
class SensitiveContactContextGuardResult:
    """Structured result for a local sensitive contact-context check."""

    text: str
    allowed: bool
    blocked_categories: tuple[SensitiveContactCategory, ...]
    reason: str | None
    preview_only: bool
    persisted: bool
    external_lookup_used: bool


def normalize_sensitive_guard_text(text: str | None) -> str:
    """Normalize free text for deterministic local matching."""
    return " ".join((text or "").strip().lower().split())


def check_sensitive_contact_context(
    text: str | None,
) -> SensitiveContactContextGuardResult:
    """Check whether a contact-context free text contains sensitive terms."""
    normalized_text = normalize_sensitive_guard_text(text)
    blocked: list[SensitiveContactCategory] = []

    if not normalized_text:
        return SensitiveContactContextGuardResult(
            text="",
            allowed=True,
            blocked_categories=(),
            reason=None,
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    for category, terms in SENSITIVE_CATEGORY_TERMS.items():
        if any(term in normalized_text for term in terms):
            blocked.append(category)

    if blocked:
        return SensitiveContactContextGuardResult(
            text=normalized_text,
            allowed=False,
            blocked_categories=tuple(blocked),
            reason="Sensitive contact-context category detected.",
            preview_only=True,
            persisted=False,
            external_lookup_used=False,
        )

    return SensitiveContactContextGuardResult(
        text=normalized_text,
        allowed=True,
        blocked_categories=(),
        reason=None,
        preview_only=True,
        persisted=False,
        external_lookup_used=False,
    )
