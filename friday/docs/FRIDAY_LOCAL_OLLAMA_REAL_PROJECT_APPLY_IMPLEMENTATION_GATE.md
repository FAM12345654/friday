# Friday Local Ollama Real Project Apply Implementation Gate

## Ziel

Dieser Schritt setzt den echten Apply-Baustein fuer einen lokalen Ollama-Apply
um, verbindet ihn aber nicht mit CLI, API oder Mobile.

Der Baustein kann eine explizite `config.py` nur dann schreiben, wenn alle Gates
gruen sind und `execute_write=True` gesetzt ist.

## Umgesetzt

- Neuer Baustein: `friday/app/local_ollama_real_project_apply.py`
- Neue Tests: `friday/tests/test_local_ollama_real_project_apply.py`
- Pflicht fuer explizites `execute_write=True`
- Pflicht fuer Post-Write-Validation-Callback
- Automatischer Rollback bei fehlgeschlagener oder fehlerhafter Validation
- Tests schreiben nur auf `tmp_path`

## Nicht angebunden

- Keine CLI-Anbindung
- Keine API-Anbindung
- Keine Mobile-Anbindung
- Kein automatischer App-Start-Apply
- Kein echter Apply auf die aktuelle Projekt-`config.py`

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Modellaufruf im Apply-Baustein.
- Kein Cloud-Fallback.
- Kein API-Key.
- Kein Versand.
- Keine Kalenderaktion.
- Keine Datenbankschema-Aenderung.
- Keine Mobile-Aenderung.
- `friday/config.py` bleibt in diesem Schritt unveraendert.
- `ENABLE_LOCAL_OLLAMA` bleibt im echten Projekt `False`.

## Rollback

Rollback wird technisch erzwungen, wenn:

- die Post-Write-Validation `False` liefert,
- die Post-Write-Validation eine Exception ausloest.

Dann wird die Backup-Datei des Writers zurueck in die Config geschrieben.

## Tests

Fokus-Tests:

```powershell
python -m pytest friday/tests/test_local_ollama_real_project_apply.py friday/tests/test_local_ollama_real_project_apply_dry_run.py friday/tests/test_local_ollama_real_project_apply_guard.py friday/tests/test_local_ollama_config_apply_writer.py friday/tests/test_local_ollama_config_apply_guard.py friday/tests/test_local_ollama_config_preview.py friday/tests/test_local_ollama_activation_gate.py friday/tests/test_ai_task_forwarding_draft.py
```

Full Regression:

```powershell
python -m pytest friday/tests
python -m compileall friday friday-api
python scripts/friday_safety_smoke.py
git diff --check
```

## Entscheidung

Der echte Apply-Baustein ist isoliert umgesetzt.

Nicht freigegeben ist weiterhin:

- ein Produkt-Button,
- ein API-Endpunkt,
- ein CLI-Menuepunkt,
- ein automatischer echter Apply auf die aktuelle Projekt-`config.py`.

## Empfehlung fuer den naechsten Build Step

Local Ollama Real Project Apply Implementation Readiness Gate:

- Apply-Baustein, Dry Run, Guard und Writer gemeinsam pruefen,
- bestaetigen, dass keine Produktanbindung existiert,
- entscheiden, ob die echte lokale Aktivierung manuell durchgefuehrt werden soll.
