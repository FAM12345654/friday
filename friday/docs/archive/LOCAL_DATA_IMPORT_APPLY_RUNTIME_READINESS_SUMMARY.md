# Local Data Import Apply Runtime Readiness Summary

## Ziel

Dieses Dokument fasst den aktuellen lokalen Runtime-Stand fuer die Import-Apply-Vorschau zusammen. Der aktuelle Stand ist bewusst preview-only: Friday zeigt eine Apply-Vorschau, fuehrt aber keinen Import aus.

## Lokal stabil abgesicherte Bereiche

| Bereich | Status | Absicherung |
|---|---|---|
| Manifest Reader | stabil | read-only Manifest-Pruefung |
| Import Dry-Run | stabil | read-only Exportdatei-Pruefung |
| Apply Preview Model | stabil | Status, Sektionen, Warnungen und Blockiergruende |
| Apply Preview CLI | stabil | Backup-/Restore-Menuepunkt `7. Import-Apply-Vorschau anzeigen` |
| Ruecksprung | stabil | `8. Zurueck zum Hauptmenue` |
| Safety Scanner | stabil | Safety Smoke PASS |

## Runtime-Verhalten

Friday kann aktuell:

- lokalen Exportordner fuer Apply-Vorschau abfragen,
- `manifest.json` read-only lesen,
- Import Dry-Run read-only ausfuehren,
- Apply-Preview-Modell bauen,
- Status anzeigen,
- geplante Sektionen anzeigen,
- Warnungen anzeigen,
- Blockiergruende anzeigen.

Friday kann aktuell nicht:

- Import anwenden,
- Restore ausfuehren,
- aktive Friday-Daten ersetzen,
- aktive SQLite-Daten schreiben,
- Dateien durch Apply Preview schreiben,
- Konflikte automatisch loesen,
- Import-Token abfragen,
- externe Provider oder Netzwerkaktionen starten.

## Aktueller Sicherheitszustand

Die Apply-Vorschau bleibt aktuell blockiert, wenn kein Backup-Schutz bereit ist.

Das ist beabsichtigt:

- Apply ohne Backup-Schutz ist nicht freigegeben.
- `IMPORT ANWENDEN` wird im CLI noch nicht abgefragt.
- Der CLI-Pfad zeigt nur den Status und die Blockiergruende.

## Teststatus

Aktueller Abschlussstand:

- `python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_local_data_import_apply_preview.py friday/tests/test_local_data_import_dry_run.py friday/tests/test_local_data_import_manifest_reader.py` -> `105 passed`
- `python -m pytest friday/tests` -> `642 passed`
- `python -m compileall friday` -> erfolgreich
- `python scripts/friday_safety_smoke.py` -> `Overall: PASS`
- `git diff --check` -> sauber

## Safety-Bewertung

- Kein Import.
- Kein Restore.
- Kein Datei-Write durch Apply Preview.
- Kein aktiver SQLite-Write.
- Kein `IMPORT ANWENDEN`-Token im CLI.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Verweise

- `LOCAL_DATA_IMPORT_APPLY_POLICY_PLAN.md`
- `LOCAL_DATA_IMPORT_APPLY_PREVIEW_PLAN.md`
- `LOCAL_DATA_IMPORT_APPLY_PREVIEW_MODEL.md`
- `LOCAL_DATA_IMPORT_APPLY_PREVIEW_READINESS_GATE.md`
- `LOCAL_DATA_IMPORT_APPLY_CLI_PLAN.md`
- `LOCAL_DATA_IMPORT_APPLY_CLI_PREVIEW_IMPLEMENTATION.md`
- `LOCAL_DATA_IMPORT_APPLY_CLI_PREVIEW_READINESS_GATE.md`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Documentation Integration.
