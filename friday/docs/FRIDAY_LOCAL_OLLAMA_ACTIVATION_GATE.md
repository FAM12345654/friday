# Friday Local Ollama Activation Gate

## Ziel

Dieses Gate macht den lokalen KI-Status sichtbar, ohne Friday automatisch auf echte Modellaufrufe umzuschalten.
Friday bleibt standardmaessig beim lokalen Mock-Provider.

## Umgesetzter Umfang

- Neuer read-only Gate-Baustein: `friday/app/local_ollama_activation_gate.py`.
- Neuer API-Endpunkt: `GET /api/ai/status`.
- Der Endpunkt zeigt:
  - aktiven Provider,
  - Mock-Fallback,
  - Ollama-Flag,
  - Modell-Konfiguration,
  - lokale URL-Pruefung,
  - optionalen Health-Check-Status,
  - Safety-Status.

## Aktivierungslogik

Ollama gilt nur dann als bereit, wenn alle Bedingungen stimmen:

- `ENABLE_LOCAL_OLLAMA = True`
- `OLLAMA_MODEL` ist gesetzt
- `OLLAMA_BASE_URL` ist lokal (`localhost` oder `127.0.0.1`)
- Safety-Flags sind weiterhin locked
- optionaler Health Check ist erfolgreich

Solange eine Bedingung fehlt, bleibt Friday beim Mock-Fallback.

## Safety-Grenzen

- Kein Cloud-Fallback.
- Kein OpenAI-/Claude-/Anthropic-Aufruf.
- Kein echter E-Mail- oder WhatsApp-Versand.
- Kein automatischer Health Check im normalen Statuspfad.
- Kein Persistieren von Modellantworten.
- Keine Datenbankschema-Aenderung.

## Tests

- `friday/tests/test_local_ollama_activation_gate.py`
- `friday/tests/test_friday_api_ai_status.py`

## Nutzerhinweis

Wenn du spaeter echtes lokales Ollama nutzen willst, brauchst du lokal auf dem Windows-PC:

```powershell
ollama pull llama3.1
```

Danach muss ein eigener Konfigurations-/Freigabe-Schritt folgen. Dieser Schritt aktiviert Ollama noch nicht dauerhaft.

## Naechster sinnvoller Schritt

Local Ollama User Setup Guide: kurze Anleitung, wie Ollama lokal installiert, ein Modell geladen und Friday danach sicher getestet wird.
