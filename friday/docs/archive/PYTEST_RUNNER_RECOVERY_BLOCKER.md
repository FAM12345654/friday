# Pytest Runner Recovery Blocker

## Ziel

Dieses Dokument haelt den aktuellen Validierungs-Blocker fest, damit der Review-Batch-CLI-Apply-Block nicht voreilig als Readiness-Gate abgeschlossen wird.

## Aktueller Stand

Die lokale Review-Batch-CLI-Apply-Implementierung ist eingebaut und direkte lokale Smoke-Pruefungen sind erfolgreich.

Ein finales Readiness-Gate wird aber noch nicht erstellt, weil die vollstaendige pytest-Regression aktuell nicht ausfuehrbar ist.

## Gepruefte Runner-Wege

| Weg | Ergebnis |
|---|---|
| `functions.shell_command` mit `python -m pytest ...` | blockiert durch `CreateProcessAsUserW failed: 5` |
| Node-Runner mit `python` | startet Python `3.14.5`, aber `pytest` fehlt |
| Codex-Bundle-Python | startet, aber `pytest` fehlt |
| `uv run --offline --with pytest ...` mit globalem Cache | blockiert durch Cache-Permission-Fehler |
| `uv run --offline --with pytest ...` mit Workspace-Cache | startet, aber `pytest` ist nicht im lokalen Cache |
| Suche nach installiertem `pytest.exe` | kein nutzbarer pytest-Runner gefunden |

## Erfolgreiche Ersatzchecks

Folgende Checks konnten lokal ausgefuehrt werden:

```bash
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

Ergebnis:

- Compilecheck erfolgreich.
- Safety Smoke: `Overall: PASS`.
- Diff-Check sauber.

Zusatzpruefung:

- Direkter Mini-E2E-Smoke fuer Review-Batch-CLI-Apply: `PASS`.

## Nicht als abgeschlossen markieren

Noch nicht abgeschlossen:

- `python -m pytest friday/tests/test_interface_combined_review.py`
- `python -m pytest friday/tests`
- Review Batch Selection CLI Apply Readiness Gate

## Safety-Bewertung

- Keine Produktlogik in diesem Recovery-Dokument geaendert.
- Keine externen Aktionen eingebaut.
- Keine Datenbankschema-Aenderung.
- Kein Readiness-Gate ohne Full Regression.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Naechster Schritt

Sobald der normale Windows-Runner wieder funktioniert oder ein pytest-faehiger lokaler Python verfuegbar ist:

```bash
python -m pytest friday/tests/test_interface_combined_review.py
python -m pytest friday/tests/test_review_batch_apply_guard.py friday/tests/test_review_batch_apply_model.py
python -m pytest friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

Danach kann das **Review Batch Selection CLI Apply Readiness Gate** erstellt werden.
