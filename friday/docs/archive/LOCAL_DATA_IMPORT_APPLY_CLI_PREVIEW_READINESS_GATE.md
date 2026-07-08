# Local Data Import Apply CLI Preview Readiness Gate

## Ziel

Dieses Gate prueft die read-only CLI-Anbindung der lokalen Import-Apply-Vorschau. Es bestaetigt, dass die CLI nur eine Vorschau zeigt und keinen Import ausfuehrt.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/menu.py` | Backup-/Restore-Menue enthaelt Apply-Preview-Option |
| `friday/app/interface.py` | read-only Apply-Preview-Anzeige vorhanden |
| `friday/app/local_data_import_apply_preview.py` | isoliertes Preview-Modell wird genutzt |
| `friday/tests/test_menu.py` | Menueoptionen abgesichert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Pfad und Ruecksprung abgesichert |

## Readiness-Ergebnis

Die CLI-Apply-Vorschau ist bereit.

Abgesichert ist:

- Backup-/Restore-Menue zeigt `7. Import-Apply-Vorschau anzeigen`.
- Rueckkehr erfolgt ueber `8. Zurueck zum Hauptmenue`.
- Exportordner kann eingegeben werden.
- Manifest Reader laeuft read-only.
- Import Dry-Run laeuft read-only.
- Apply-Preview-Modell erzeugt Status, Sektionen und Blockiergruende.
- Ohne Backup-Schutz bleibt Apply blockiert.
- `z` kehrt zurueck, ohne Preview zu erzeugen.
- Es wird kein `IMPORT ANWENDEN`-Token abgefragt.

## Nicht freigegeben

Weiterhin nicht freigegeben sind:

- echter Import,
- Restore in aktive Friday-Daten,
- In-Place-Restore,
- aktiver SQLite-Write,
- Datei-Write durch Apply Preview,
- Konfliktloesung,
- automatisches Zusammenfuehren,
- externe Provider,
- Netzwerkaktionen.

## Safety-Bewertung

- CLI-Pfad ist read-only.
- Kein Import.
- Kein Restore.
- Kein Datei-Write.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Teststatus

Relevante Pruefungen:

- `python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_local_data_import_apply_preview.py friday/tests/test_local_data_import_dry_run.py friday/tests/test_local_data_import_manifest_reader.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Runtime Readiness Summary.
