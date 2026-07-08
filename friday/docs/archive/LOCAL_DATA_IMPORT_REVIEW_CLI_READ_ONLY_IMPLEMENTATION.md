# Local Data Import Review CLI Read-Only Implementation

## Ziel

Dieser Schritt ergaenzt einen read-only CLI-Pfad fuer die lokale Datenimport-Pruefung.

Der CLI-Pfad zeigt nur Manifest Reader und Import Dry-Run an.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/menu.py` | Backup-/Restore-Menue um Import-Review erweitert |
| `friday/app/interface.py` | read-only Import-Review-Pfad im CLI |
| `friday/tests/test_menu.py` | Menueoptionen aktualisiert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-E2E-Tests fuer Import-Review |

## Abgesicherte Verhaltensweisen

- Backup-/Restore-Menue zeigt `Lokalen Datenimport pruefen`.
- CLI fragt nach einem Exportordner.
- Leere Eingabe oder `z` kehrt zurueck.
- Gueltiger Export wird read-only geprueft.
- Manifest Reader und Import Dry-Run werden genutzt.
- Blockierte Pfade zeigen Blockiergruende.
- Es wird nichts importiert.
- Es wird nichts wiederhergestellt.
- Es wird nichts geschrieben.

## Nicht freigegeben

Weiterhin nicht freigegeben sind:

- Import,
- Restore,
- aktiver DB-Write,
- In-Place-Restore,
- Merge aktiver Daten,
- Cloud-Sync,
- externe Provider.

## Safety-Bewertung

- Keine externen Aktionen.
- Kein Import.
- Kein Restore.
- Kein Datei-Write durch den Import-Review-Pfad.
- Keine Datenbankschema-Aenderung.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Import Review CLI Read-Only Readiness Gate` folgen.

Dieser Schritt sollte pruefen und dokumentieren:

- CLI-Pfad ist read-only,
- Scanner bleiben PASS,
- Menue- und Ruecksprungpfade sind stabil,
- Import/Restore bleiben nicht freigegeben.
