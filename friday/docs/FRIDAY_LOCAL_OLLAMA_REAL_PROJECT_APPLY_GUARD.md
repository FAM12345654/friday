# Friday Local Ollama Real Project Apply Guard

## Ziel

Dieser Schritt setzt einen read-only Guard fuer einen spaeteren echten Apply auf
die Projektdatei `friday/config.py` um.

Der Guard schreibt nichts. Er entscheidet nur, ob ein spaeterer separater
Apply-Schritt ueberhaupt vorbereitet werden duerfte.

## Umgesetzt

- Neuer Guard: `friday/app/local_ollama_real_project_apply_guard.py`
- Neue Tests: `friday/tests/test_local_ollama_real_project_apply_guard.py`
- Keine CLI-Anbindung
- Keine Mobile-Anbindung
- Kein API-Apply-Endpunkt
- Kein Write auf `friday/config.py`

## Guard-Pruefungen

Der Guard verlangt:

- exaktes Token `OLLAMA AKTIVIEREN`,
- Safety Smoke als bestanden,
- lokalen Ollama Health Check als bestanden,
- lokale Base-URL,
- gesetzten Modellnamen,
- echten Projekt-`config.py`-Pfad,
- vorhandene und eindeutige Ollama-Config-Zeilen,
- gueltigen Timeout zwischen 1 und 60 Sekunden.

## Blockierte Faelle

Der Guard blockiert:

- falsches Token,
- fehlgeschlagenen Safety Smoke,
- fehlgeschlagenen Health Check,
- nicht-lokale URLs,
- leeren Modellnamen,
- falschen Config-Pfad,
- fehlende oder doppelte Config-Zeilen,
- ungueltigen Timeout.

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Cloud-Fallback.
- Kein API-Key.
- Kein Modellaufruf.
- Kein Versand.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- `friday/config.py` bleibt unveraendert.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt `False`.

## Tests

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
```

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Entscheidung

Der echte Projekt-Apply bleibt weiterhin nicht freigegeben.

Der neue Guard ist eine weitere Sicherheitsstufe vor einem spaeteren Apply.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Readiness Gate:

- Guard, Writer, Preview und Apply Gate gemeinsam dokumentiert pruefen,
- bestaetigen, dass kein echter Write erfolgt,
- erst danach einen getrennten echten Apply-Schritt entscheiden.

Status danach: Das Readiness Gate ist in `FRIDAY_LOCAL_OLLAMA_REAL_PROJECT_APPLY_READINESS_GATE.md` dokumentiert.
