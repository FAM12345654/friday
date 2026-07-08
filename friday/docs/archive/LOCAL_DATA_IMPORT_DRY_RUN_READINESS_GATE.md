# Local Data Import Dry-Run Readiness Gate

## Ziel

Dieses Gate prueft den aktuellen Stand des lokalen Import-Dry-Runs.

Der Dry-Run ist nur fuer eine sichere Vorschau gedacht:

- Exportordner pruefen,
- Manifest-Reader-Ergebnis nutzen,
- erwartete Exportdateien read-only pruefen,
- blockierende Fehler melden,
- nichts importieren,
- nichts wiederherstellen,
- nichts schreiben.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/local_data_import_manifest_reader.py` | read-only Manifest Reader vorhanden |
| `friday/app/local_data_import_dry_run.py` | read-only Import-Dry-Run vorhanden |
| `friday/tests/test_local_data_import_manifest_reader.py` | Manifest-Fokus-Tests vorhanden |
| `friday/tests/test_local_data_import_dry_run.py` | Dry-Run-Fokus-Tests vorhanden |
| `friday/app/local_data_export_writer.py` | Export Writer bleibt kompatibel |
| `friday/docs/LOCAL_DATA_IMPORT_DRY_RUN_MODEL.md` | Modell-Doku vorhanden |

## Readiness-Ergebnis

Der Import-Dry-Run ist bereit fuer die naechste Planungsphase.

Abgesichert ist:

- Dry-Run blockiert, wenn der Manifest Reader blockiert.
- Exportordner muss unter `local_data/exports` liegen.
- Fehlende erwartete Exportdateien blockieren.
- Ungueltige JSON-Dateien blockieren.
- Sensible Kontaktfelder blockieren.
- Rohe private Review-/Nachrichtentexte blockieren.
- Aktivierte externe Safety-Flags blockieren.
- `external_lookup_used=True` blockiert.
- Gueltige Exportordner werden read-only geprueft.
- Gueltige Manifeste aus dem aktuellen Export Writer bleiben kompatibel.

## Nicht freigegeben

Weiterhin nicht freigegeben sind:

- Import,
- Restore,
- aktiver Datenbank-Write,
- In-Place-Restore,
- Merge aktiver Daten,
- CLI-Import,
- automatischer Datenabgleich,
- Cloud-Sync,
- externe Provider,
- automatische Verarbeitung ohne Review.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Kein Import implementiert.
- Kein Restore implementiert.
- Kein Datei-Write durch den Dry-Run.
- Keine Datenbankschema-Aenderung.
- Keine aktive SQLite-Datenbank wird geoeffnet.
- Keine externe Aktion.
- Keine Netzwerkaktion.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Teststatus

Relevante Pruefungen:

- `python -m pytest friday/tests/test_local_data_import_manifest_reader.py friday/tests/test_local_data_import_dry_run.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Import Review CLI Read-Only Plan` folgen.

Dieser Schritt sollte nur planen:

- wie ein spaeterer CLI-Menuepunkt den Manifest Reader und Dry-Run read-only anzeigen darf,
- welche Ruecksprung- und Fehlermeldungen sinnvoll sind,
- dass weiterhin kein Import, Restore oder Write freigegeben wird.
