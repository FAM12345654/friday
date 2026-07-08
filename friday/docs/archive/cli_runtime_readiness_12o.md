# CLI Runtime Readiness 12O

## Ziel

Kurze Standortbestimmung des lokalen CLI-Runtimes nach den Stabilisierungsschritten `12C` bis `13P`.

## Lokal stabil abgesicherte Bereiche

| Bereich | Status | Absicherung |
|---|---|---|
| Hauptmenü / Run-Loop | stabil | `test_interface_main_menu_e2e.py`, `test_cli_flow.py` |
| Aufgabenmenü | stabil | `test_task_interface_flow.py` |
| Task Markdown Export | stabil | `export` via `export_tasks_markdown_to_default_path`, `test_task_markdown_export.py`, `test_interface_main_menu_e2e.py` |
| CLI Help / Command Overview | stabil | `test_handle_menu_choice_help_overview`, `test_run_can_open_help_then_exit` in `friday/tests/test_interface_main_menu_e2e.py`, `cli_help_overview_12q.md`, `cli_help_edge_cases_12r.md` |
| Local Model Diagnostic | stabil (reine Anzeige) | `cli_local_model_diagnostic_safety_status_13n`, `cli_local_model_diagnostic_help_hint_13p`, `cli_local_model_diagnostic_documentation_13q.md` |
| Task Create/Edit/Search/Done/Archive/Delete | stabil | tmp_path SQLite Tests in `test_task_interface_flow.py` |
| Review: Nachrichten-Vorschläge | stabil | `test_interface_message_review.py` |
| Review: Aufgaben-Vorschläge | stabil | `test_interface_task_suggestion_review.py` |
| Combined Review | stabil | `test_interface_combined_review.py` |
| Kalender-Slot-Auswahl (lokal) | lokal stabil | `test_interface_message_review.py`, `test_calendar_agent.py` |
| Safety Status | stabil | `test_interface_main_menu_e2e.py`, `test_startup.py` |
| Lokale User-Journeys | stabil | Review- und Task-Journey-Doku-Testabdeckung (`12E`, `12F`) |

## Teststatus

- Gesamter Testlauf: `python -m pytest friday/tests` → `256 passed`
- Kompilierung: `python -m compileall friday` → erfolgreich
- Whitespace/Diff-Check: `git diff --check` → sauber
- Fokus-Tests und Smoke-Checks sind in den begleitenden Doku-Dateien zusammengefasst.

## Bewusst deaktivierte externe Funktionen

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Safety-Bewertung

- Keine externen Aktionen in lokalen CLI-Flows.
- Keine echten Nachrichten gesendet.
- Keine echten Kalendertermine erstellt.
- Lokale SQLite-Datenhaltung (`local_data/friday.db`).
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht.
  - `"JA"` löscht.
  - `" JA "` bleibt durch `strip()` zulässig.

## Verweise

- [cli_docs_finalization_gate_12n.md](cli_docs_finalization_gate_12n.md)
- [cli_developer_smoke_guide_12j.md](cli_developer_smoke_guide_12j.md)
- [cli_test_index_12i.md](cli_test_index_12i.md)
- [README_USER.md](README_USER.md)

## Empfehlung für Build Step 13E

Als nächsten Schritt liegt ein kleiner lokaler Produkt-Planungs-Schritt nahe: `Build Step 13E – Kontakt-Kontext Planung`.
