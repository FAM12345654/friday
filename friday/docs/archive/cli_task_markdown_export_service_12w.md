# CLI Task Markdown Export Service 12W

## Ziel

Erster sicherer Implementierungsschritt für lokalen Markdown-Export von Aufgaben, basierend auf Build Step 12V.

## Umfang

- Reine lokale Markdown-Formatierung als Service-Funktion.
- Optionales Schreiben in eine explizit übergebene Datei.
- Keine neue CLI-Menüoption.
- Kein Nutzerpfad im Interface.
- Kein Obsidian-/Cloud-Verhalten.

## Implementierte Funktionen

- `format_tasks_as_markdown(tasks: Iterable[Mapping[str, Any]]) -> str`
  - Gruppiert Aufgaben in:
    - `open`
    - `done`
    - `archived`
  - Setzt fehlende Felder konsistent:
    - Kategorie → `sonstiges`
    - Fälligkeitsdatum → `kein Datum`
    - Priorität → `normal`
  - Sortiert deterministisch nach `id`.
- `write_tasks_markdown(output_path: Path, tasks: Iterable[Mapping[str, Any]]) -> Path`
  - Schreibt den erzeugten Inhalt nach einem expliziten Pfad.
  - Die Funktion nutzt bewusst einen kontrollierten Dateipfad; keine automatische Menü-/Pfad-Auswahl.

## Tests

- `friday/tests/test_task_markdown_export.py`
- Neue fokussierte Tests:
  - Status-Gruppierung (`open`, `done`, `archived`)
  - Standardwerte bei fehlenden Feldern
  - leere Liste
  - Datei-Schreibpfad auf `tmp_path`

## Safety-Bewertung

- Keine externen Aktionen.
- Keine Datenbankschema-Änderung.
- Keine CLI-Menüänderung.
- Keine Nutzerpfad-Eingabe.
- Keine Obsidian-/Cloud-Schreiboperation.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy unverändert:
  - `"ja"` löscht nicht,
  - `"JA"` löscht,
  - `" JA "` bleibt durch `strip()` zulässig.

## Empfehlung für Build Step 12X

Als nächstes: lokalen kontrollierten Exportpfad prüfen (z. B. fester lokaler Standardpfad),
und danach erst entscheiden, ob ein CLI-Export-Menüpunkt sinnvoll und sicher ergänzt wird.
