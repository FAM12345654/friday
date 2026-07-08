# CLI UX Text Consistency 12D

## Vereinheitlichte Textmuster

| Situation | Text |
|---|---|
| Ungültige Auswahl im Menü oder Bereich | `Ungültige Auswahl. Bitte erneut versuchen.` |
| Ungültige Aufgaben-ID | `Ungültige Aufgaben-ID.` |
| Aufgabe nicht gefunden | `Aufgabe wurde nicht gefunden.` |
| Ungültige Priorität | `Ungültige Priorität.` |
| Delete ohne exakte Bestätigung | `Löschen wurde abgebrochen.` |
| Aufgabe erstellt | `Aufgabe wurde erstellt.` |
| Aufgabe aktualisiert | `Aufgabe wurde aktualisiert.` |
| Aufgabe erledigt | `Aufgabe wurde als erledigt markiert.` |
| Aufgabe archiviert | `Aufgabe wurde archiviert.` |
| Aufgabe gelöscht | `Aufgabe wurde dauerhaft gelöscht.` |

## Bewusst unveränderte Texte
- `Löschen wurde abgebrochen.` bleibt unverändert; die Bestätigung ist weiterhin case-sensitive (`JA`).
- Der Delete-Flow akzeptiert weiterhin ` JA ` durch `.strip()` wie bisher.
- Vorschlagsspezifische Meldungen (`Vorschlags-ID`, `Kalender-Slot...`) wurden nicht umbenannt, damit Review-Tests weiterhin auf bestehendes Verhalten passen.

## Tests
- `friday/tests/test_interface_main_menu_e2e.py`
  - `test_handle_menu_choice_invalid_input`
  - `test_handle_menu_choice_empty_or_whitespace_input_is_invalid`
  - `test_task_menu_invalid_input_returns_to_loop_then_back`
  - `test_task_menu_multiple_invalid_inputs_then_back`
  - `test_review_pending_suggestions_invalid_area_then_exit_keeps_open`
- `friday/tests/test_task_interface_flow.py`
  - `test_create_task_from_input_creates_local_task`
  - `test_edit_task_from_input_changes_provided_values`
  - `test_edit_task_from_input_rejects_invalid_priority`
  - `test_edit_task_from_input_unknown_id_prints_not_found`
  - `test_task_delete_from_input_rejects_lowercase_ja`
  - `test_task_delete_from_input_requires_confirmation`
  - `test_task_delete_from_input_deletes_after_exact_ja`

## Safety-Bewertung
- Keine externen Aktionen.
- Lokale Datenhaltung über SQLite mit `tmp_path` für neue textbezogene Testfälle.
- Sicherheitsflags unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Keine Datenbankschema-Änderung.
- Keine Änderungen an Löschelogik oder Bestätigungslogik.

## Empfehlung für Build Step 12E
- Nächster Schritt: eine kleine End-to-End-Journey als E2E-Test ergänzen
  (Start → Hauptmenü → Aufgabenmenü → erstellen → suchen/filtern → erledigen/archivieren → zurück → Exit),
  weiterhin ohne neue Logik, nur mit stabiler Testabdeckung.
