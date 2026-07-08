# Local Data Import Manifest Reader Readiness Gate

## Ziel

Dieses Gate prueft den aktuellen Stand des lokalen Import-Manifest-Readers.

Der Reader ist nur fuer eine sichere Vorschau gedacht:

- Manifest lesen,
- technische Metadaten pruefen,
- blockierende Fehler melden,
- nichts importieren,
- nichts wiederherstellen,
- nichts schreiben.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/local_data_import_manifest_reader.py` | read-only Manifest Reader vorhanden |
| `friday/tests/test_local_data_import_manifest_reader.py` | Fokus-Tests fuer gueltige und blockierte Manifest-Faelle vorhanden |
| `friday/app/local_data_export_writer.py` | aktuelles Export-Manifest bleibt kompatibel |
| `friday/docs/LOCAL_DATA_IMPORT_MANIFEST_READER_MODEL.md` | Modell-Doku vorhanden |

## Readiness-Ergebnis

Der Manifest Reader ist bereit fuer den naechsten Planungsbaustein.

Abgesichert ist:

- Manifest muss unter `local_data/exports` liegen.
- Fehlendes Manifest blockiert.
- Ungueltiges JSON blockiert.
- Falscher Export-Typ blockiert.
- Zielpfad ausserhalb `local_data/exports` blockiert.
- Fehlgeschlagener Safety Smoke im Manifest blockiert.
- Fehlende Ausschlussliste blockiert.
- Sensible Manifest-Inhalte blockieren.
- Externe Lookups im Manifest blockieren.
- Gueltige Manifeste aus dem aktuellen Export Writer werden akzeptiert.

## Nicht freigegeben

Weiterhin nicht freigegeben sind:

- Import,
- Restore,
- aktiver Datenbank-Write,
- In-Place-Restore,
- Merge aktiver Daten,
- CLI-Import,
- Cloud-Sync,
- externe Provider,
- automatische Verarbeitung ohne Review.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Kein Import implementiert.
- Kein Restore implementiert.
- Kein Datei-Write durch den Reader.
- Keine Datenbankschema-Aenderung.
- Keine externe Aktion.
- Keine Netzwerkaktion.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Teststatus

Relevante Pruefungen:

- `python -m pytest friday/tests/test_local_data_import_manifest_reader.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Import Dry-Run Plan` folgen.

Dieser Schritt sollte nur planen:

- wie ein spaeterer Import-Dry-Run das gelesene Manifest nutzt,
- welche Exportdateien read-only geprueft werden duerfen,
- wie Konflikte dargestellt werden,
- dass weiterhin nichts geschrieben oder importiert wird.
