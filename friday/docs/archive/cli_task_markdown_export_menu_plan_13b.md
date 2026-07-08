# CLI Task Markdown Export Menu Plan 13B

## Ziel

Dieses Dokument fasst die Implementierung des geplanten CLI-Menüpunkts aus Build 13B zusammen.

## Aktueller Stand

Der Export-Menüpunkt wurde in Schritt **13C** umgesetzt.

- `10. Aufgaben als Markdown exportieren` ist im Aufgabenmenü verfügbar.
- `show_task_menu()` nutzt die neue Bereichsbreite `Auswahl (1-10):`.
- Export läuft über den vorhandenen sicheren Wrapper:
  `export_tasks_markdown_to_default_path`.
- Kein Nutzerpfad und keine externen Aktionen.

`13B` blieb die reine Planungsphase; `13C` enthielt die tatsächliche CLI-Umsetzung.

## Geplantes Verhalten (jetzt umgesetzt)

- Nutzer wählt `10` im Aufgabenmenü.
- Friday sammelt lokale Aufgaben (`open`, `done`, `archived`).
- Export wird lokal nach
  `local_data/exports/friday_tasks_<timestamp>.md` geschrieben.
- Erfolgsmeldung: `Aufgaben wurden lokal exportiert: <pfad>`.
- Fehlerfall: `Aufgaben konnten nicht exportiert werden.`

## Safety-Grenzen

- Keine externen Aktionen.
- Kein freier Nutzerpfad.
- Lokale Verarbeitung bleibt aktiv.
- Keine echten Nachrichten, WhatsApp, E-Mails, SMS, Kalender-, Wetter- oder Musikaktionen.
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht,
  - `"JA"` löscht,
  - `" JA "` bleibt durch `strip()` zugelassen.

## Verweise

- Implementierung in `friday/app/menu.py`.
- Implementierung in `friday/app/interface.py`.
- Tests: `test_interface_main_menu_e2e.py`, `test_menu.py`, `test_task_interface_flow.py`,
  `test_task_markdown_export.py`.
