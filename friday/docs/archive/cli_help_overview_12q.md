# CLI Help Overview 12Q

## Ziel

Dokumentiert den neuen lokalen Hilfe-/Command-Overview-Pfad in der CLI nach Build Step 12Q.

## Neuer CLI-Pfad

- Hauptmenüpunkt: `8. Hilfe / Übersicht`
- Zeigt eine reine lokale Übersicht und lokale Sicherheitsgrenzen an.
- Keine Statusänderungen, keine Datenbank-Schreibvorgänge, keine externen Aktionen.
- Die Hilfe enthält den lokalen Diagnosehinweis:
  `Lokale Modell-Diagnose: siehe Sicherheitsstatus. Es werden keine externen Modellaufrufe genutzt.`

## Abgesicherte Bereiche

- Hilfe kann über das Hauptmenü geöffnet werden.
- Die `run()`-Schleife bleibt stabil: Help anzeigen → weiterlaufen → Exit bleibt möglich.
- Aufruf beendet mit `7` wie gewohnt.
- Reine Informationsausgabe ohne Änderung an Task-, Review-, Delete- oder Archive-Logik.

## Safety-Bewertung

- Keine externen Aktionen (keine echten Nachrichten, keine echten Kalendertermine).
- Keine neuen Provider-Aufrufe.
- Lokale SQLite bleibt unberührt.
- Safety-Flags bleiben unverändert lokal-only.
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` löscht durch `strip()` weiterhin

## Tests

- `test_handle_menu_choice_help_overview`
- `test_run_can_open_help_then_exit`
- Full Regression: `python -m pytest friday/tests`

## Empfehlung für Build Step 12R

Build Step 12R sollte Help-/Robustheitsfälle ergänzen:
- Help nach ungültiger Eingabe
- Mehrfaches Help-Öffnen
- Help-Wechsel mit Aufgaben- und Hauptmenüfluss
- weiterhin stabiler Exit
