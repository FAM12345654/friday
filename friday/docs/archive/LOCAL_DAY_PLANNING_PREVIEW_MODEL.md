# Local Day Planning Preview Model

## Ziel

Dieses Dokument beschreibt das isolierte read-only Tagesplan-Preview-Modell fuer Friday.

Der Baustein erstellt aus vorhandenen lokalen Aufgaben eine sortierte Tagesplan-Vorschau, ohne Aufgaben zu veraendern.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/day_planning_preview.py` | Isoliertes Preview-Modell fuer lokale Tagesplanung |
| `friday/tests/test_day_planning_preview.py` | Unit-Tests fuer Sortierung, Ausschlussregeln und Safety |

## Modell

Das Modell nutzt zwei frozen Dataclasses:

| Dataclass | Zweck |
|---|---|
| `DayPlanItem` | Eine empfohlene Aufgabe in der Tagesplan-Vorschau |
| `DayPlanPreview` | Gesamter read-only Preview-Status |

Die zentrale Funktion ist:

```python
build_day_plan_preview(tasks, today, limit=None)
```

## Sortierlogik

Die erste Version sortiert deterministisch:

1. ueberfaellige und heute faellige Aufgaben zuerst,
2. spaetere Aufgaben danach,
3. Aufgaben ohne Faelligkeitsdatum zuletzt,
4. innerhalb desselben Datums nach Prioritaet:
   - `urgent`,
   - `high`,
   - `normal` / `medium`,
   - `low`,
5. Titel als stabiler Tie-Breaker.

## Ausschlussregeln

Nicht empfohlen werden:

- Aufgaben ohne Titel,
- Aufgaben mit Status `done`,
- Aufgaben mit Status `archived`.

## Read-only-Grenzen

- Keine SQLite-Verbindung.
- Keine Repository-Nutzung.
- Keine CLI-Anbindung.
- Keine Persistenz.
- Kein `input()`.
- Kein `print()`.
- Keine externen Aktionen.
- Keine Kalenderintegration.
- Keine KI-/Provider-Nutzung.

## Tests

Abgedeckt sind:

- leere Aufgabenliste,
- Ausschluss von erledigten und archivierten Aufgaben,
- Sortierung nach Faelligkeit,
- Sortierung nach Prioritaet,
- stabiler Titel-Tie-Breaker,
- unbekannte Prioritaeten,
- Limitierung ohne Schreibeffekt,
- Safety-Flags.

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

Naechster sinnvoller Build Step: **Local Day Planning Preview Readiness Gate**.

Ziel:

- Preview-Modell final pruefen,
- Safety-Grenzen dokumentieren,
- Doku-Index aktualisieren,
- keine CLI-Anbindung.
