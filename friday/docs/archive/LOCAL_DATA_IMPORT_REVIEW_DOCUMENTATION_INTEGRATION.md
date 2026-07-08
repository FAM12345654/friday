# Local Data Import Review Documentation Integration

## Ziel

Dieser Schritt integriert den lokalen Import-Review in die Nutzer-Dokumentation. Der Import-Review bleibt read-only und dient nur dazu, einen lokalen Exportordner vor einem moeglichen spaeteren Import zu pruefen.

## Nutzerpfad

Im Friday-Hauptmenue:

1. `Backup / Restore` oeffnen.
2. `6. Lokalen Datenimport pruefen` waehlen.
3. Exportordner eingeben, z. B. `local_data/exports/friday_data_export_YYYYMMDD_HHMMSS`.

## Was Friday prueft

- `manifest.json` im Exportordner.
- Exportformat und Manifest-Felder.
- Erwartete lokale Exportdateien.
- Read-only Import-Dry-Run.
- Blockiergruende wie fehlende Dateien, ungueltige JSON-Dateien, externe Flags oder sensible Felder.

## Was Friday nicht tut

- Kein Import.
- Kein Restore.
- Kein Schreiben in aktive Friday-Dateien.
- Kein Schreiben in die aktive SQLite-Datenbank.
- Kein In-Place-Restore.
- Keine externen Aktionen.
- Keine Provider-, Netzwerk- oder Cloud-Aufrufe.

## Safety-Bewertung

- Der Pfad ist read-only.
- Manifest Reader und Import Dry-Run bleiben getrennt vom echten Import.
- Aktive lokale Daten werden nicht ersetzt.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.
- Externe Integrationen bleiben deaktiviert.

## Geaenderte Dokumentation

- `README_USER.md` erklaert den Menuepunkt `6. Lokalen Datenimport pruefen`.
- `SAFETY_MATRIX.md` markiert die Dokumentationsintegration als abgeschlossen.
- `TEST_MATRIX.md` ordnet die Dokumentation dem read-only Import-Review zu.
- `cli_documentation_index_12l.md` verlinkt dieses Dokument.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Review Final Acceptance Gate.
