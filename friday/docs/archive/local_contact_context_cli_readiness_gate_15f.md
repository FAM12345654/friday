# Contact CLI Readiness Gate 15F

## Ziel

15F schließt den Contact-CLI-Block 15A bis 15E ab.

Geprüft wurde:

- Kontakt-Kontext-Menü sichtbar,
- Kontakte anzeigen und suchen,
- Bearbeiten als Draft,
- Speichern nur mit hartem Token,
- Vergessen/Löschen nur mit hartem Token,
- keine externen Aktionen.

## Geprüfte CLI-Funktionen

| Bereich | Status |
|---|---|
| Hauptmenüpunkt `9. Kontakt-Kontext anzeigen` | umgesetzt |
| Kontakte anzeigen | umgesetzt |
| Kontakt suchen | umgesetzt |
| Bearbeiten als Vorschau | umgesetzt |
| Speichern mit `SPEICHERN` | umgesetzt |
| Speichern bei `ja`/`JA` blockiert | umgesetzt |
| Kontakt vergessen mit `KONTAKT LÖSCHEN` | umgesetzt |
| falsche Löschbestätigung blockiert | umgesetzt |
| Rückkehr zum Hauptmenü | umgesetzt |

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Kontaktimport.
- Speichern nur nach explizitem Token `SPEICHERN`.
- Löschen nur nach explizitem Token `KONTAKT LÖSCHEN`.
- Keine Datenbankschema-Änderung in 15F.
- Task-Delete-Policy unverändert.
- Safety-Flags unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`

## Tests

Relevante Tests:

- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_contact_context_repository.py`
- vollständige Suite `friday/tests`

Aktueller Stand nach 15E/15F:

- `python -m pytest friday/tests/test_interface_main_menu_e2e.py` -> grün
- `python -m pytest friday/tests/test_contact_context_repository.py` -> grün
- `python -m pytest friday/tests` -> grün
- `python -m compileall friday` -> grün
- `git diff --check` -> sauber

## Empfehlung für Build Step 16A

Nächster sinnvoller Schritt: `16A — Review Contact Integration Plan`.

Dabei sollte nur geplant werden, wie der Review unbekannte Kontakte erkennt. Noch keine automatische Speicherung und keine externe Aktion.
