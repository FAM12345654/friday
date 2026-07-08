# Local Data Import/Export Smoke Guide

## Ziel

Dieser Smoke Guide beschreibt die empfohlenen Pruefbefehle nach Aenderungen am lokalen Datenexport-/Import-Runtime-Bereich.

Er gilt fuer:

- lokalen Datenexport,
- Import-Manifest-Review,
- Import-Dry-Run,
- Import-Apply-Vorschau,
- guarded Import-Apply-Schreibpfad,
- Backup-/Restore-Menuepunkte `5` bis `9`.

## Wann ausfuehren?

Fuehre diesen Smoke Guide aus, wenn geaendert wurde:

- `friday/app/local_data_export_*`,
- `friday/app/local_data_import_*`,
- `friday/app/interface.py` im Backup-/Restore-Menue,
- `friday/app/menu.py` im Backup-/Restore-Menue,
- Import-/Export-Dokumentation,
- Safety-Scanner oder Approval-Token-Regeln.

## Fokus-Tests

```powershell
python -m pytest friday/tests/test_local_data_export_preview.py friday/tests/test_local_data_export_guard.py friday/tests/test_local_data_export_writer.py
```

```powershell
python -m pytest friday/tests/test_local_data_import_manifest_reader.py friday/tests/test_local_data_import_dry_run.py
```

```powershell
python -m pytest friday/tests/test_local_data_import_apply_preview.py friday/tests/test_local_data_import_apply_write_guard.py friday/tests/test_local_data_import_apply_writer.py
```

```powershell
python -m pytest friday/tests/test_interface_main_menu_e2e.py friday/tests/test_menu.py
```

## Vollstaendige Regression

```powershell
python -m pytest friday/tests
```

## Compilecheck

```powershell
python -m compileall friday
```

## Safety Smoke

```powershell
python scripts/friday_safety_smoke.py
```

Erwartung:

```text
Overall: PASS
```

## Diff-/Whitespace-Check

```powershell
git diff --check
```

Erwartung:

- keine Ausgabe,
- Exit-Code `0`.

## Erwartete Safety-Grenzen

- Export nur lokal unter `local_data/exports/`.
- Export nur mit exakt `DATEN EXPORTIEREN`.
- Import-Review bleibt read-only.
- Import-Apply-Vorschau bleibt read-only.
- Import-Apply schreibt nur nach:
  - Backup-Schutz,
  - Safety Smoke PASS,
  - Guard-Freigabe,
  - exakt `IMPORT ANWENDEN`.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.

## Aktueller akzeptierter Referenzstand

- `python -m pytest friday/tests` -> `677 passed`
- `python -m compileall friday` -> erfolgreich
- `python scripts/friday_safety_smoke.py` -> `Overall: PASS`
- `git diff --check` -> sauber

## Empfehlung fuer naechsten Build Step

Local Data Import/Export Final Bundle Gate: den Export-/Import-/Apply-Block als abgeschlossenes Bundle in der Doku markieren und den naechsten Produktbereich planen.
