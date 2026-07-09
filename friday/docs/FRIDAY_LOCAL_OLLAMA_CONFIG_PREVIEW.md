# Friday Local Ollama Config Preview

## Ziel

Friday kann jetzt eine geplante lokale Ollama-Konfiguration als Vorschau pruefen.
Es wird keine Konfiguration geschrieben und kein Modell aufgerufen.

## Umgesetzter Umfang

- Neuer Preview-Baustein: `friday/app/local_ollama_config_preview.py`
- Neuer API-Endpunkt: `GET /api/ai/ollama/config-preview`
- Tests fuer:
  - gueltiges lokales Modell,
  - fehlendes Modell,
  - nicht-lokale URL,
  - nicht angeforderte Aktivierung,
  - vorgeschlagene Config-Zeilen.

## Beispiel

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/ai/ollama/config-preview?model=llama3.1&base_url=http://localhost:11434"
```

## Safety-Grenzen

- `ENABLE_LOCAL_OLLAMA` bleibt unveraendert.
- Kein Cloud-Fallback.
- Kein OpenAI-/Claude-/Anthropic-Aufruf.
- Kein Ollama Live-Call.
- Kein echter E-Mail-/WhatsApp-Versand.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.

## Naechster sinnvoller Schritt

Local Ollama Manual Config Apply Gate:

- nur mit explizitem Nutzerwunsch,
- weiterhin Safety Smoke vor dem Umschalten,
- danach lokaler Health Check,
- danach erst Draft-Flow-Test.
