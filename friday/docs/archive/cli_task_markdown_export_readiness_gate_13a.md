# CLI Task Markdown Export Readiness Gate 13A

## Ziel

Finale Readiness-Prüfung für den lokalen Markdown-Export vor einem möglichen CLI-Menüpunkt.

## Geprüfte Bausteine

| Baustein | Status | Hinweis |
|---|---|---|
| Markdown-Formatierung | vorhanden | `format_tasks_as_markdown` |
| Write-Helper | vorhanden | `write_tasks_markdown` |
| Safe-Path-Helper | vorhanden | `build_default_tasks_export_path` |
| Export-Wrapper | vorhanden | `export_tasks_markdown_to_default_path` |
| tmp_path Tests | vorhanden | `test_task_markdown_export.py` |
| CLI-Menüpunkt | nicht vorhanden | bewusst noch nicht freigegeben |
| Nutzerpfad | nicht vorhanden | bewusst nicht erlaubt |
| Obsidian-/Cloud-Ziel | nicht vorhanden | bewusst nicht erlaubt |

## Teststatus

- `python -m pytest friday/tests/test_task_markdown_export.py` → `10 passed`
- `python -m pytest friday/tests` → `246 passed`
- `python -m compileall friday` → erfolgreich
- `git diff --check` → sauber

## Safety-Ergebnis

- Export bleibt lokal.
- Export nutzt `local_data/exports/`.
- Zeitstempel-Dateiname verhindert Standard-Überschreiben.
- Keine freien Nutzerpfade.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Änderung.
- Safety-Flags bleiben unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` bleibt durch `strip()` zugelassen

## Entscheidung

Der Export-Unterbau ist technisch bereit für die Planung eines späteren CLI-Menüpunkts.

Noch nicht freigegeben in 13A:
- kein Menüpunkt
- keine README-Claims für einen Produkt-Feature-Menüpunkt
- kein freier Pfad
- kein Obsidian-/Cloud-Schreiben

## Empfehlung für Build Step 13B

CLI Export Menu Planning:

- UX für Aufgabenmenüpunkt planen,
- Erfolg-/Fehlertexte definieren,
- Testplan festlegen,
- Safety-Grenzen bestätigen,
- noch keine Implementierung.
