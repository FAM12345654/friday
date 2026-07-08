# CLI Task Markdown Export Docs 13D

## Ziel

Dieses Dokument beschreibt den produktiv verfügbaren lokalen Markdown-Export für Aufgaben in der Friday-CLI.

## Neuer CLI-Pfad

- Aufgabenmenüpunkt: `10. Aufgaben als Markdown exportieren`
- Rückkehr bleibt: `8. Zurück zum Hauptmenü`
- Quick Add bleibt: `9. Aufgabe schnell erfassen`

## Verhalten

- Exportiert lokale Aufgaben als Markdown-Datei.
- Speichert in `local_data/exports/`.
- Dateiname enthält Zeitstempel:
  `friday_tasks_<YYYYMMDD_HHMMSS>.md`
- Erfolgstext:
  `Aufgaben wurden lokal exportiert: <pfad>`
- Fehlertext:
  `Aufgaben konnten nicht exportiert werden.`

## Sicherheit und Grenzen

- Kein freier Nutzerpfad.
- Kein Obsidian-/Cloud-Ziel.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Änderung.
- Delete-Policy bleibt unverändert.

## Tests

- `python -m pytest friday/tests/test_task_markdown_export.py`
- `python -m pytest friday/tests/test_interface_main_menu_e2e.py`
- `python -m pytest friday/tests`

## Sicherheitsflags

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Empfehlung für Build Step 13E

Als nächsten Schritt wird **Kontakt-Kontext Planung** empfohlen.
