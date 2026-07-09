# Friday Local Ollama Real Project Apply Gate Plan

## Ziel

Dieser Plan beschreibt, wie ein spaeterer echter Apply auf die Projektdatei
`friday/config.py` sicher geplant werden muss.

In diesem Schritt wird nichts aktiviert und keine Projekt-`config.py`
geschrieben.

## Aktueller Stand

- Der Config Preview ist vorhanden.
- Das Apply Gate ist vorhanden.
- Der isolierte Config Writer ist vorhanden.
- Das Readiness Gate fuer den isolierten Writer ist abgeschlossen.
- Die echte Projekt-`config.py` bleibt unveraendert.
- `ENABLE_LOCAL_OLLAMA = False` bleibt aktiv.

## Nicht umgesetzt in diesem Schritt

- Kein echter Write auf `friday/config.py`.
- Kein Setzen von `ENABLE_LOCAL_OLLAMA = True`.
- Kein API-Endpoint fuer echten Apply.
- Kein CLI-Apply-Button.
- Keine Mobile-Anbindung.
- Kein Ollama-Modellaufruf.
- Kein Cloud-Fallback.
- Kein Versand von Nachrichten.

## Voraussetzungen fuer einen spaeteren echten Projekt-Apply

Ein echter Apply darf spaeter nur erfolgen, wenn alle Punkte erfuellt sind:

1. Nutzer bestaetigt bewusst mit `OLLAMA AKTIVIEREN`.
2. Safety Smoke ist `PASS`.
3. Lokaler Ollama Health Check ist erfolgreich.
4. Base-URL ist lokal:
   - `http://localhost:11434`
   - oder `http://127.0.0.1:11434`
5. Modellname ist gesetzt.
6. `friday/config.py` enthaelt jede Ollama-Pflichtzeile genau einmal.
7. Vor dem Write wird ein Backup der alten Config erstellt.
8. Nach dem Write laufen Compilecheck, Fokus-Tests und Safety Smoke.
9. Bei Fehler wird automatisch auf sichere Mock-Konfiguration zurueckgesetzt.

## Geplanter harter Nutzer-Flow

Ein spaeterer echter Flow sollte diese Reihenfolge erzwingen:

```text
1. Config Preview anzeigen
2. Health Check ausfuehren
3. Safety Smoke ausfuehren
4. Exakten Token abfragen: OLLAMA AKTIVIEREN
5. Projekt-Config einmalig freigeben
6. Config schreiben
7. Compilecheck und Fokus-Tests ausfuehren
8. Safety Smoke erneut ausfuehren
9. Ergebnis anzeigen
```

Wichtig: Der Apply darf nicht automatisch beim App-Start, API-Start oder Mobile-Start passieren.

## Geplante Zielwerte

Erlaubte Zielwerte fuer den spaeteren lokalen Apply:

```python
ENABLE_LOCAL_OLLAMA = True
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1"
OLLAMA_TIMEOUT_SECONDS = 5
```

## Geplanter Rollback

Bei jedem Fehler muss Friday auf diese Werte zurueckfallen:

```python
ENABLE_LOCAL_OLLAMA = False
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = ""
OLLAMA_TIMEOUT_SECONDS = 5
```

Rollback ist Pflicht bei:

- fehlgeschlagenem Compilecheck,
- fehlgeschlagenen Fokus-Tests,
- fehlgeschlagenem Safety Smoke,
- fehlgeschlagenem lokalem Health Check,
- nicht-lokaler Base-URL,
- fehlenden oder doppelten Config-Zeilen,
- unerwarteter Aenderung an externen Safety-Flags.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Kein echter E-Mail-/WhatsApp-/SMS-Versand.
- Keine echten Kalendertermine.
- Kein Cloud-KI-Fallback.
- Kein API-Key.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- Die echte Projekt-`config.py` bleibt in diesem Schritt unveraendert.

## Tests fuer einen spaeteren echten Projekt-Apply

Ein spaeterer technischer Apply muss mindestens diese Pruefungen ausfuehren:

```powershell
python -m pytest friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_local_ollama_runtime.py friday/tests/test_ai_task_forwarding_draft.py
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Entscheidung

Der echte Projekt-Apply ist geplant, aber noch nicht freigegeben.

Aktuell bleibt der sichere Zustand:

- Mock-Fallback aktiv.
- `ENABLE_LOCAL_OLLAMA = False`.
- Kein echter Config-Write.
- Kein echter Modellaufruf.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Guard:

- einen separaten Guard bauen, der ausdruecklich entscheidet, ob die echte
  Projekt-`config.py` ueberhaupt beschrieben werden darf,
- weiterhin ohne Write,
- weiterhin ohne API-/CLI-/Mobile-Anbindung,
- danach erst einen echten Apply-Schritt vorbereiten.
