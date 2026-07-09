# Friday Local Ollama Real Project Apply Execution Plan

## Ziel

Dieser Plan beschreibt den finalen Ablauf fuer einen spaeteren echten Apply auf
die Projektdatei `friday/config.py`.

In diesem Schritt wird der Apply nicht ausgefuehrt.

## Aktueller sicherer Stand

- `ENABLE_LOCAL_OLLAMA = False`
- Mock-Fallback bleibt aktiv
- kein Write auf `friday/config.py`
- kein echter Modellaufruf
- kein Cloud-Fallback
- kein API-Key
- keine externen Aktionen
- keine Mobile-/CLI-/API-Apply-Anbindung

## Voraussetzung vor echter Ausfuehrung

Ein spaeterer echter Apply darf nur starten, wenn alle Punkte erfuellt sind:

1. Nutzer hat lokal Ollama installiert.
2. Ein lokales Modell ist geladen, z. B. `llama3.1`.
3. Config Preview ist gruen.
4. Real Project Apply Guard ist gruen.
5. Dry Run zeigt die erwarteten vier Config-Zeilen.
6. Safety Smoke ist `PASS`.
7. Lokaler Ollama Health Check ist `PASS`.
8. Nutzer bestaetigt exakt mit `OLLAMA AKTIVIEREN`.
9. Backup- und Rollback-Pfad sind vor dem Write bekannt.

## Finaler Apply-Ablauf

Der spaetere Apply muss diese Reihenfolge strikt einhalten:

1. `friday/config.py` lesen.
2. Bestehende Ollama-Zeilen validieren.
3. Config Preview bauen.
4. Real Project Apply Guard ausfuehren.
5. Dry Run ausfuehren und geplante Zeilen anzeigen.
6. Safety Smoke unmittelbar vor Write ausfuehren.
7. Lokalen Ollama Health Check unmittelbar vor Write ausfuehren.
8. Exakten Token `OLLAMA AKTIVIEREN` verlangen.
9. Backup der aktuellen `friday/config.py` erstellen.
10. Nur diese vier Zeilen schreiben:

```python
ENABLE_LOCAL_OLLAMA = True
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT_SECONDS = 5
```

11. `python -m compileall friday friday-api` ausfuehren.
12. Ollama-/AI-Fokus-Tests ausfuehren.
13. `python scripts/friday_safety_smoke.py` ausfuehren.
14. `python -m pytest friday/tests` ausfuehren.
15. Bei jedem Fehler Rollback ausfuehren.
16. Ergebnis dokumentieren.

## Rollback-Pflicht

Rollback muss diese sichere Mock-Konfiguration wiederherstellen:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

Rollback ist Pflicht bei:

- fehlgeschlagenem Compilecheck,
- fehlgeschlagenen Fokus-Tests,
- fehlgeschlagener Full Regression,
- fehlgeschlagenem Safety Smoke,
- fehlgeschlagenem lokalen Health Check,
- falschem Token,
- nicht-lokaler Base-URL,
- fehlenden oder doppelten Config-Zeilen,
- unerwarteter Aenderung an externen Safety-Flags.

## Nicht-Ziele

- Kein Cloud-Fallback.
- Kein OpenAI-/Claude-/Anthropic-Key.
- Kein echter Versand von E-Mail, WhatsApp oder SMS.
- Keine Kalenderaktion.
- Keine Datenbankschema-Aenderung.
- Keine automatische Aktivierung beim App-Start.
- Keine Mobile-Aktivierung ohne separates Gate.

## Tests fuer den spaeteren echten Apply

Ein spaeterer Apply muss mindestens diese Befehle ausfuehren:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply_dry_run.py friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_local_ollama_runtime.py friday/tests/test_ai_task_forwarding_draft.py
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
python -m pytest friday/tests
git diff --check
```

## Safety-Bewertung

- Keine Produktlogik in diesem Schritt geaendert.
- Keine externe Aktion.
- Kein echter Modellaufruf.
- Kein Write auf `friday/config.py`.
- `ENABLE_LOCAL_OLLAMA` bleibt `False`.
- Execution bleibt geplant, aber nicht ausgefuehrt.

## Entscheidung

Der echte Projekt-Apply ist als finaler Ablauf geplant, aber weiterhin nicht
ausgefuehrt.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Execution Readiness Gate:

- Execution Plan gegen Preview, Guard, Writer und Dry Run pruefen,
- bestaetigen, dass noch kein echter Write erfolgt,
- danach entscheiden, ob der echte Apply gebaut oder weiterhin manuell gehalten wird.

Status danach: Das Execution Readiness Gate ist in `FRIDAY_LOCAL_OLLAMA_REAL_PROJECT_APPLY_EXECUTION_READINESS_GATE.md` dokumentiert.
