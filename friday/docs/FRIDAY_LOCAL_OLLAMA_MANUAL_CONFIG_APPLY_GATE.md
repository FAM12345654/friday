# Friday Local Ollama Manual Config Apply Gate

## Ziel

Dieses Gate prueft, ob eine spaetere manuelle Ollama-Konfiguration vorbereitet werden duerfte.
Es schreibt keine Konfiguration und aktiviert Ollama nicht automatisch.

## Umgesetzter Umfang

- Neuer Guard-Baustein: `friday/app/local_ollama_config_apply_guard.py`
- Neuer API-Endpunkt: `POST /api/ai/ollama/config-apply-gate`
- Harter Token: `OLLAMA AKTIVIEREN`
- Guard prueft:
  - Config Preview ist enable-ready,
  - harter Token stimmt exakt,
  - Safety Smoke wurde als bestanden gemeldet,
  - lokaler Ollama Health Check wurde als bestanden gemeldet.

## Wichtige Grenze

Auch wenn der Guard `allowed=True` liefert:

- `config.py` wird nicht veraendert.
- `ENABLE_LOCAL_OLLAMA` bleibt unveraendert.
- `OLLAMA_MODEL` bleibt unveraendert.
- Es wird kein Modell aufgerufen.
- Es wird nichts gesendet.

Der Guard meldet nur: `ready_for_manual_config_edit`.

## Beispiel

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/ai/ollama/config-apply-gate" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"model":"llama3.1","base_url":"http://localhost:11434","approval_token":"OLLAMA AKTIVIEREN","scanner_smoke_passed":true,"health_check_passed":true}'
```

## Safety-Bewertung

- Kein Cloud-Fallback.
- Kein API-Key.
- Kein echter E-Mail-/WhatsApp-Versand.
- Kein automatischer Config-Write.
- Keine Datenbankschema-Aenderung.
- Kein Mobile-OTA erforderlich.

## Naechster sinnvoller Schritt

Local Ollama Config Apply Documentation:

- genau dokumentieren, welche Zeilen manuell in `config.py` geaendert wuerden,
- weiterhin nur nach Guard, Tests und bewusstem Nutzerwunsch.

Status danach: Die manuelle Apply-Dokumentation ist in `FRIDAY_LOCAL_OLLAMA_CONFIG_APPLY_DOCUMENTATION.md` vorhanden.
