"""Deterministic local relevance rules for task suggestions."""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Iterable, Mapping

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
MAX_AI_RELEVANCE_BODY_CHARS = 1500
THINK_BLOCK_RE = re.compile(r"(?is)<think>.*?</think>")
NOISE_SENDER_PATTERNS = (
    "instagram.com",
    "linkedin.com",
    "facebookmail.com",
    "noreply",
    "no-reply",
    "newsletter",
    "mailer-daemon",
    "marketing",
    "notification",
    "notifications@",
)


def _text_tokens(text: str) -> set[str]:
    """Return case-insensitive word tokens from local text."""
    return {match.group(0).casefold() for match in _TOKEN_RE.finditer(text or "")}


def _rule_value(rule: Mapping[str, Any]) -> Mapping[str, Any]:
    value = rule.get("value")
    if isinstance(value, Mapping):
        return value
    raw_value = rule.get("value_json")
    if isinstance(raw_value, str):
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, Mapping) else {}
    return {}


def _rule_enabled(rule: Mapping[str, Any]) -> bool:
    return bool(rule.get("enabled", True))


def _sender_matches_rule(sender: str | None, sender_key: str | None) -> bool:
    normalized_sender = str(sender or "").casefold()
    normalized_key = str(sender_key or "").casefold()
    return bool(normalized_key and normalized_key in normalized_sender)


def _learned_rules_mark_relevant(
    *,
    text: str,
    sender: str | None,
    learned_rules: Iterable[Mapping[str, Any]] | None,
) -> bool:
    tokens = _text_tokens(text)
    for rule in learned_rules or ():
        if not _rule_enabled(rule):
            continue
        kind = str(rule.get("kind") or "")
        value = _rule_value(rule)
        if kind == "sender_contact":
            if value.get("contact_type") == "kunde" and value.get("betreuer") == "philip":
                sender_key = str(rule.get("key") or value.get("sender") or "")
                if _sender_matches_rule(sender, sender_key):
                    return True
        if kind == "mail_topic_task_rule" and value.get("create_task") is True:
            sender_key = str(value.get("sender_key") or "")
            if sender_key and not _sender_matches_rule(sender, sender_key):
                continue
            topic_tokens = _text_tokens(str(value.get("topic") or ""))
            if topic_tokens and topic_tokens.intersection(tokens):
                return True
    return False


def is_relevant_for_user(
    *,
    text: str,
    sender_contact: Mapping[str, Any] | None = None,
    sender: str | None = None,
    learned_rules: Iterable[Mapping[str, Any]] | None = None,
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

    if _learned_rules_mark_relevant(
        text=text,
        sender=sender,
        learned_rules=learned_rules,
    ):
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


def _uncertain_relevance() -> dict[str, Any]:
    return {
        "relevant": True,
        "reason": "unsicher",
        "method": "unsicher",
    }


def _noise_text(*values: str | None) -> str:
    return " ".join(str(value or "") for value in values).casefold()


def _is_noise_sender(*, sender: str | None, subject: str | None, snippet: str | None) -> bool:
    text = _noise_text(sender, subject, snippet)
    return any(pattern in text for pattern in NOISE_SENDER_PATTERNS)


def _limited_body(body_full: str | None) -> str:
    return str(body_full or "").strip()[:MAX_AI_RELEVANCE_BODY_CHARS]


def _strip_think_blocks(value: str) -> str:
    return THINK_BLOCK_RE.sub("", value or "").strip()


def _extract_json_object_text(value: str) -> str:
    text = _strip_think_blocks(value)
    if not text:
        return ""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return text
    return text[start : end + 1]


def _normalize_ai_relevance_result(result: Mapping[str, Any] | str | None) -> Mapping[str, Any] | str | None:
    if isinstance(result, str):
        return _extract_json_object_text(result)
    return result


def _build_mail_relevance_prompt(body_full: str, context: Mapping[str, Any]) -> str:
    limited_body = _limited_body(body_full)
    return (
        "Du bist Friday und analysierst lokal eine Microsoft-Mail. "
        "Antworte ausschliesslich als JSON mit den Feldern "
        "relevant (boolean), reason (kurzer deutscher Text), confidence (0.0 bis 1.0). "
        "Frage: Betrifft diese Mail Philip Zeitler persoenlich oder das ganze Team Familienhelden? "
        "Keine externen Aktionen. Keine Zusammenfassung ausserhalb von JSON.\n\n"
        f"Absender: {context.get('sender') or '-'}\n"
        f"Empfaenger: {context.get('recipients_text') or '-'}\n"
        f"Betreff: {context.get('subject') or '-'}\n"
        f"Mail-Text-Ausschnitt max. {MAX_AI_RELEVANCE_BODY_CHARS} Zeichen:\n"
        f"{limited_body}"
    )


def decide_mail_relevance_with_local_ai(body_full: str, context: Mapping[str, Any]) -> dict[str, Any]:
    """Use the guarded local model provider for short second-opinion relevance checks."""
    if not str(body_full or "").strip():
        return _uncertain_relevance()
    from friday.app.local_model_provider import select_local_model_provider

    provider = select_local_model_provider()
    prompt = _build_mail_relevance_prompt(body_full, context)
    result = provider.generate_json(prompt, MAIL_RELEVANCE_AI_SCHEMA)
    validation = validate_model_json(
        MAIL_RELEVANCE_AI_SCHEMA,
        _normalize_ai_relevance_result(result.output),
    )
    if result.error or not validation.is_valid:
        return _uncertain_relevance()
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
    allow_ai: bool = True,
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

    if _is_noise_sender(sender=sender, subject=subject, snippet=snippet):
        return {
            "relevant": False,
            "reason": "noise",
            "method": "noise",
        }

    recipients_text = _recipient_text(recipients)
    body_text = str(body_full or "").strip()
    combined = " ".join(
        [
            str(subject or ""),
            str(snippet or ""),
            str(sender or ""),
            recipients_text,
            body_text,
        ]
    )
    tokens = _text_tokens(combined)
    recipient_tokens = _text_tokens(recipients_text)
    if USER_TRIGGER_WORDS.intersection(recipient_tokens):
        return {
            "relevant": True,
            "reason": "recipient",
            "method": "recipient",
        }
    if _mentions_all_partners(tokens):
        return {
            "relevant": True,
            "reason": "team",
            "method": "team",
        }
    if USER_TRIGGER_WORDS.intersection(tokens):
        return {
            "relevant": True,
            "reason": "name",
            "method": "name",
        }
    if sender_contact:
        betreuer = str(sender_contact.get("betreuer") or "").strip().casefold()
        if betreuer == "philip":
            return {
                "relevant": True,
                "reason": "betreuer",
                "method": "betreuer",
            }

    if body_text and allow_ai:
        decider = ai_decider or decide_mail_relevance_with_local_ai
        try:
            result = decider(
                _limited_body(body_text),
                {
                    "account": account_text,
                    "subject": subject or "",
                    "snippet": snippet or "",
                    "sender": sender or "",
                    "recipients_text": recipients_text,
                },
            )
        except Exception:
            return _uncertain_relevance()
        validation = validate_model_json(
            MAIL_RELEVANCE_AI_SCHEMA,
            _normalize_ai_relevance_result(result),
        )
        if validation.is_valid:
            return {
                "relevant": bool(validation.data["relevant"]),
                "reason": str(validation.data["reason"])[:160],
                "method": "ki",
            }
        return _uncertain_relevance()

    if body_text and not allow_ai:
        return _uncertain_relevance()

    return {
        "relevant": False,
        "reason": "not_relevant",
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
