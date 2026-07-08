# CLI Task Markdown Export Wrapper 12Z

## Ziel

Kontrollierter lokaler Wrapper für den Markdown-Export lokaler Aufgaben.

## Implementierter Wrapper

- `export_tasks_markdown_to_default_path(base_dir, tasks, timestamp=None)`
- nutzt `build_default_tasks_export_path`
- nutzt `write_tasks_markdown`
- schreibt nach `local_data/exports/`

## Safety-Grenzen

- Kein CLI-Menüpunkt.
- Kein freier Nutzerpfad.
- Kein Obsidian-/Cloud-Ziel.
- Keine externen Aktionen.
- Keine Datenbankschema-Änderung.
- Delete-Policy unverändert.

## Tests

- Wrapper schreibt unter `local_data/exports/`.
- Wrapper verarbeitet leere Tasks.
- Unterschiedliche Timestamps erzeugen unterschiedliche Dateien.
- Full Regression: `python -m pytest friday/tests`

## Empfehlung für Build Step 13A

Export-Readiness prüfen, bevor ein CLI-Menüpunkt separat geplant/implementiert wird.
