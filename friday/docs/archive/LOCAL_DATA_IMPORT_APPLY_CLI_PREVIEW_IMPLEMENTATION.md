# Local Data Import Apply CLI Preview Implementation

## Ziel

Dieser Schritt bindet die lokale Import-Apply-Vorschau read-only in das Backup-/Restore-Menue ein. Die CLI zeigt nur die Vorschau und aktiviert keinen echten Import.

## Geaenderte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/menu.py` | Backup-/Restore-Menue um Preview-Option erweitert |
| `friday/app/interface.py` | read-only Apply-Preview-Anzeige ergaenzt |
| `friday/tests/test_menu.py` | Menueoptionen aktualisiert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Preview-Pfad und Ruecksprung abgesichert |

## CLI-Pfad

Im Backup-/Restore-Menue:

```text
7. Import-Apply-Vorschau anzeigen
8. Zurueck zum Hauptmenue
```

Die Vorschau fragt nach einem lokalen Exportordner und nutzt:

- Manifest Reader,
- Import Dry-Run,
- Apply-Preview-Modell.

## Verhalten

Die CLI zeigt:

- Exportordner,
- Preview-Status,
- Backup-Schutz-Status,
- geplante Sektionen,
- Blockiergruende,
- Warnungen.

Da noch kein Backup-Schutz fuer Apply freigegeben ist, bleibt die Apply-Vorschau aktuell blockiert und zeigt `backup_required`.

## Nicht freigegeben

- Kein Import.
- Kein Restore.
- Kein Datei-Write.
- Kein aktiver SQLite-Write.
- Kein `IMPORT ANWENDEN`-Token wird abgefragt.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.

## Safety-Bewertung

- Der CLI-Pfad ist read-only.
- Aktive Friday-Daten werden nicht veraendert.
- Exportordner werden nur gelesen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Tests

Abgesichert ist:

- Menue zeigt die neue Apply-Preview-Option.
- Gueltiger Exportordner zeigt die read-only Vorschau.
- Ohne Backup-Schutz bleibt die Vorschau blockiert.
- `z` kehrt ohne Token und ohne Preview-Erstellung zurueck.
- Es wird nichts geschrieben.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply CLI Preview Readiness Gate.
