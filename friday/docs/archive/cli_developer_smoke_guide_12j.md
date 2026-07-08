# CLI Developer Smoke Guide 12J

## Ziel

Nach jeder gezielten CLI-Änderung an Friday schnell verifizierbar prüfen, dass die wichtigsten lokalen Test- und Stabilitätschecks grün sind.

## Empfohlene Schnellprüfung (lokal)

```bash
python -m pytest friday/tests/test_interface_main_menu_e2e.py
python -m pytest friday/tests/test_task_interface_flow.py
python -m pytest friday/tests/test_interface_combined_review.py
python -m pytest friday/tests/test_interface_message_review.py friday/tests/test_interface_task_suggestion_review.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Erwartete Nutzung

- Nach jeder kleinen Änderung an Menüführung, Task-Flow oder Review-Flow.
- Vor einem Commit/Abschluss eines lokalen Build-Steps.
- Wenn ein neuer Edge-Case-Test ergänzt wurde.

## Kurzbeschreibung der Checks

- `test_interface_main_menu_e2e.py`
  Prüft Hauptmenü-Loop, stabile Rücksprünge und Exit-Pfade.
- `test_task_interface_flow.py`
  Prüft lokale Task-Workflows inkl. Create/Edit/Search/Done/Archive/Delete.
- `test_interface_combined_review.py`
  Prüft kombinierten Review-Pfad im Menü.
- `test_interface_message_review.py` und `test_interface_task_suggestion_review.py`
  Prüfen Vorschlags-Review mit robusten Action-Eingaben.
- `friday/tests`
  Voller CLI-Regressionstest über die komplette Testsuite.
- `compileall friday`
  Stellt sicher, dass die Python-Dateien syntaktisch kompilierbar bleiben.
- `friday_safety_smoke.py`
  Prueft lokale Safety-Scanner fuer verbotene Imports, Netzwerk-Muster, Input/Print, Safety-Flags und Approval-Tokens.
- `git diff --check`
  Prüft Format/Whitespace- und Patchqualität.

## Safety-Hinweis

Dieser Guide ändert keine Produktionslogik.

- Keine externen Aktionen werden aktiviert.
- Lokaler Betrieb bleibt mit SQLite (`tmp_path`) in den CLI-Tests.
- Keine Datenbankschema-Änderungen.
- Safety-Flags bleiben unverändert.
- Keine Obsidian-, Local-AI- oder Self-Building-Ausfuehrung wird durch den Guide aktiviert.

## Empfehlung für nächsten Schritt (12K)

- Optional einen kurzen `README`-Block ergänzen, der auf diesen Guide verweist, damit neue Kolleg*innen denselben Ablauf übernehmen.
