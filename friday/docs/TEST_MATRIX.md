# Friday Test Matrix

## Ziel

Uebersicht ueber relevante Testbereiche nach dem Stand `1084 passed, 4 skipped`.

## Teststand

- Full Regression: `1084 passed, 4 skipped`
- `python -m compileall friday`: erfolgreich
- `python scripts/friday_safety_smoke.py`: `Overall: PASS`
- `git diff --check`: sauber

## Testbereiche

| Bereich | Testdateien / Beispiele | Status |
|---|---|---|
| Startup / Config | `test_startup.py`, `test_date_utils.py` | stabil |
| CLI Core / Menues | `test_menu.py`, `test_cli_flow.py`, `test_interface_main_menu_e2e.py` | stabil |
| Tasks | `test_task_repository.py`, `test_task_agent.py`, `test_task_interface_flow.py` | stabil |
| Quick Add | `test_quick_add_parser.py`, CLI-E2E | stabil |
| Recurring Tasks | `test_task_repository.py`, `test_database.py` | stabil; kein Duplikat bei erneutem Done |
| Markdown Export | `test_task_markdown_export.py` | stabil inkl. Wiederholungsanzeige |
| Day Planning | `test_day_planning_preview.py`, `test_day_planning_renderer.py`, CLI-E2E | read-only stabil |
| Messages / Review | `test_message_agent.py`, `test_interface_message_review.py`, `test_interface_combined_review.py` | lokal stabil |
| Task Suggestions | `test_task_suggestion_repository.py`, `test_interface_task_suggestion_review.py` | lokal stabil |
| Review Activity / Batch | `test_review_activity_*.py`, `test_review_batch_*.py` | lokal/gated stabil |
| Contact Context | `test_contact_context_*.py`, CLI-E2E | lokal/gated stabil |
| Sensitive Guards | `test_sensitive_contact_context_guard.py`, Obsidian/Contact Tests | stabil |
| Obsidian | `test_obsidian_brain.py`, `test_obsidian_guard.py`, `test_obsidian_note_preview.py` | preview/gated stabil |
| Backup / Restore | `test_backup_*.py`, `test_restore_*.py`, CLI-E2E | lokal/gated stabil |
| Local Data Export / Import | `test_local_data_*` | lokal/gated stabil |
| Privacy Dashboard / Cleanup | `test_privacy_*.py` | read-only/gated stabil |
| Local AI / Ollama | `test_local_model_*.py`, `test_local_ollama_*.py` | mock/opt-in stabil |
| E-Mail Draft-only | `test_email_draft_model.py`, CLI-E2E | lokal, preview-only, kein Versand |
| Safety Scanners | `test_forbidden_import_scanner.py`, `test_no_network_scanner.py`, `test_no_input_print_scanner.py`, `test_safety_flag_regression_scanner.py`, `test_scanner_smoke_script.py` | stabil |

## Safety-Testabdeckung

- Keine externen Aktionen in Produktflows.
- Safety-Flags bleiben auf sicheren Werten.
- Harte Tokens bleiben erforderlich.
- Scanner Smoke prueft blockierte Imports, Netzwerk, Input/Print, Flags und Tokens.
- Lokale tmp_path-SQLite-Tests schuetzen echte Nutzerdaten.

## Hinweis

Historische Detail-Gates liegen unter `friday/docs/archive/` und werden nicht mehr als aktive Steuerungsdokumente gefuehrt.


## 1.0 User Acceptance

| Test | Status |
|---|---|
| riday/tests/test_user_acceptance_journey.py | lokale End-to-End-Akzeptanzreise vorhanden |
| Full Regression | 1084 passed, 4 skipped |

## Post-1.0 UX-Doku

| Bereich | Empfehlung |
|---|---|
| CLI-Hilfe und Rueckkehrhinweise | `python -m pytest friday/tests/test_interface_main_menu_e2e.py` |
| Basis-CLI-Flows | `python -m pytest friday/tests/test_cli_flow.py` |
| Vollstaendige lokale Regression | `python -m pytest friday/tests` |

## 1.1G Full Regression

| Command | Ergebnis |
|---|---|
| `python -m pytest friday/tests` | `1084 passed, 4 skipped` |
| `python -m compileall friday` | erfolgreich |
| `python scripts\friday_safety_smoke.py` | `Overall: PASS` |
| `git diff --check` | sauber |
