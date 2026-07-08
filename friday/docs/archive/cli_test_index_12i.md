# CLI Test Index 12I

## Ziel

Dieser Index listet die vorhandenen CLI-Tests und ordnet sie den lokalen CLI-Flows zu. Ziel ist ein schneller Überblick für die nächste Planung ohne neue Produktlogik.

## Testdateien

| Datei | Fokus | Hinweise |
|---|---|---|
| `friday/tests/test_interface_main_menu_e2e.py` | Hauptmenü, Run-Loop, Task- und Review-Navigationspfade | Starker Fokus auf robuste Eingaben am Menü- und Rücksprungpfad |
| `friday/tests/test_task_interface_flow.py` | Task-Flow (Create/Edit/Search/Done/Archive/Delete) im Aufgabenmenü | Umfassende Validierung einzelner Task-Workflows |
| `friday/tests/test_interface_message_review.py` | Nachrichten-Vorschlags-Review | Freigeben, ablehnen, bearbeiten, invalid Action/Robustheit |
| `friday/tests/test_interface_task_suggestion_review.py` | Aufgaben-Vorschlags-Review | Freigeben, ablehnen, bearbeiten, robuste Actions |
| `friday/tests/test_interface_combined_review.py` | Kombinierter Review-Pfad | Übersicht, Bereichswechsel, Journey über Nachrichten- und Aufgaben-Vorschläge |
| `friday/tests/test_cli_flow.py` | Basisschnittstelle `run()`/`handle_menu_choice`-Smoke | Optionenzuweisung und Exit-Verhalten |
| `friday/tests/test_interface.py` | Interface-Inkonsistenzen | Sicherstellung von Methode-Aufrufbarkeit/Anzeigeeinbindung |
| `friday/tests/test_interface_main_menu_e2e.py` | Safety/Review/Task-Journey | Safety-Status, ungültige Eingaben, Exit, Review-Loop |
| `friday/tests/test_task_agent.py` | Task-Agent-Logik für lokale Workflows | Create/Edit/Archive/Delete/Done auf Agent-Ebene |
| `friday/tests/test_task_repository.py` | Datenzugriff für Task-Operationen | Such-/Filter-/Status-/Sortierlogik |
| `friday/tests/test_task_suggestion_repository.py` | Task-Vorschlag-Repo | Suggestion-Lebenszyklus, Konvertierung |
| `friday/tests/test_message_agent.py` | Message-Agent + lokale Suggestion-Generierung | Lokale Erkennung, Vorschlagsstatuswechsel |
| `friday/tests/test_message_suggestion_repository.py` | Message-Vorschlags-Repo | Pending/Approve/Reject/Edit-Verhalten |
| `friday/tests/test_calendar_agent.py` | Kalendervorschlag-Flow | Lokale Slot-Generierung und Selektion |
| `friday/tests/test_startup.py` | Konfiguration/Safety | App-Name, Local-Mode, Safety-Flags, Demo-Date |
| `friday/tests/test_approval_flow.py` | Lokale Freigabepfade | Rückgabewerte der lokalen Freigabe-Flow |
| `friday/tests/test_cli_flow.py` | CLI-Menü-Stabilität | Option 6 und Option 1, Exit, ungültige Eingabe |

## Coverage Matrix

| Bereich | Abgedeckte Fälle | Testdateien | Status | Offene Lücken |
|---|---|---|---|---|
| Main Menu | `0`-Beenden, `6` Review öffnen, ungültige Eingaben, Whitespace-Eingaben, Mehrfachfehler vor Exit | `friday/tests/test_interface_main_menu_e2e.py`, `friday/tests/test_cli_flow.py`, `friday/tests/test_interface.py` | gut abgedeckt | Keine harte Lücke auf Kernmenü-Ebene; weiterhin sinnvoll: zusätzliche vollständige E2E-Coverage für Menütexte/Zeileninhalte |
| Safety Status | Anzeige von Local/Live Flags | `friday/tests/test_interface_main_menu_e2e.py`, `friday/tests/test_startup.py` | gut abgedeckt | Keine bekannten offenen Lücken in der lokalen Safety-Anzeige |
| Task Create | Titel, Priorität, Pflichtfelder, erfolgreiche Erstellung | `friday/tests/test_task_interface_flow.py` | gut abgedeckt | Keine große Lücke erkannt |
| Task Edit | Edit bei Teil-/Leereingabe, ungültiger ID, ungültige Priorität | `friday/tests/test_task_interface_flow.py` | gut abgedeckt | Kein vollständiger Edit-journey-Test mit Menü-Rücksprung nach `x` im selben Lauf |
| Task Search/Filter | Textsuche, leere Suche, Filter ohne Treffer, leerer Query | `friday/tests/test_task_interface_flow.py` | gut abgedeckt | Keine Lücke erkannt |
| Task Done | Aufgabe erledigen, Wiederholter Aufruf, ungültige ID | `friday/tests/test_task_interface_flow.py`, `friday/tests/test_interface_main_menu_e2e.py` | gut abgedeckt | Keine bekannte Lücke |
| Task Archive | Archive-Flow, ungültige ID, bereits archivierter Status, Wiederholung | `friday/tests/test_task_interface_flow.py` | gut abgedeckt | Keine bekannte Lücke |
| Task Delete | Delete-Confirmation, `ja`-Case-Sensitivity, leer/invalid/nicht vorhanden | `friday/tests/test_task_interface_flow.py`, `friday/tests/test_interface_main_menu_e2e.py` | gut abgedeckt | Keine neue Lücke; weiterhin manuell auf Produktanforderung achten |
| Message Review | Freigeben/Ablehnen/Bearbeiten/Selection/Robustheit (Whitespace, Sonderzeichen, unbekannte Actions, Mehrfach-Invalid) | `friday/tests/test_interface_message_review.py`, `friday/tests/test_interface_combined_review.py` | gut abgedeckt | Bereichswechsel pro `z`/leer ist vorhanden, aber kein vollständig sequenzieller Wiederholungstest mit mehreren Sprüngen |
| Task Suggestion Review | Freigeben/Ablehnen/Bearbeiten/Robustheit; Doppelkonvertierungsschutz; kein externer Tasking | `friday/tests/test_interface_task_suggestion_review.py`, `friday/tests/test_interface_combined_review.py` | gut abgedeckt | Keine große Lücke erkannt |
| Combined Review | Öffnen über `6`, Aufgaben-/Nachrichtenbereich, Mehrfach-Ansichten, Rücksprung auf Hauptmenü | `friday/tests/test_interface_combined_review.py`, `friday/tests/test_interface_main_menu_e2e.py` | gut abgedeckt | Teilweise Lücke: weniger Tests zu langen Eingabesequenzen mit gemischten Wiederholungsrückkehrsoptionen |
| Calendar Slot Selection | Slot-Liste, ungültige Slot-ID, fehlende Slots, erneute Auswahl/Ersetzung | `friday/tests/test_interface_message_review.py`, `friday/tests/test_calendar_agent.py` | gut abgedeckt | Kein Lücke erkennbar |
| Full Local Task Journey | Start → Task erstellen → suchen/filter → erledigen/archivieren → Exit (in Kombination) | `friday/tests/test_interface_main_menu_e2e.py` | teilweise abgedeckt | Vollständige End-to-End-Kette inkl. Archive/Done-Varianten als separater konsolidierter Smoke-Case noch sinnvoll |
| Review Robustness | Whitespace/Sonderzeichen/Mehrfach-Invalid/kein Absturz bei Rückkehr | `friday/tests/test_interface_message_review.py`, `friday/tests/test_interface_task_suggestion_review.py`, `friday/tests/test_interface_combined_review.py` | gut abgedeckt | Keine große Lücke |
| CLI Text Consistency | Konsistente Fehlermeldungen, Konsistenz für Haupt-/Task-/Review-Flow | `friday/tests/test_interface_main_menu_e2e.py`, `friday/tests/test_task_interface_flow.py`, `friday/tests/test_interface_message_review.py`, `friday/tests/test_interface_task_suggestion_review.py` | teilweise abgedeckt | Ein paar Ausgaben sind noch textlich lokalisiert, aber die zentralen Invalid-/Fallback-Meldungen sind gut abgedeckt |

## Safety Coverage

- Keine externen Aktionen in den CLI-Tests (lokale Durchläufe mit temporärer SQLite).
- Lokale Datenbankpfade in den meisten CLI-E2E-Tests über `tmp_path` aufgebaut.
- Delete-Policy bleibt case-sensitive:
  - `"ja"` löscht nicht,
  - `"JA"` löscht,
  - (bestehendes Verhalten durch `strip()` erlaubt) `" JA "` als Löschen.
- Review-Freigaben bleiben lokal und lösen keinen echten Versand aus.
- Kalender-Slot-Auswahl bleibt lokal.
- Safety-Flags bleiben unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`

## Offene oder nächste sinnvolle Lücken

| Priorität | Bereich | Empfehlung |
|---|---|---|
| Mittel | Full Local Task Journey | Ergänzen oder dokumentieren, welche Task-Statusvarianten (done/archived) als vollständiger CLI-Smoke aktiv geprüft werden sollen. |
| Niedrig | Combined Review Rücksprungsequenzen | Sequenztest für mehrfaches Wechseln zwischen Nachrichten- und Aufgabenbereich mit Wiederholung von `z` und leerem Rücksprung. |
| Niedrig | CLI Text Consistency | Ggf. zentrale Erwartungstexte pro Hauptmenü- und Subflow in einer kleinen Smoke-Matrix testen. |

## Empfehlung für Build Step 12J

- Build Step 12J: eine kurze **CLI Developer Smoke Guide** ergänzen, die die stabilen Prüfkommandos nach Änderungen dokumentiert (Voll-Lauf, Review-Fokus, Compilecheck, Diff-Check).
