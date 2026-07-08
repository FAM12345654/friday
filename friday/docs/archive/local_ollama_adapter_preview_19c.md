# Local Ollama Adapter Preview 19C

## Ziel

Build Step 19C ergaenzt eine sichere Preview fuer einen moeglichen spaeteren lokalen Ollama-Adapter.

Dieser Schritt fuehrt keine echten Modellaufrufe aus:
- kein Netzwerk,
- kein Live-Check,
- kein Cloud-Fallback,
- keine Produktanbindung,
- keine Datenbankschema-Aenderung.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/local_ollama_adapter_preview.py` | Preview-only Ollama-Konfiguration, Health-Preview und Request-Preview |
| `friday/tests/test_local_ollama_adapter_preview.py` | Tests fuer Default-disabled, lokale URL-Regeln und No-Network-Verhalten |

## Konfiguration

Neue sichere Defaults:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

## Verhalten

| Situation | Ergebnis |
|---|---|
| Default | Adapter ist deaktiviert |
| Health-Check | meldet Preview-Status, fuehrt keinen Live-Check aus |
| Request Preview | baut Endpoint/Payload, fuehrt nichts aus |
| Nicht-lokale Base-URL | wird abgelehnt |
| Cloud-Fallback | wird abgelehnt |

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Modellaufrufe.
- Kein Netzwerk.
- Kein Cloud-Fallback.
- Keine automatische Produktentscheidung.
- Keine Task-/Review-/Kontakt-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Tests

- `python -m pytest friday/tests/test_local_ollama_adapter_preview.py`
- `python -m pytest friday/tests`

## Empfehlung fuer Build Step 19D

Build Step 19D sollte den Model Output Validator bauen:
- JSON-Struktur pruefen,
- unbekannte Felder ablehnen,
- Pflichtfelder pruefen,
- leere/ungueltige Antworten ablehnen,
- weiterhin ohne Produktanbindung.
