"""Deterministic local relevance rules for task suggestions."""

from __future__ import annotations

import re
from typing import Any, Callable, Mapping

from friday.app.model_output_validator import validate_model_json


USER_TRIGGER_WORDS = {"philip", "phips", "ph", "zeitler"}
PARTNER_TRIGGER_WORDS = {
    "philip": {"philip", "phips", "ph", "zeitler"},
    "alex": {"alex"},
    "flo": {"flo", "florian"},
}
SHARED_MAILBOX_IDENTIFIERS = {"office@familienhelden.at", "office_familienhelden_at"}
PERSONAL_MAILBOX_IDENTIFIERS = {"philip@familienhelden.at", "philip_familienhelden_at"}
_TOKEN_RE = re.compile(r"[0-9A-Za-zÄÖÜäöüß]+")

MAIL_RELEVANCE_AI_SCHEMA: dict[str, Any] = {
    "required": ["relevant", "reason", "confidence"],
    "properties": {
        "relevant": "bool",
        "reason": "str",
        "confidence": "number",
    },
    "min_confidence": 0.0,
}

MailRelevanceAIDecider = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


def _text_tokens(text: str) -> set[str]:
    """Return case-insensitive word tokens from local text."""
    return {match.group(0).casefold() for match in _TOKEN_RE.finditer(text or "")}


def is_relevant_for_user(
    *,
    text: str,
    sender_contact: Mapping[str, Any] | None = None,
) -> bool:
    """Return whether a task-like message should become a Friday task.

    This intentionally stays deterministic and local. A task-like message is
    relevant when it explicitly mentions Philip/Phips/PH/Zeitler as a whole
    word, or when the known sender contact is a customer assigned to Philip.
    """

    if sender_contact:
        betreuer = str(sender_contact.get("betreuer") or "").strip().casefold()
        if betreuer == "philip":
            return True

    return bool(USER_TRIGGER_WORDS.intersection(_text_tokens(text)))


def _recipient_text(recipients: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None) -> str:
    parts: list[str] = []
    for item in recipients or ():
        if not isinstance(item, Mapping):
            continue
        parts.append(str(item.get("name") or ""))
        parts.append(str(item.get("address") or ""))
        parts.append(str(item.get("label") or ""))
    return " ".join(parts)


def _mailbox_tokens(value: str | None) -> set[str]:
    lowered = str(value or "").strip().casefold()
    return {lowered, lowered.replace("@", "_").replace(".", "_")}


def _is_shared_mailbox(account: str | None) -> bool:
    tokens = _mailbox_tokens(account)
    return bool(tokens.intersection(SHARED_MAILBOX_IDENTIFIERS))


def _is_personal_mailbox(account: str | None) -> bool:
    tokens = _mailbox_tokens(account)
    return bool(tokens.intersection(PERSONAL_MAILBOX_IDENTIFIERS))


def _mentions_all_partners(tokens: set[str]) -> bool:
    return all(bool(words.intersection(tokens)) for words in PARTNER_TRIGGER_WORDS.values())


def _fallback_relevance() -> dict[str, Any]:
    return {
        "relevant": True,
        "reason": "ai_unavailable_conservative_include",
        "method": "fallback",
    }


def _build_mail_relevance_prompt(body_full: str, context: Mapping[str, Any]) -> str:
    return (
        "Du bist Friday und analysierst lokal eine Microsoft-Mail. "
        "Antworte ausschliesslich als JSON mit den Feldern "
        "relevant (boolean), reason (kurzer deutscher Text), confidence (0.0 bis 1.0). "
        "Frage: Betrifft diese Mail Philip Zeitler persoenlich oder das ganze Team Familienhelden? "
        "Keine externen Aktionen. Keine Zusammenfassung ausserhalb von JSON.\n\n"
        f"Absender: {context.get('sender') or '-'}\n"
        f"Empfaenger: {context.get('recipients_text') or '-'}\n"
        f"Betreff: {context.get('subject') or '-'}\n"
        "Voller Mail-Text:\n"
        f"{body_full}"
    )


def decide_mail_relevance_with_local_ai(body_full: str, context: Mapping[str, Any]) -> dict[str, Any]:
    """Use the guarded local model provider for full-body relevance checks."""
    if not str(body_full or "").strip():
        return _fallback_relevance()
    from friday.app.local_model_provider import select_local_model_provider

    provider = select_local_model_provider()
    prompt = _build_mail_relevance_prompt(body_full, context)
    result = provider.generate_json(prompt, MAIL_RELEVANCE_AI_SCHEMA)
    validation = validate_model_json(MAIL_RELEVANCE_AI_SCHEMA, result.output)
    if result.error or not validation.is_valid:
        return _fallback_relevance()
    reason = str(validation.data.get("reason") or "KI: relevant").strip()
    return {
        "relevant": bool(validation.data.get("relevant")),
        "reason": reason[:160],
        "confidence": float(validation.data.get("confidence") or 0.0),
    }


def determine_mail_relevance(
    *,
    account: str | None,
    subject: str | None,
    snippet: str | None,
    sender: str | None,
    recipients: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    sender_contact: Mapping[str, Any] | None = None,
    body_full: str | None = None,
    ai_decider: MailRelevanceAIDecider | None = None,
) -> dict[str, Any]:
    """Return deterministic local relevance for Microsoft mail previews.

    Shared office mailboxes show only messages relevant to Philip by default.
    Personal mailboxes remain fully visible.
    """
    account_text = str(account or "").strip()
    if _is_personal_mailbox(account_text) or not _is_shared_mailbox(account_text):
        return {
            "relevant": True,
            "reason": "personal_mailbox",
            "method": "deterministic",
        }

    combined = " ".join(
        [
            str(subject or ""),
            str(snippet or ""),
            str(sender or ""),
            _recipient_text(recipients),
        ]
    )
    tokens = _text_tokens(combined)
    if _mentions_all_partners(tokens):
        return {
            "relevant": True,
            "reason": "team_all_partners",
            "method": "deterministic",
        }
    if USER_TRIGGER_WORDS.intersection(tokens):
        return {
            "relevant": True,
            "reason": "philip_trigger",
            "method": "deterministic",
        }
    if sender_contact:
        betreuer = str(sender_contact.get("betreuer") or "").strip().casefold()
        if betreuer == "philip":
            return {
                "relevant": True,
                "reason": "customer_betreuer_philip",
                "method": "deterministic",
            }

    body_text = str(body_full or "").strip()
    if body_text:
        recipients_text = _recipient_text(recipients)
        decider = ai_decider or decide_mail_relevance_with_local_ai
        try:
            result = decider(
                body_text,
                {
                    "account": account_text,
                    "subject": subject or "",
                    "snippet": snippet or "",
                    "sender": sender or "",
                    "recipients_text": recipients_text,
                },
            )
        except Exception:
            return _fallback_relevance()
        validation = validate_model_json(MAIL_RELEVANCE_AI_SCHEMA, result)
        if validation.is_valid:
            return {
                "relevant": bool(validation.data["relevant"]),
                "reason": str(validation.data["reason"])[:160],
                "method": "ai",
            }
        if result.get("method") == "fallback":
            return _fallback_relevance()
        return _fallback_relevance()

    return {
        "relevant": False,
        "reason": "office_not_relevant",
        "method": "deterministic",
    }


def is_mail_relevant(
    *,
    account: str | None,
    subject: str | None,
    snippet: str | None,
    sender: str | None,
    recipients: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...] | None = None,
    sender_contact: Mapping[str, Any] | None = None,
) -> bool:
    """Return whether a mail preview should be visible in the default view."""
    return bool(
        determine_mail_relevance(
            account=account,
            subject=subject,
            snippet=snippet,
            sender=sender,
            recipients=recipients,
            sender_contact=sender_contact,
            body_full=None,
        )["relevant"]
    )
