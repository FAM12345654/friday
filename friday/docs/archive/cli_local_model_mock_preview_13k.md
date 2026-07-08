# Local Model Mock Preview 13K

## Ziel

Diese Phase ergänzt einen isolierten Vorschau-Pfad auf Basis des vorhandenen lokalen Mock-Adapters.

## Umfang

- Vorschau-Funktion ohne Verbindung zu produktiven CLI-Flows.
- Keine Task-/Message-/Review-Integration.
- Kein externer Provider-Aufruf, keine Netzwerkaktion.
- Keine API-Keys oder Cloud-Abhängigkeit.

## Implementierung

- Neue Datei: `friday/app/local_model_preview.py`
- Dataclass: `LocalModelPreview`
  - `prompt: str`
  - `result: LocalModelMockResult`
  - `readiness: LocalModelReadinessStatus`
  - `preview_only: bool`
  - `product_flow_connected: bool`
- Funktion: `preview_local_model_response(prompt)`
  - nutzt ausschließlich `LocalModelMockAdapter`
  - setzt `preview_only=True`
  - setzt `product_flow_connected=False`
  - gibt `LocalModelMockResult` und `LocalModelReadinessStatus` mit zurück

## Tests

- `friday/tests/test_local_model_mock_preview.py`
  - `test_preview_local_model_response_uses_mock_adapter`
  - `test_preview_local_model_response_includes_readiness_status`
  - `test_preview_local_model_response_handles_empty_prompt`
  - `test_preview_local_model_response_is_deterministic`

## Safety-Bewertung

- Keine externen Modellaufrufe.
- Keine Ollama-/LiteLLM-/OpenAI-Calls.
- Keine API-Keys.
- Keine externen Nachrichten, keine echten Termine.
- Safety-Flags unverändert.
- Delete-Policy unverändert:
  - `"ja"` löscht nicht,
  - `"JA"` löscht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung für Build Step 13L

- 13L sollte als **Local Model Preview Readiness Gate** die Isolation validieren.
- Kriterien bleiben: keine Produktfluss-Anbindung, kein externer Aufruf, stabile Deterministik.
