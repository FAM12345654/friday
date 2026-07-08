# Friday Local Product Phase 4 Local AI Control Gate

## Ziel

Dieses Gate dokumentiert die kontrollierte lokale AI-Erweiterung nach dem MVP-GO.

Der Grundsatz bleibt:

- Mock bleibt Default,
- keine Cloud-AI,
- keine Produktflow-Live-Calls,
- keine Netzwerkaktion im Standard-Smoke,
- Ollama nur als lokale Preview.

## Neue Bausteine

| Datei | Zweck |
|---|---|
| `friday/app/local_model_settings.py` | Read-only Settings-Preview mit Mock als Default |
| `friday/app/local_model_health_preview.py` | Nicht-ausfuehrender Ollama-Health-Preview fuer `127.0.0.1` |
| `friday/app/local_model_validation_pipeline.py` | Strikte Komposition aus Validator und Logic Check |
| `friday/app/interface.py` | Read-only Local-AI-Diagnose im Sicherheitsstatus |
| `friday/tests/test_local_model_settings.py` | Tests fuer Mock-Default und Ollama-Preview-Settings |
| `friday/tests/test_local_model_health_preview.py` | Tests fuer nicht-ausfuehrenden Health-Preview |
| `friday/tests/test_local_model_validation_pipeline.py` | Tests fuer Validator+Logic-Check-Komposition |
| `friday/tests/test_interface_main_menu_e2e.py` | Tests fuer die read-only Local-AI-Diagnoseanzeige |

## Local Model Settings

Der sichere Default bleibt:

```text
provider = mock
mock_is_default = True
cloud_fallback_allowed = False
product_flow_connected = False
```

Ollama kann nur als Preview beschrieben werden.

## Local-AI-Diagnose im Sicherheitsstatus

Der Sicherheitsstatus zeigt zusaetzlich lokale Diagnosewerte:

- `ENABLE_LOCAL_OLLAMA`,
- ob ein Modell gesetzt ist,
- ob die konfigurierte Ollama-URL lokal erlaubt ist,
- dass kein Ollama Live-Health-Check automatisch ausgefuehrt wird.

Diese Anzeige ist read-only und startet keinen Netzwerk- oder Modellaufruf.

## Ollama Health Check Preview

Der Health Check Preview:

- beschreibt nur einen moeglichen lokalen Check,
- erlaubt nur `http://127.0.0.1...`,
- fuehrt keinen Netzwerkcall aus,
- ist nicht im Standard-Smoke,
- ist nicht an Produktflows angebunden.

## Model Output Validation + Logic Check

Die neue Pipeline akzeptiert lokale Modell-/Mock-Ausgaben nur, wenn:

- JSON/Schema-Validierung erfolgreich ist,
- keine unbekannten Felder unerlaubt auftauchen,
- Confidence-Anforderungen erfuellt sind,
- Logic Check keine riskanten Aktionen erkennt,
- sensible Kontaktbegriffe blockiert werden.

Riskante Aktionen wie `send_email`, `send_whatsapp`, `create_calendar_event` oder `obsidian_write` werden nicht akzeptiert.

## Validierungsstand

| Check | Ergebnis |
|---|---|
| Full Regression | `1065 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

## Safety-Bewertung

- Keine externen Aktionen.
- Keine Cloud-AI.
- Keine Produktflow-Live-Calls.
- Keine Datenbankschema-Aenderung.
- Kein Standard-Smoke-Netzwerkcheck.
- Mock bleibt Default.

## Ergebnis

Phase 4 ist kontrolliert umgesetzt: Friday kann Local-AI-Settings, einen Ollama-Health-Preview und eine strikte Validator/Logic-Check-Pipeline lokal modellieren, ohne echte Modellaufrufe zu starten.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Finales lokales Produktabschluss-Gate.
