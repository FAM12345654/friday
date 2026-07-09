# Friday Local Ollama Real Project Apply Dry Run

## Ziel

Dieser Schritt setzt einen Dry-Run-Baustein fuer den spaeteren echten Apply auf
`friday/config.py` um.

Der Dry Run schreibt nichts und aktiviert Ollama nicht.

## Umgesetzt

- Neuer Baustein: `friday/app/local_ollama_real_project_apply_dry_run.py`
- Neue Tests: `friday/tests/test_local_ollama_real_project_apply_dry_run.py`
- Ausgabe geplanter Config-Zeilen
- Ausgabe verbindlicher Rollback-Zeilen
- Nutzung des bestehenden Real Project Apply Guards

## Dry-Run-Verhalten

Der Dry Run zeigt:

- aktuelle Ollama-Config-Zeilen,
- geplante Zielzeilen,
- ob sich eine Zeile aendern wuerde,
- Rollback-Zeilen fuer Mock-Fallback,
- blockierende Guard-Gruende.

Der Dry Run schreibt nicht:

- keine `friday/config.py`,
- keine Backup-Datei,
- keine Temp-Datei,
- keine Mobile-Datei,
- keine Datenbank.

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Modellaufruf.
- Kein Cloud-Fallback.
- Kein API-Key.
- Kein Versand.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt `False`.

## Tests

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply_dry_run.py friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
```

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Entscheidung

Der Dry Run ist umgesetzt.

Nicht freigegeben ist weiterhin:

- echter Write auf `friday/config.py`,
- automatisches Aktivieren von Ollama,
- API-/CLI-/Mobile-Apply.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Dry Run Readiness Gate:

- Dry Run, Guard und Writer gemeinsam pruefen,
- bestaetigen, dass kein Write erfolgt,
- danach entscheiden, ob ein echter Apply mit Rollback gebaut wird.

Status danach: Das Dry Run Readiness Gate ist in `FRIDAY_LOCAL_OLLAMA_REAL_PROJECT_APPLY_DRY_RUN_READINESS_GATE.md` dokumentiert.
