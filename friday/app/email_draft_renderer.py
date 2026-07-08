"""Render local email drafts without input, print, provider, or network."""

from __future__ import annotations

from friday.app.email_draft_model import EmailDraft


def render_email_draft_preview(draft: EmailDraft) -> str:
    """Render a local email draft preview without external delivery."""
    lines = [
        "E-Mail-Entwurf (lokal, nicht gesendet)",
        "",
        f"An: {draft.recipient_label}",
        f"Betreff: {draft.subject}",
        "",
        draft.body if draft.body else "(kein Nachrichtentext)",
        "",
        f"Status: {draft.status}",
        "Hinweis: Dies ist nur ein lokaler Entwurf.",
        "Es wurde nichts gesendet.",
        "Kein E-Mail-Provider ist verbunden.",
        "Dies ist nur eine lokale Vorschau.",
    ]

    if draft.blocked_reasons:
        lines.append("Blockiert:")
        lines.extend(f"- {reason}" for reason in draft.blocked_reasons)

    return "\n".join(lines).rstrip() + "\n"
