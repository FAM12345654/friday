# CLI Help Edge Cases 12R

## Ziel

Robustheitsfälle für den lokalen Help-/Command-Overview-Pfad in Build Step 12Q.

## Abgesicherte Fälle

- Help mehrfach öffnen.
- Ungültige Hauptmenü-Eingabe → Help → Exit.
- Aufgabenmenü öffnen, zurück → Help → Exit.
- Help bleibt reine Anzeige.

## Tests

- `test_run_can_open_help_multiple_times_then_exit`
- `test_run_invalid_input_then_help_then_exit`
- `test_run_task_menu_back_then_help_then_exit`

## Sicherheitsbewertung

- Help erzeugt keine externen Aktionen.
- Es werden keine externen Nachrichten gesendet.
- Es werden keine echten Kalendertermine erstellt.
- Keine Datenbankänderung im Help-Fluss.
- Safety-Flags bleiben lokal-only.
- Delete-Policy unverändert:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` löscht durch `strip()` weiterhin

## Ergebnis

- Help-Ausgabe verwendet den lokalen Header als `Lokaler CLI-Überblick:`.
- Die neuen Edge-Case-Tests ergänzen die Stabilität des Hauptmenü- und Laufpfades.

## Empfehlung für Build Step 12S

Help-Doku und Nutzer-Dokumentation um den Menüpunkt `8. Hilfe / Übersicht` ergänzen.
