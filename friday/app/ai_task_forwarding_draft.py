"""AI-assisted task forwarding drafts with local-first safety guards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from friday import config
from friday.app.local_model_provider import LocalModelProvider, select_local_model_provider
from friday.app.local_model_validation_pipeline import validate_and_logic_check_model_output
from friday.app.sensitive_contact_context_guard import check_sensitive_contact_context


VALID_FORWARD_CHANNELS = {"email", "whatsapp"}
AI_FORWARD_DRAFT_SCHEMA: dict[str, Any] = {
    "required": ["draft_text", "confidence"],
    "properties": {
        "draft_text": "string",
        "confidence": "number",
    },
    "min_confidence": 0.5,
}


@dataclass(frozen=True)
class AITaskForwardingDraft:
    """Preview-only draft generated through Friday's local AI provider layer."""

    task_id: int | None
    task_title: str
    contact_id: int | str | None
    contact_name: str
    channel: str
    target: str
    draft_text: str
    provider: str
    model: str
    is_mock: bool
    ai_connected: bool
    provider_output_used: bool
    validation_accepted: bool
    blocked_reasons: tuple[str, ...]
    approval_token_required: str
    preview_only: bool = True
    persisted: bool = False
    external_send_enabled: bool = False
    external_call_used: bool = False
    product_flow_connected: bool = True


def _clean(value: Any, fallback: str = "") -> str:
    """Normalize simple display values."""
    cleaned = " ".join(str(value or "").strip().split())
    return cleaned or fallback


def _approval_token_for(channel: str) -> str:
    return "WHATSAPP SENDEN" if channel == "whatsapp" else "EMAIL SENDEN"


def _target_for(contact: Mapping[str, Any], channel: str) -> str:
    if channel == "whatsapp":
        return _clean(contact.get("whatsapp_target"), "kein WhatsApp-Ziel gespeichert")
    return _clean(contact.get("email_address"), "keine E-Mail-Adresse gespeichert")


def _build_prompt(task: Mapping[str, Any], contact: Mapping[str, Any], channel: str, target: str) -> str:
    """Prompt template for a short, polite German forwarding draft."""
    title = _clean(task.get("title"), "diese Aufgabe")
    contact_name = _clean(contact.get("name"), "Kontakt")
    due_date = _clean(task.get("due_date"))
    notes = _clean(task.get("notes"))
    return "\n".join(
        line
        for line in (
            "Erstelle einen kurzen deutschen Weiterleiten-Entwurf.",
            f"Aufgabe: {title}",
            f"Kontakt: {contact_name}",
            f"Kanal: {channel}",
            f"Ziel: {target}",
            f"Faelligkeit: {due_date}" if due_date else "",
            f"Notiz: {notes}" if notes else "",
            "Formuliere kurz, freundlich und klar auf Deutsch.",
            "Antworte ausschliesslich als JSON mit draft_text und confidence.",
            "Keine Links, keine Signatur, keine Versandaktion ausloesen.",
        )
        if line
    )


def _build_template_draft(task: Mapping[str, Any], contact: Mapping[str, Any], channel: str, target: str) -> str:
    contact_name = _clean(contact.get("name"), "du")
    title = _clean(task.get("title"), "diese Aufgabe")
    due = _clean(task.get("due_date"))
    notes = _clean(task.get("notes"))
    channel_label = "WhatsApp" if channel == "whatsapp" else "E-Mail"

    lines = [
        f"Hallo {contact_name},",
        "",
        f'kannst du bitte die Aufgabe "{title}" übernehmen?',
    ]
    if due:
        lines.append(f"Fällig: {due}")
    if notes:
        lines.append(f"Hinweis: {notes}")
    lines.extend(
        [
            "",
            "Danke dir!",
            "",
            f"Kanal: {channel_label}",
            f"Ziel: {target}",
            "KI-Draft: lokaler Fallback.",
            "Noch nicht gesendet.",
        ]
    )
    return "\n".join(lines)


def _with_ai_label(draft_text: str, model: str) -> str:
    clean_draft = draft_text.strip()
    label = f"KI-Draft: {model or 'lokales Modell'} lokal."
    if "KI-Draft:" in clean_draft:
        return clean_draft
    return "\n".join([clean_draft, "", label, "Noch nicht gesendet."])


def _safety_reasons(*, channel: str, target: str, draft_text: str) -> tuple[str, ...]:
    reasons: list[str] = []
    if channel not in VALID_FORWARD_CHANNELS:
        reasons.append("Ungueltiger Weiterleiten-Kanal.")
    if target in {"keine E-Mail-Adresse gespeichert", "kein WhatsApp-Ziel gespeichert"}:
        reasons.append("Kontakt-Ziel fehlt fuer den gewaehlten Kanal.")
    guard = check_sensitive_contact_context(draft_text)
    if not guard.allowed:
        categories = ", ".join(guard.blocked_categories)
        reasons.append(f"Draft enthaelt sensible Kategorie: {categories}.")
    return tuple(reasons)


def build_ai_task_forwarding_draft(
    *,
    task: Mapping[str, Any],
    contact: Mapping[str, Any],
    channel: str,
    provider: LocalModelProvider | None = None,
) -> AITaskForwardingDraft:
    """Build a safe AI-assisted task forwarding draft without sending or persisting."""
    normalized_channel = _clean(channel).lower()
    if normalized_channel not in VALID_FORWARD_CHANNELS:
        normalized_channel = "email"

    selected_provider = provider or select_local_model_provider()
    target = _target_for(contact, normalized_channel)
    prompt = _build_prompt(task, contact, normalized_channel, target)
    provider_result = selected_provider.generate_json(prompt, AI_FORWARD_DRAFT_SCHEMA)

    provider_output_used = False
    validation_accepted = False
    blocked_reasons: list[str] = []
    draft_text = _build_template_draft(task, contact, normalized_channel, target)

    if not provider_result.is_mock and not provider_result.error:
        validation = validate_and_logic_check_model_output(
            schema=AI_FORWARD_DRAFT_SCHEMA,
            output=provider_result.output,
            purpose="message_draft",
        )
        validation_accepted = validation.accepted
        if validation.accepted:
            candidate_text = _clean(validation.validation.data.get("draft_text"))
            if candidate_text:
                draft_text = _with_ai_label(candidate_text, selected_provider.config.model)
                provider_output_used = True
        else:
            blocked_reasons.extend(validation.blocked_reasons)

    if provider_result.error:
        blocked_reasons.append(provider_result.error)

    blocked_reasons.extend(
        _safety_reasons(
            channel=normalized_channel,
            target=target,
            draft_text=draft_text,
        )
    )

    return AITaskForwardingDraft(
        task_id=task.get("id") if task.get("id") is not None else None,
        task_title=_clean(task.get("title"), "diese Aufgabe"),
        contact_id=contact.get("id") if contact.get("id") is not None else None,
        contact_name=_clean(contact.get("name"), "Unbekannter Kontakt"),
        channel=normalized_channel,
        target=target,
        draft_text=draft_text,
        provider=selected_provider.config.provider,
        model=selected_provider.config.model,
        is_mock=provider_result.is_mock,
        ai_connected=True,
        provider_output_used=provider_output_used,
        validation_accepted=validation_accepted,
        blocked_reasons=tuple(dict.fromkeys(blocked_reasons)),
        approval_token_required=_approval_token_for(normalized_channel),
        external_call_used=provider_result.external_call_used,
        external_send_enabled=False,
        persisted=False,
        preview_only=True,
        product_flow_connected=True,
    )


def ai_task_forwarding_safety_summary() -> dict[str, bool]:
    """Return read-only safety metadata for the connected AI draft flow."""
    return {
        "ai_draft_flow_connected": True,
        "cloud_model_enabled": False,
        "real_email_enabled": config.ENABLE_REAL_EMAIL,
        "real_whatsapp_enabled": config.ENABLE_REAL_WHATSAPP,
        "external_send_enabled": False,
        "requires_user_approval": config.REQUIRE_USER_APPROVAL,
    }
