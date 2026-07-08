# CLI Review Robustness 12H

## Geprüfte Bereiche
- Nachrichten-Vorschlags-Review
- Aufgaben-Vorschlags-Review

## Neue Testfälle
- `friday/tests/test_interface_message_review.py`
  - `test_review_pending_suggestions_whitespace_action_stays_open`
  - `test_review_pending_suggestions_special_character_action_stays_open`
  - `test_review_pending_suggestions_multiple_invalid_actions_then_return`
- `friday/tests/test_interface_task_suggestion_review.py`
  - `test_review_pending_task_suggestion_whitespace_action_stays_open`
  - `test_review_pending_task_suggestion_special_character_action_stays_open`
  - `test_review_pending_task_suggestion_multiple_invalid_actions_then_return`

## Erwartete Texte/Verhalten
- Bei whitespace-Action und Sonderzeichen-Action wird
  - `Ungültige Auswahl. Bitte erneut versuchen.` ausgegeben.
- Bei mehreren aufeinanderfolgenden ungültigen Actions bleibt der betroffene Vorschlag offen.
- Die Rückkehr aus der Detailansicht (`z`) bleibt stabil und führt zurück zur Review-Übersicht.

## Abgesicherte Robustheit
- Aktionen werden lokal ohne externe Nebenwirkungen verworfen, wenn sie ungültig sind.
- Die Review-Loops bleiben stabil bei fehlerhaften Eingaben.
- Die bestehende Delete-Policy bleibt unverändert.

## Safety
- Keine externen Aktionen.
- Nur lokale Tests mit temporärer SQLite-DB (`tmp_path`).
- Sicherheitsflags unverändert lokal-first (`*_REAL_* = False`, `REQUIRE_USER_APPROVAL = True`).
- `USE_SQLITE_STORAGE = True`.
- Keine Änderungen am Datenbankschema.

## Empfehlung für Build Step 12I
- Als nächsten Schritt die Rückkehr auf Bereichsebene (`z`/leere Eingabe) im Kombinations-Review zusätzlich mit expliziten Sequenz-Tests pro Bereich absichern.
