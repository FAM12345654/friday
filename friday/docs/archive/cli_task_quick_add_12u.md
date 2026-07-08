# CLI Task Quick Add 12U

## Ziel

Schnelle lokale Aufgabeingabe mit nur einem Titel.

## Neuer CLI-Pfad

- Aufgabenmenüpunkt: `9. Aufgabe schnell erfassen`
- Rückkehr bleibt: `8. Zurück zum Hauptmenü`

## Verhalten

- Prompt: `Schnelle Aufgabe:`
- Titel ist erforderlich.
- Standardwerte:
  - Kategorie: `sonstiges`
  - Priorität: `normal`
  - Fälligkeitsdatum: leer / `None`
  - Notizen: leer / `None`

## Absicherung und Rückgabewerte

- Erfolgsnachricht: `Aufgabe wurde schnell erstellt.`
- Leerer Titel: `Eine Aufgabe braucht mindestens einen Titel.`
- Erfolgsfluss setzt direkt über die bestehende lokale `create_task(...)`-Logik auf dem lokal gespeicherten Task-Agent.

## Safety-Bewertung

- Lokale Task-Erstellung über bestehende SQLite-Datenhaltung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Änderung.
- Delete-Policy unverändert.

## Tests

- `test_quick_add_task_from_input_creates_local_task_with_defaults`
- `test_quick_add_task_from_input_rejects_empty_title`
- optional: `test_task_menu_quick_add_then_back`

## Verweise

- Build Step 12U
- [CLI Documentation Index 12L](cli_documentation_index_12l.md)
