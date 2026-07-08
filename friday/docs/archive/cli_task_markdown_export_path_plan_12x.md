# CLI Task Markdown Export Path Plan 12X

## Ziel

Nach Build Step 12W soll der nächste lokale Export-Fortschritt sicher geplant werden, ohne neue Produktlogik zu ändern:

- fester, kontrollierter Exportpfad,
- klarer Umgang mit bestehenden Dateien,
- sichere Dateisystem-Grenzen,
- keine Nutzerpfad-Eingabe, kein Menüzugang in diesem Schritt.

## Ausgangslage

- Der Markdown-Export-Service ist in 12W implementiert:
  - `format_tasks_as_markdown(tasks)`
  - `write_tasks_markdown(output_path, tasks)`
- Es wurde absichtlich noch kein CLI-Menüpunkt gebaut.
- Kein freier Pfad aus der Benutzereingabe.
- Tests für den Service sind grün.

## Bewertete Pfadoptionen

| Option | Nutzen | Risiko | Empfehlung |
|---|---|---|---|
| A. Fester Standardpfad: `local_data/exports/friday_tasks.md` | Sehr einfacher Zugriff, gut dokumentierbar | Risiko: Überschreiben | Für ersten echten Export akzeptabel, wenn Überschreibverhalten explizit festgelegt wird |
| B. Zeitstempel-Dateiname unter `local_data/exports/` | Kein Überschreiben, einfacher sicherer Betrieb | Risiko: viele Dateien | Für späteren Export Schritt stark empfohlen |
| C. Fester Pfad + `.bak`-Backup | Datenverlust wird reduziert | Mehr Logik, mehr Pfadeffekte | Später sinnvoll, wenn Dateiverwaltung nötig wird |
| D. Nutzerdefinierter Pfad | Hohe Flexibilität, hoher Komfort | Erhöhte Risikooberfläche (Pfadfehler, falsche Orte) | Nicht für den nächsten Schritt |
| E. Obsidian-/Cloud-Pfade | Potentieller Komfort im Workflow | Externe Zielorte, zusätzliche Integrationsrisiken | Nicht in den nächsten Schritten |

## Empfohlene Export-Path-Policy für nächsten sicheren Schritt

- Export nur über festen lokalen Ordner:
  - `local_data/exports/`
- Kein Nutzerpfad in der ersten Umsetzungsphase.
- Kein Cloud- oder Obsidian-Ziel.
- Standard-Dateiname in Phase 12Y: mit Zeitstempel (z. B. `friday_tasks_YYYYMMDD_HHMMSS.md`) empfohlen, um Überschreiben zu vermeiden.
- Parent-Ordner darf kontrolliert erzeugt werden.
- Keine automatischen externen Side-Effects.

## Safe-Dateisystem-Grenzen

- Kein Zugriff auf beliebige Nutzerpfade.
- Kein Schreibzugriff außerhalb des Projektverzeichnisses.
- Keine automatische Umleitung auf geteilte/Cloud-Verzeichnisse.
- Keine Pfad-Sanitizer-Auflösung aus Nutzereingabe.

## Vorschlag für spätere Tests

Für den nächsten Implementierungsschritt (ohne CLI-Menüpunkt) sollte geprüft werden:

- Export erzeugt Datei **nur** unter `local_data/exports/`.
- Dateiname folgt der festgelegten lokalen Standard-Policy.
- Bestehende Dateien werden nicht unbeabsichtigt überschrieben (oder Überschreibverhalten ist dokumentiert).
- Exportinhalt enthält `offen`, `erledigt`, `archiviert` korrekt.
- Keine externen Aktionen oder externen Ziele.

## Safety-Bewertung

- 12X bleibt ein Planungsschritt ohne Produktlogikänderung.
- Keine neue Testerweiterung in diesem Schritt.
- Keine CLI-Menüoption.
- Keine Cloud-/Netzwerk-/Obsidian-Schreiboperation.
- `Safety-Flags` bleiben unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy unverändert:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` bleibt durch `strip()` zulässig

## Empfehlung für Build Step 12Y

Empfohlen: **Safe Path Helper** für kontrollierten lokalen Export unter `local_data/exports/` implementieren, mit Zeitstempel-Dateinamen als Standard.
