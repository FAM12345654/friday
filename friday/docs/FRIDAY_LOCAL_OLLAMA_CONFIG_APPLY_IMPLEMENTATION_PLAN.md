# Friday Local Ollama Config Apply Implementation Plan

## Ziel

Dieser Plan beschreibt, wie ein spaeterer technischer Apply-Schritt fuer lokales Ollama sicher umgesetzt werden duerfte.
In diesem Schritt wird nichts angewendet.

## Nicht umgesetzt in diesem Schritt

- Keine Aenderung an `friday/config.py`.
- Kein Setzen von `ENABLE_LOCAL_OLLAMA = True`.
- Kein Ollama-Live-Call.
- Kein Cloud-Fallback.
- Kein API-Key.
- Kein echter E-Mail-/WhatsApp-Versand.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.

## Voraussetzungen fuer einen spaeteren Apply

Ein spaeterer Apply darf nur gebaut werden, wenn vorher alle Gates gruen sind:

- `FRIDAY_LOCAL_OLLAMA_USER_SETUP_GUIDE.md` wurde befolgt.
- `FRIDAY_LOCAL_OLLAMA_CONFIG_PREVIEW.md` liefert eine sichere Vorschau.
- `FRIDAY_LOCAL_OLLAMA_MANUAL_CONFIG_APPLY_GATE.md` liefert `allowed=True`.
- Safety Smoke ist `PASS`.
- Lokaler Ollama Health Check ist `PASS`.
- Nutzer bestaetigt bewusst mit `OLLAMA AKTIVIEREN`.

## Geplanter Apply-Ablauf

Ein spaeterer technischer Apply duerfte nur diese Schritte ausfuehren:

1. Aktuelle `friday/config.py` lesen.
2. Aktuelle Ollama-Zeilen sichern.
3. Safety Smoke ausfuehren und PASS erzwingen.
4. Config Preview erneut ausfuehren.
5. Apply Guard mit Token `OLLAMA AKTIVIEREN` pruefen.
6. Nur diese Zeilen ersetzen:

```python
ENABLE_LOCAL_OLLAMA = True
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT_SECONDS = 5
```

7. `python -m compileall friday friday-api` ausfuehren.
8. Fokus-Tests fuer Ollama und AI-Draft ausfuehren.
9. `python scripts/friday_safety_smoke.py` ausfuehren.
10. Bei Fehlern sofort Rollback auf Mock-Konfiguration.

## Geplanter Rollback

Rollback muss deterministisch sein:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

Rollback ist Pflicht, wenn:

- Compilecheck fehlschlaegt.
- Fokus-Tests fehlschlagen.
- Safety Smoke fehlschlaegt.
- Ollama Health Check fehlschlaegt.
- eine nicht-lokale URL erkannt wird.
- `git diff --check` fehlschlaegt.

## Sicherheitsgrenzen

- Ollama darf nur lokal ueber `localhost` oder `127.0.0.1` genutzt werden.
- Kein Cloud-Modell darf als Fallback genutzt werden.
- Modellantworten duerfen keine externen Aktionen ausloesen.
- Task-Weiterleiten bleibt Draft-only.
- E-Mail/WhatsApp bleiben deaktiviert.
- Bei jedem Fehler bleibt oder wird Mock Provider aktiv.

## Geplante Tests fuer spaeteren Apply

```powershell
python -m pytest friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_local_ollama_runtime.py friday/tests/test_ai_task_forwarding_draft.py
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Akzeptanzkriterien fuer spaeteren Apply

- `config.py` enthaelt nur erlaubte lokale Ollama-Werte.
- Alle Safety-Flags fuer externe Aktionen bleiben deaktiviert.
- Mock-Fallback bleibt funktionsfaehig.
- Health Check ist lokal und erfolgreich.
- Task-Forwarding-Draft funktioniert mit lokalem Provider oder faellt sicher auf Mock zurueck.
- Full Regression bleibt gruen.

## Empfehlung fuer naechsten Build Step

Local Ollama Runtime Smoke Plan:

- planen, wie ein lokaler Ollama-Live-Test einmalig und kontrolliert ausgefuehrt wird,
- weiterhin ohne Versand,
- weiterhin mit Mock-Fallback,
- keine dauerhafte Aktivierung ohne separates Apply-Gate.
