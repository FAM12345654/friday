"""Conservative local detection of completed WhatsApp conversations."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from friday.app.local_model_provider import select_local_model_provider
from friday.app.whatsapp_inbox_store import (
    WhatsAppConversationResolution,
    read_whatsapp_conversation,
    resolve_whatsapp_conversation,
)


MIN_AI_CONFIDENCE = 0.90
_NEGATED_COMPLETION = re.compile(
    r"\b(?:nicht|noch\s+nicht)\s+(?:erledigt|geklaert|geklärt|abgeschlossen)\b",
    re.IGNORECASE,
)
_EXPLICIT_COMPLETION = re.compile(
    r"\b(?:ist\s+erledigt|hat\s+sich\s+erledigt|ist\s+geklaert|ist\s+geklärt|"
    r"thema\s+ist\s+durch|alles\s+erledigt|alles\s+geklaert|alles\s+geklärt|"
    r"abgeschlossen)\b",
    re.IGNORECASE,
)


def _not_resolved(reason: str, provider: str = "deterministic") -> WhatsAppConversationResolution:
    return WhatsAppConversationResolution(
        resolved=False,
        hidden_count=0,
        confidence=0.0,
        reason=reason,
        provider=provider,
    )


def classify_and_resolve_whatsapp_reply(
    *,
    chat_id: str,
    reply_text: str,
    db_path: Path | str | None = None,
    provider: Any | None = None,
) -> WhatsAppConversationResolution:
    """Hide a local conversation only after a high-confidence completion signal."""
    normalized_reply = " ".join(str(reply_text or "").split())
    if not normalized_reply:
        return _not_resolved("empty_reply")
    if _NEGATED_COMPLETION.search(normalized_reply):
        return _not_resolved("completion_negated")
    if _EXPLICIT_COMPLETION.search(normalized_reply):
        return resolve_whatsapp_conversation(
            chat_id,
            confidence=1.0,
            reason="explicit_completion_reply",
            provider="deterministic",
            db_path=db_path,
        )

    conversation = read_whatsapp_conversation(chat_id, db_path=db_path)
    if not conversation:
        return _not_resolved("no_active_conversation")

    selected_provider = provider or select_local_model_provider()
    prompt = (
        "Pruefe konservativ, ob die folgende eigene WhatsApp-Antwort das Thema eindeutig "
        "abschliesst. Antworte nur mit JSON. resolved darf nur true sein, wenn keine offene "
        "Frage, Aufgabe oder Zusage mehr uebrig bleibt.\n"
        f"Verlauf: {json.dumps([item.get('body', '') for item in conversation], ensure_ascii=False)}\n"
        f"Eigene Antwort: {normalized_reply}"
    )
    result = selected_provider.generate_json(
        prompt,
        {
            "type": "object",
            "properties": {
                "resolved": {"type": "boolean"},
                "confidence": {"type": "number"},
                "reason": {"type": "string"},
            },
            "required": ["resolved", "confidence", "reason"],
        },
    )
    output = result.output if isinstance(result.output, dict) else {}
    confidence = max(0.0, min(float(output.get("confidence") or 0.0), 1.0))
    if output.get("resolved") is not True or confidence < MIN_AI_CONFIDENCE:
        return _not_resolved("ai_not_confident", result.provider)
    return resolve_whatsapp_conversation(
        chat_id,
        confidence=confidence,
        reason=str(output.get("reason") or "ai_completion_reply"),
        provider=result.provider,
        db_path=db_path,
    )
