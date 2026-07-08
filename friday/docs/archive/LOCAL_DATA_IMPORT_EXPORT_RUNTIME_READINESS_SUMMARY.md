# Local Data Import/Export Runtime Readiness Summary

## Ziel

Diese Summary beschreibt den aktuellen lokalen Runtime-Stand fuer Datenexport, Import-Review und Import-Apply.

Sie dient als kurze Betriebsuebersicht nach der finalen Dokumentationssynchronisierung.

## Lokal stabil verfuegbare Bereiche

| Bereich | Status | Schutz |
|---|---|---|
| Lokaler Datenexport | stabil | Safety Smoke, Guard, Token `DATEN EXPORTIEREN`, Ziel unter `local_data/exports/` |
| Import-Manifest-Review | stabil | read-only, keine Writes |
| Import-Dry-Run | stabil | read-only, prueft Exportdateien und lokale Safety-Flags |
| Import-Apply-Vorschau | stabil | read-only, kein Token, keine Writes |
| Import nach Freigabe anwenden | stabil | Backup-Schutz, Safety Smoke, Guard, Token `IMPORT ANWENDEN`, lokale SQLite |
| Backup-/Restore-Menue | stabil | getrennte Menuepunkte fuer Preview, Review und guarded Writes |

## CLI-Uebersicht

| Menuepunkt | Verhalten |
|---|---|
| `5. Lokaler Datenexport Vorschau anzeigen` | Export-Preview und guarded Export-Write |
| `6. Lokalen Datenimport pruefen` | Read-only Import-Review |
| `7. Import-Apply-Vorschau anzeigen` | Read-only Apply-Vorschau |
| `8. Import nach Freigabe anwenden` | Guarded lokaler Import-Apply |
| `9. Zurueck zum Hauptmenue` | Rueckkehr ohne Write |

## Testabdeckung

Fokusbereiche:

- `friday/tests/test_local_data_export_preview.py`
- `friday/tests/test_local_data_export_guard.py`
- `friday/tests/test_local_data_export_writer.py`
- `friday/tests/test_local_data_import_manifest_reader.py`
- `friday/tests/test_local_data_import_dry_run.py`
- `friday/tests/test_local_data_import_apply_preview.py`
- `friday/tests/test_local_data_import_apply_write_guard.py`
- `friday/tests/test_local_data_import_apply_writer.py`
- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_menu.py`

Aktueller akzeptierter Stand:

- `python -m pytest friday/tests` -> `677 passed`
- `python -m compileall friday` -> erfolgreich
- `python scripts/friday_safety_smoke.py` -> `Overall: PASS`
- `git diff --check` -> sauber

## Safety-Grenzen

Freigegeben:

- lokale Exportdateien unter `local_data/exports/`,
- read-only Import-Pruefung,
- read-only Apply-Vorschau,
- lokaler Apply in SQLite nach Schutzkette.

Nicht freigegeben:

- externe Aktionen,
- Netzwerk- oder Provider-Aufrufe,
- Cloud-Integrationen,
- echte Nachrichten,
- echte Kalendertermine,
- Restore in aktive Projektdateien,
- automatischer Import ohne Token,
- Datenbankschema-Aenderungen im Runtime-Pfad,
- Import von Secrets, Tokens, `.env`, privaten Roh-Nachrichten oder sensiblen Kontakt-Freitexten.

## Safety-Flags

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Betriebsbewertung

Der lokale Datenexport-/Import-Runtime-Bereich ist bereit fuer lokale Nutzung im aktuellen Friday-CLI-Stand.

Writes sind klar getrennt, tokenpflichtig und durch Safety Smoke, Guards und Tests abgesichert.

## Empfehlung fuer naechsten Build Step

Local Data Import/Export Smoke Guide: eine sehr kurze Entwickler-/Nutzer-Pruefanleitung fuer diesen Runtime-Bereich erstellen, damit nach spaeteren Aenderungen gezielt Export/Import/Apply geprueft werden kann.
