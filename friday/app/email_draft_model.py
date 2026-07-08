"""Local email draft model without provider, login, network, or external delivery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from friday.app.sensitive_contact_context_guard import check_sensitive_contact_context


EmailDraftStatus = Literal["drafted", "edited", "discarded", "blocked"]
CREDENTIAL_MARKERS = (
    "api_key",
    "api key",
    "secret",
    "password",
    "passwort",
    "token",
    "private key",
)


@dataclass(frozen=True)
class EmailDraft:
    """A local preview-only email draft."""

    recipient_label: str
    subject: str
    body: str
    source_context: str
    status: EmailDraftStatus
    blocked_reasons: tuple[str, ...]
    preview_only: bool = True
    provider_used: bool = False
    external_send_enabled: bool = False
    persisted: bool = False
    external_lookup_used: bool = False


def normalize_email_draft_text(value: str | None) -> str:
    """Normalize draft fields for deterministic local display."""
    return " ".join((value or "").strip().split())


def build_email_draft(
    recipient_label: str | None,
    subject: str | None,
    body: str | None,
    source_context: str | None = "local_preview",
    status: str = "drafted",
) -> EmailDraft:
    """Build a local email draft and block unsafe states."""
    normalized_recipient = normalize_email_draft_text(recipient_label) or "Unbekannter Kontakt"
    normalized_subject = normalize_email_draft_text(subject) or "Ohne Betreff"
    normalized_body = (body or "").strip()
    normalized_context = normalize_email_draft_text(source_context) or "local_preview"
    normalized_status = normalize_email_draft_text(status).lower() or "drafted"

    blocked_reasons: list[str] = []
    if normalized_status not in {"drafted", "edited", "discarded", "blocked"}:
        blocked_reasons.append("Unbekannter E-Mail-Draft-Status.")

    if not normalized_body:
        blocked_reasons.append("E-Mail-Entwurf braucht einen lokalen Nachrichtentext.")

    for label, value in (
        ("Empfaenger", normalized_recipient),
        ("Betreff", normalized_subject),
        ("Nachricht", normalized_body),
    ):
        guard = check_sensitive_contact_context(value)
        if not guard.allowed:
            categories = ", ".join(guard.blocked_categories)
            blocked_reasons.append(f"{label} enthaelt sensible Kategorie: {categories}.")
        lowered = value.lower()
        if any(marker in lowered for marker in CREDENTIAL_MARKERS):
            blocked_reasons.append(f"{label} enthaelt moegliche Zugangsdaten oder Secrets.")

    draft_status: EmailDraftStatus
    if blocked_reasons:
        draft_status = "blocked"
    else:
        draft_status = normalized_status  # type: ignore[assignment]

    return EmailDraft(
        recipient_label=normalized_recipient,
        subject=normalized_subject,
        body=normalized_body,
        source_context=normalized_context,
        status=draft_status,
        blocked_reasons=tuple(blocked_reasons),
    )
