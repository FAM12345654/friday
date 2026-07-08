# Local Data Import Apply Documentation Integration

## Ziel

Dieser Schritt integriert die lokale Import-Apply-Vorschau in die Nutzer-Dokumentation. Die Dokumentation stellt klar, dass die Vorschau nur informiert und keinen Import ausfuehrt.

## Nutzerpfad

Im Friday-Hauptmenue:

1. `Backup / Restore` oeffnen.
2. `7. Import-Apply-Vorschau anzeigen` waehlen.
3. Exportordner eingeben, z. B. `local_data/exports/friday_data_export_YYYYMMDD_HHMMSS`.

## Was Friday zeigt

- Exportordner.
- Preview-Status.
- Backup-Schutz-Status.
- Geplante Sektionen.
- Blockiergruende.
- Warnungen.

## Was Friday nicht tut

- Kein Import.
- Kein Restore.
- Kein Schreiben in aktive Friday-Dateien.
- Kein Schreiben in die aktive SQLite-Datenbank.
- Kein In-Place-Restore.
- Kein automatisches Zusammenfuehren.
- Kein Abfragen von `IMPORT ANWENDEN`.
- Keine externen Aktionen.
- Keine Provider-, Netzwerk- oder Cloud-Aufrufe.

## Nutzerhinweis

Die Apply-Vorschau ist aktuell absichtlich blockiert, solange kein Backup-Schutz fuer Apply freigegeben ist. Das ist eine Sicherheitsgrenze, kein Fehler.

## Safety-Bewertung

- Der Pfad ist read-only.
- Aktive lokale Daten werden nicht ersetzt.
- Exportordner werden nur gelesen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.
- Externe Integrationen bleiben deaktiviert.

## Geaenderte Dokumentation

- `README_USER.md` erklaert den Menuepunkt `7. Import-Apply-Vorschau anzeigen`.
- `SAFETY_MATRIX.md` markiert die Dokumentationsintegration als abgeschlossen.
- `TEST_MATRIX.md` ordnet die Dokumentation der Apply-Vorschau zu.
- `cli_documentation_index_12l.md` verlinkt dieses Dokument.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Final Acceptance Gate.
