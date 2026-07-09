"""Build local AI context blocks from Friday's user-editable notes."""

from __future__ import annotations

from typing import Any, Iterable

from friday.app.account_policy_engine import build_ai_context
from friday.app.account_policy_store import AccountPolicy, list_account_policies
from friday.app.email_account_store import EmailAccount, load_email_account
from friday.app.whatsapp_inbox_store import load_whatsapp_agent_notes
from friday.storage.learning_repository import LearningRepository


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _contact_label(contact: dict[str, Any]) -> str:
    return _clean_text(contact.get("name") or contact.get("display_name") or "Kontakt")


def build_agent_context(
    *,
    contact: dict[str, Any] | None = None,
    channel: str | None = None,
    policies: Iterable[AccountPolicy] | None = None,
    email_account: EmailAccount | None = None,
    whatsapp_notes: dict[str, Any] | None = None,
    learned_rules: Iterable[dict[str, Any]] | None = None,
) -> str:
    """Return a local-only context block for local AI prompts.

    The returned text is intended for local Ollama prompts only. It must not be
    logged, sent to cloud models, or exposed to external providers.
    """
    normalized_channel = _clean_text(channel).casefold()
    lines: list[str] = []

    policy_items = list(policies) if policies is not None else list_account_policies()
    policy_context = build_ai_context(policy_items)
    if policy_context and policy_context != "Keine aktiven Account-Policy-Notizen.":
        lines.append(policy_context)

    if normalized_channel in {"", "email"}:
        account = email_account if email_account is not None else load_email_account()
        email_notes = _clean_text(getattr(account, "agent_notes", "")) if account else ""
        if email_notes:
            lines.append(f"E-Mail-Konto-Notiz:\n{email_notes}")

    if normalized_channel in {"", "whatsapp"}:
        notes_payload = (
            whatsapp_notes
            if whatsapp_notes is not None
            else load_whatsapp_agent_notes()
        )
        notes = _clean_text(notes_payload.get("agent_notes") if notes_payload else "")
        if notes:
            lines.append(f"WhatsApp-Agent-Notiz:\n{notes}")

    if contact:
        contact_notes = _clean_text(contact.get("notes"))
        contact_type = _clean_text(contact.get("contact_type") or contact.get("category"))
        betreuer = _clean_text(contact.get("betreuer"))
        contact_lines: list[str] = []
        if contact_type == "kunde" and betreuer:
            contact_lines.append(
                f"Kunde {_contact_label(contact)}, Betreuer: {betreuer.title()}"
            )
        if contact_type:
            contact_lines.append(f"Kontaktart: {contact_type}")
        if contact_notes:
            contact_lines.append(f"Notizen: {contact_notes}")
        if contact_lines:
            lines.append(f"Kontakt-Notiz fuer {_contact_label(contact)}:\n" + "\n".join(contact_lines))

    rule_items = list(learned_rules) if learned_rules is not None else _load_active_learned_rules()
    rule_lines = _format_learned_rule_lines(rule_items)
    if rule_lines:
        lines.append("Gelernte lokale Regeln:\n" + "\n".join(rule_lines))

    if not lines:
        return ""
    return "Lokaler Agent-Kontext (nicht extern senden):\n" + "\n\n".join(lines)


def _load_active_learned_rules() -> list[dict[str, Any]]:
    try:
        return LearningRepository().list_rules(include_disabled=False)
    except Exception:
        return []


def _format_learned_rule_lines(rules: Iterable[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    for rule in rules:
        if not rule.get("enabled", True):
            continue
        kind = str(rule.get("kind") or "")
        value = rule.get("value") or {}
        if not isinstance(value, dict):
            value = {}
        if kind == "sender_contact":
            sender = _clean_text(value.get("sender") or rule.get("key"))
            contact_type = _clean_text(value.get("contact_type"))
            betreuer = _clean_text(value.get("betreuer"))
            detail = f"{sender}: Kontaktart {contact_type or '-'}"
            if betreuer:
                detail += f", Betreuer {betreuer.title()}"
            lines.append(detail)
        elif kind == "mail_topic_task_rule":
            topic = _clean_text(value.get("topic"))
            if value.get("create_task") and topic:
                lines.append(f"Wiederkehrendes Mail-Thema '{topic}' darf als Aufgabe vorgeschlagen werden.")
        elif kind == "sender_ignore":
            sender = _clean_text(value.get("sender") or rule.get("key"))
            if sender:
                lines.append(f"Absender {sender} wurde im Lernen-Reiter ignoriert.")
    return lines[:8]
