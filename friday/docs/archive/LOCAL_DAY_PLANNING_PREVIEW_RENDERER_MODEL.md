# Local Day Planning Preview Renderer Model

## Ziel

Dieses Dokument beschreibt den lokalen Renderer fuer die Tagesplan-Vorschau.

Der Renderer macht aus einem `DayPlanPreview` einen deutschen Text-String.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/day_planning_renderer.py` | Reiner String-Renderer fuer lokale Tagesplanung |
| `friday/tests/test_day_planning_renderer.py` | Tests fuer Ausgabe, Leerzustand, Safety und Nicht-Mutation |

## Funktion

```python
render_day_plan_preview(preview: DayPlanPreview) -> str
```

Die Funktion:

- gibt nur einen String zurueck,
- nutzt kein `print()`,
- nutzt kein `input()`,
- liest nicht aus SQLite,
- schreibt nichts,
- veraendert keine Aufgaben,
- ruft keine externen Dienste auf.

## Ausgabe

Beispiel mit Aufgaben:

```text
Lokale Tagesplanung fuer 2026-07-08

Empfohlene Aufgaben:
1. Rechnung pruefen
   Faellig: 2026-07-08
   Prioritaet: high
   Grund: heute faellig

Empfohlen: 2 von 2 lokalen Aufgaben.
Hinweis: Diese Ansicht ist nur eine lokale Vorschau. Es wurde nichts geaendert.
```

Beispiel ohne Aufgaben:

```text
Lokale Tagesplanung fuer 2026-07-08

Keine offenen Aufgaben fuer die Tagesplanung gefunden.

Hinweis: Diese Ansicht ist nur eine lokale Vorschau. Es wurde nichts geaendert.
```

## Tests

Abgedeckt sind:

- freundlicher Leerzustand,
- Ausgabe mit Aufgaben,
- Faelligkeitsanzeige,
- Aufgaben ohne Faelligkeitsdatum,
- Safety-Hinweis,
- keine Mutation der Preview,
- Safety-Flags.

## Nicht-Ziele

- Keine CLI-Anbindung.
- Kein neuer Hauptmenuepunkt.
- Keine TaskAgent-Anbindung.
- Keine SQLite-Verbindung.
- Keine Persistenz.
- Keine automatische Planung.
- Keine Kalenderintegration.
- Keine KI-/Provider-Nutzung.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine Schreiboperationen.
- Safety-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Local Day Planning Preview Renderer Readiness Gate**.

Ziel:

- Renderer final pruefen,
- Safety-Grenzen dokumentieren,
- Doku-Index aktualisieren,
- keine CLI-Anbindung.
