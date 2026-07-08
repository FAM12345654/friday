# Local Data Export Writer Readiness Gate

## Ziel

Dieses Gate prueft und dokumentiert den aktuellen Stand des lokalen Datenexport-Writers.

Der Writer ist fuer isolierte lokale Nutzung freigegeben, bleibt aber noch ohne CLI-Anbindung.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/local_data_export_preview.py` | Preview-Modell vorhanden |
| `friday/app/local_data_export_guard.py` | Guard-Modell vorhanden |
| `friday/app/local_data_export_writer.py` | Writer-Modell vorhanden |
| `friday/tests/test_local_data_export_preview.py` | Preview-Tests vorhanden |
| `friday/tests/test_local_data_export_guard.py` | Guard-Tests vorhanden |
| `friday/tests/test_local_data_export_writer.py` | Writer-Tests vorhanden |
| `friday/docs/LOCAL_DATA_EXPORT_WRITER_MODEL.md` | Writer-Dokumentation vorhanden |

## Readiness-Ergebnis

- Writer nutzt den Guard vor Dateioperationen.
- Writer schreibt nur bei exaktem Token `DATEN EXPORTIEREN`.
- Writer schreibt nur unter `local_data/exports`.
- Writer liest keine Datenbank.
- Writer liest keine Repositories.
- Writer nutzt keine externen Aktionen.
- Writer hat keine CLI-Anbindung.
- Writer erzeugt kein ZIP.
- Writer ueberschreibt keinen vorhandenen Zielordner.
- Writer filtert Kontakt-Kontexte auf erlaubte Felder.
- Writer filtert Review-Vorschlaege ohne rohe private Nachrichtentexte.
- Writer schreibt Manifest, Task JSON, Task Markdown, Kontakt-Summary, Review-Summary, Safety-Status und Exportnotizen.

## Abgesicherte Tests

| Testdatei | Ergebnis |
|---|---|
| `friday/tests/test_local_data_export_writer.py` | Writer-Verhalten, Blockierpfade, Manifest, Filterung und Safe-Flags |
| `friday/tests/test_local_data_export_guard.py` | Guard-Pflicht fuer Zielpfad, Token, Safety Smoke und Excludes |
| `friday/tests/test_local_data_export_preview.py` | Preview-Quelle fuer Zielpfad, Sections, Ausschluesse und Token |

## Nicht freigegeben

Noch nicht freigegeben sind:

- Export-Menue im CLI,
- automatische DB-/Repository-Sammlung,
- ZIP-Erstellung,
- Cloud-Export,
- Obsidian Export,
- externe Provider,
- echter Nachrichtenversand,
- echte Kalenderaktionen,
- Restore aus Exportdaten.

## Safety-Bewertung

- Keine Netzwerkaktion.
- Keine externen Aktionen.
- Keine Datenbankabfrage im Writer.
- Keine Datenbankschema-Aenderung.
- Keine Safety-Flag-Aenderung.
- Delete-Policy unveraendert.
- Guard-Pflicht vor Dateioperation.
- Safety Smoke PASS.

## Validierung

Empfohlene Validierung fuer dieses Gate:

- `python -m pytest friday/tests/test_local_data_export_preview.py friday/tests/test_local_data_export_guard.py friday/tests/test_local_data_export_writer.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export CLI Plan` folgen.

Dieser Plan sollte festlegen:

- wo ein Export-Menue spaeter sichtbar wird,
- wie Preview, Guard und Writer im CLI getrennt bleiben,
- welcher harte Token abgefragt wird,
- wie Safety Smoke PASS vor Export sichergestellt wird,
- wie Nutzer vor sensiblen Daten gewarnt werden,
- dass die CLI-Anbindung erst nach eigenem Gate gebaut wird.
