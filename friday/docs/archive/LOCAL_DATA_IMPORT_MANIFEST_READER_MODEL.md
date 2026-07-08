# Local Data Import Manifest Reader Model

## Ziel

Dieser Schritt ergaenzt einen isolierten read-only Manifest Reader fuer lokale Friday-Datenexporte.

Der Reader liest nur `manifest.json`, validiert technische Metadaten und gibt eine sichere Vorschau zurueck.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/local_data_import_manifest_reader.py` | Read-only Manifest Reader |
| `friday/tests/test_local_data_import_manifest_reader.py` | Fokus-Tests fuer gueltige und blockierte Manifest-Faelle |
| `friday/docs/LOCAL_DATA_IMPORT_MANIFEST_READER_MODEL.md` | Dokumentation dieses Bausteins |

## Abgesicherte Verhaltensweisen

- Manifest muss unter `local_data/exports` liegen.
- Fehlendes Manifest blockiert.
- Ungueltiges JSON blockiert.
- Fehlende Pflichtfelder blockieren.
- Falscher Export-Typ blockiert.
- Zielpfad ausserhalb `local_data/exports` blockiert.
- Fehlgeschlagener Safety Smoke blockiert.
- Fehlende Exclude-Dokumentation blockiert.
- Sensible Manifest-Inhalte blockieren.
- Externe Lookups im Manifest blockieren.
- Reader schreibt keine Dateien.
- Reader oeffnet keine aktive SQLite-Datenbank.

## Read-only Ergebnis

Bei gueltigem Manifest liefert der Reader nur eine sichere Zusammenfassung:

- Export-Typ,
- Zielordner,
- Exportbereiche,
- ausgeschlossene Inhalte,
- geschriebene Exportdateien,
- Zaehler,
- Safety-/Preview-Flags.

Es wird nichts importiert, nichts wiederhergestellt und nichts in die aktive Friday-Datenbank geschrieben.

## Safety-Bewertung

- Keine Produktlogik mit externen Aktionen.
- Kein Import.
- Kein Restore.
- Kein Datei-Write.
- Keine Datenbankschema-Aenderung.
- Keine Netzwerkaktion.
- Keine Provider.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Import Manifest Reader Readiness Gate` folgen.

Dieser Schritt sollte pruefen und dokumentieren:

- Reader ist read-only,
- Reader ist scanner-clean,
- Reader ist kompatibel mit dem aktuellen Export Writer,
- Import/Restore bleiben nicht freigegeben.
