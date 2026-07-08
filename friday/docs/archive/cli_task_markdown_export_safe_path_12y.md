# CLI Task Markdown Export Safe Path 12Y

## Ziel

Kontrollierter, lokaler Standardpfad für den Markdown-Task-Export.

## Implementierter Helper

- `build_default_tasks_export_path(base_dir, timestamp=None)`
  - Erzeugt einen Pfad ausschließlich unter:
    - `local_data/exports/`
  - Dateiname im Format:
    - `friday_tasks_YYYYMMDD_HHMMSS.md`

## Safety-Grenzen

- Kein freier Nutzerpfad.
- Kein CLI-Menüpunkt.
- Kein Obsidian-/Cloud-Ziel.
- Keine externen Aktionen.
- Keine Datenbankschema-Änderung.
- Parent-Ordner wird nur kontrolliert über `write_tasks_markdown` erzeugt.

## Testabdeckung

- Lokaler Exportpfad ist kontrolliert:
  - `tmp_path / local_data / exports / friday_tasks_YYYYMMDD_HHMMSS.md`
- Helper nutzt zeitpunktbasierte, deterministische Benennung bei festen Zeitstempeln.
- Schreiben mit `write_tasks_markdown` funktioniert auf dem erzeugten Safe-Path.

## Sicherheitshinweis

- `Safety-Flags` bleiben unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht,
  - `"JA"` löscht,
  - `" JA "` bleibt durch `strip()` zulässig.

## Empfehlung für Build Step 12Z

Als nächster Schritt kann ein kleiner Export-Wrapper ergänzt werden, der:

- Aufgaben als Liste annimmt,
- `build_default_tasks_export_path` nutzt,
- `write_tasks_markdown` nutzt,
- weiterhin ohne CLI-Menüpunkt und ohne Nutzerpfad arbeitet.
