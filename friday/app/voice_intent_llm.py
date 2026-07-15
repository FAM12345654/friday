"""Optional local-LLM fallback for the deterministic voice intent parser.

When :func:`friday.app.voice_intent.parse_voice_command` returns ``unknown``,
the API can ask the guarded local model provider to map a free-form German or
English sentence onto one of the known intents. This is fully local: if the
active provider is the deterministic mock (Ollama off or unhealthy), the
fallback short-circuits and returns ``None`` so the request stays fast and
never depends on a model call.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Mapping

from friday.app import voice_intent
from friday.app.voice_intent import VoiceIntent
from friday.app.voice_synthesis import normalize_language

# Schema shape mirrors the other generate_json callers (todo_relevance,
# ai_task_forwarding_draft): a "required"/"properties" dict with simple
# type names as values.
VOICE_INTENT_LLM_SCHEMA: dict[str, Any] = {
    "required": ["intent", "argument", "language", "days_offset"],
    "properties": {
        "intent": "str",
        "argument": "str",
        "language": "str",
        "days_offset": "int",
    },
}

_INTENT_LINE = ", ".join(voice_intent.INTENTS)


def _build_prompt(text: str) -> str:
    """Return a compact German classification prompt for one sentence."""
    return (
        "Du bist Friday und ordnest lokal einen gesprochenen Befehl einer "
        "Absicht zu. Antworte ausschliesslich als JSON mit den Feldern "
        "intent, argument, language, days_offset. Keine externen Aktionen, "
        "keine Zusammenfassung ausserhalb von JSON.\n"
        f"intent muss genau einer dieser Werte sein: {_INTENT_LINE}.\n"
        "argument ist der Aufgabentitel oder die Suchbegriffe (leer, wenn "
        "keine).\n"
        "language ist \"de\" oder \"en\".\n"
        "days_offset ist eine ganze Zahl, nur fuer snooze_task relevant: "
        "1=morgen, 2=uebermorgen, 7=naechste Woche, sonst 1.\n\n"
        f"Satz: {text}"
    )


def _is_mock_provider(provider: Any) -> bool:
    """Return True when the provider is the deterministic local mock."""
    config = getattr(provider, "config", None)
    return bool(config is not None and getattr(config, "provider", None) == "mock")


def _normalize_language(value: Any) -> str:
    """Normalize the model's language field to \"de\" or \"en\" (default \"de\").

    Delegates to :func:`voice_synthesis.normalize_language` so language
    handling stays consistent across the voice stack (e.g. ``en-US`` -> ``en``).
    """
    return normalize_language(value)


def _clean_argument(value: Any) -> str:
    """Coerce the model's argument field to a cleaned single-line string."""
    return " ".join(str(value or "").split()).strip().strip(".!?")


def _coerce_days_offset(value: Any) -> int:
    """Coerce and clamp the days_offset field to the range 1..30 (default 1)."""
    try:
        offset = int(value)
    except (TypeError, ValueError):
        return 1
    return max(1, min(30, offset))


def resolve_intent_with_llm(
    text: str,
    *,
    provider: Any | None = None,
    today: str | None = None,
) -> VoiceIntent | None:
    """Map a free-form sentence to a :class:`VoiceIntent` via the local model.

    Returns ``None`` when the local provider is the mock, on any provider
    error, or on any validation failure. Never raises.
    """
    cleaned = " ".join(str(text or "").split()).strip()
    if not cleaned:
        return None

    try:
        if provider is None:
            from friday.app.local_model_provider import select_local_model_provider

            provider = select_local_model_provider()

        if _is_mock_provider(provider):
            return None

        result = provider.generate_json(_build_prompt(cleaned), VOICE_INTENT_LLM_SCHEMA)
        if result is None or getattr(result, "is_mock", False) or getattr(result, "error", None):
            return None

        output = getattr(result, "output", None)
        if not isinstance(output, Mapping):
            return None

        intent = str(output.get("intent") or "").strip()
        if intent not in voice_intent.INTENTS:
            return None

        language = _normalize_language(output.get("language"))
        argument = _clean_argument(output.get("argument"))

        snooze_until: str | None = None
        if intent == "snooze_task":
            effective_today = date.fromisoformat(today) if today else date.today()
            offset = _coerce_days_offset(output.get("days_offset"))
            snooze_until = (effective_today + timedelta(days=offset)).isoformat()

        return VoiceIntent(
            intent=intent,
            argument=argument,
            language=language,
            snooze_until=snooze_until,
        )
    except Exception:
        # Fallback must never make the API slower/fail; degrade to None.
        return None
