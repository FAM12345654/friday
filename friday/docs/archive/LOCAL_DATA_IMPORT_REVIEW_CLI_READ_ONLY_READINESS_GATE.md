# Local Data Import Review CLI Read-Only Readiness Gate

## Ziel

Dieses Gate prueft den aktuellen Stand des read-only CLI-Pfads fuer lokalen Datenimport-Review.

Der CLI-Pfad ist nur fuer eine sichere Vorschau gedacht:

- Exportordner abfragen,
- Manifest Reader ausfuehren,
- Import Dry-Run ausfuehren,
- Ergebnisse anzeigen,
- nichts importieren,
- nichts wiederherstellen,
- nichts schreiben.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/menu.py` | Backup-/Restore-Menue enthaelt Import-Review-Option |
| `friday/app/interface.py` | read-only Import-Review-Pfad vorhanden |
| `friday/app/local_data_import_manifest_reader.py` | Manifest Reader bleibt read-only |
| `friday/app/local_data_import_dry_run.py` | Import Dry-Run bleibt read-only |
| `friday/tests/test_menu.py` | Menueoptionen abgesichert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Pfad und Ruecksprung abgesichert |
| `friday/tests/test_local_data_import_manifest_reader.py` | Manifest Reader abgesichert |
| `friday/tests/test_local_data_import_dry_run.py` | Dry-Run abgesichert |

## Readiness-Ergebnis

Der read-only CLI-Pfad ist bereit.

Abgesichert ist:

- Menuepunkt `Lokalen Datenimport pruefen` ist vorhanden.
- Ruecksprung erfolgt ueber `Zurueck zum Hauptmenue`.
- Leere Eingabe oder `z` bricht die Import-Pruefung ab.
- Gueltige Exportordner werden read-only geprueft.
- Blockierte Manifest- oder Dry-Run-Faelle zeigen Blockiergruende.
- Es wird nichts importiert.
- Es wird nichts wiederhergestellt.
- Es wird nichts geschrieben.

## Nicht freigegeben

Weiterhin nicht freigegeben sind:

- Import,
- Restore,
- aktiver Datenbank-Write,
- In-Place-Restore,
- Merge aktiver Daten,
- automatische Konfliktloesung,
- Import von Secrets,
- Import von Obsidian Vaults,
- Import von Roh-Nachrichten,
- Cloud-Sync,
- externe Provider.

## Safety-Bewertung

- Keine neue Produktlogik mit externen Aktionen.
- Kein Import implementiert.
- Kein Restore implementiert.
- Kein Datei-Write durch Import-Review.
- Keine Datenbankschema-Aenderung.
- Keine aktive SQLite-Datenbank wird fuer Import geoeffnet.
- Keine Netzwerkaktion.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Teststatus

Relevante Pruefungen:

- `python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_local_data_import_manifest_reader.py friday/tests/test_local_data_import_dry_run.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Import Review Documentation Integration` folgen.

Dieser Schritt sollte nur dokumentieren:

- wie Nutzer den read-only Import-Review im Backup-/Restore-Menue finden,
- dass Import und Restore weiterhin nicht freigegeben sind,
- dass der Pfad nur prueft und nichts schreibt.
