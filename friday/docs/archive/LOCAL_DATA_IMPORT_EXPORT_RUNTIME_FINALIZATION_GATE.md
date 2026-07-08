# Local Data Import/Export Runtime Finalization Gate

## Ziel

Dieses Gate schliesst den lokalen Datenexport- und Import-Review-Runtime-Block zusammen ab. Es fasst den stabilen Stand fuer Export, Import-Review und Apply-Vorschau zusammen.

## Gepruefte Runtime-Bereiche

| Bereich | Status | Ergebnis |
|---|---|---|
| Local Data Export Preview | stabil | Vorschau ohne Dateioperation |
| Local Data Export Guard | stabil | harter Token, Zielpfad und Safety Smoke |
| Local Data Export Writer | stabil | schreibt nur guard-basiert unter `local_data/exports/` |
| Local Data Export CLI Approval | stabil | CLI-Export nur mit `DATEN EXPORTIEREN` |
| Local Data Import Manifest Reader | stabil | liest `manifest.json` read-only |
| Local Data Import Dry-Run | stabil | prueft Exportdateien read-only |
| Local Data Import Review CLI | stabil | zeigt Manifest/Dry-Run read-only |
| Local Data Import Apply Preview Model | stabil | erzeugt Apply-Preview ohne Write |
| Local Data Import Apply Preview CLI | stabil | zeigt Apply-Vorschau read-only |

## Finales Runtime-Ergebnis

Der lokale Datenexport-/Import-Review-Block ist runtime-stabil.

Freigegeben ist:

- lokaler Datenexport unter `local_data/exports/`,
- Export nur mit hartem Token `DATEN EXPORTIEREN`,
- Import-Review read-only,
- Manifest Reader read-only,
- Import Dry-Run read-only,
- Apply-Vorschau read-only.

Nicht freigegeben ist:

- echter Import,
- Restore in aktive Friday-Daten,
- In-Place-Restore,
- aktiver SQLite-Write durch Import,
- automatisches Zusammenfuehren,
- Konfliktloesung,
- Abfrage von `IMPORT ANWENDEN`,
- Import von Secrets,
- Import von Obsidian Vaults,
- Import privater Roh-Nachrichten,
- externe Provider,
- Netzwerkaktionen.

## Aktueller CLI-Stand

Im Backup-/Restore-Menue stehen lokal bereit:

- Backup-Vorschau,
- Backup lokal erstellen,
- Restore-Dry-Run,
- Restore-Kopie,
- lokaler Datenexport,
- lokaler Datenimport-Review,
- Import-Apply-Vorschau.

Dabei gilt:

- Backup/Export/Restore-Copy haben harte Tokens.
- Import-Review und Apply-Vorschau bleiben read-only.
- Apply fragt keinen `IMPORT ANWENDEN`-Token ab.

## Teststatus

Aktueller Abschlussstand:

- `python -m pytest friday/tests` -> `642 passed`
- `python -m compileall friday` -> erfolgreich
- `python scripts/friday_safety_smoke.py` -> `Overall: PASS`
- `git diff --check` -> sauber

Relevante Testbereiche:

- `test_local_data_export_preview.py`
- `test_local_data_export_guard.py`
- `test_local_data_export_writer.py`
- `test_local_data_import_manifest_reader.py`
- `test_local_data_import_dry_run.py`
- `test_local_data_import_apply_preview.py`
- `test_interface_main_menu_e2e.py`
- `test_menu.py`

## Safety-Bewertung

- Lokaler Datenexport ist hart gegatet.
- Import bleibt read-only.
- Apply bleibt preview-only.
- Kein aktiver Import-Write.
- Kein In-Place-Restore.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import/Export User Guide Finalization.
