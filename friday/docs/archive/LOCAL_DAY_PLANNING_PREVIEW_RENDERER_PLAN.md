# Local Day Planning Preview Renderer Plan

## Ziel

Dieses Dokument plant einen spaeteren Renderer fuer die lokale Tagesplan-Vorschau.

Der Renderer soll aus einem `DayPlanPreview` einen einfachen deutschen CLI-Text erzeugen, aber noch keine CLI-Anbindung bauen.

## Ausgangslage

Vorhanden:

- `friday/app/day_planning_preview.py`
- `DayPlanItem`
- `DayPlanPreview`
- `build_day_plan_preview(tasks, today, limit=None)`
- Fokus-Tests fuer Sortierung und Safety
- Readiness-Gate ohne CLI-Anbindung

## Geplanter Renderer

Vorgeschlagene neue Datei:

```text
friday/app/day_planning_renderer.py
```

Vorgeschlagene Funktion:

```python
render_day_plan_preview(preview: DayPlanPreview) -> str
```

Der Renderer soll nur Text zurueckgeben.

Er soll nicht:

- `print()` verwenden,
- `input()` verwenden,
- SQLite lesen oder schreiben,
- Aufgaben veraendern,
- externe Dienste aufrufen,
- Kalendertermine erstellen,
- Daten persistieren.

## Geplanter Textaufbau

Beispiel fuer Aufgaben:

```text
Lokale Tagesplanung fuer 2026-07-08

Empfohlene Aufgaben:
1. Rechnung pruefen
   Faellig: 2026-07-08
   Prioritaet: high
   Grund: heute faellig

Hinweis: Diese Ansicht ist nur eine lokale Vorschau. Es wurde nichts geaendert.
```

Beispiel ohne Aufgaben:

```text
Lokale Tagesplanung fuer 2026-07-08

Keine offenen Aufgaben fuer die Tagesplanung gefunden.

Hinweis: Diese Ansicht ist nur eine lokale Vorschau. Es wurde nichts geaendert.
```

## Gewuenschte Textregeln

- Ein klarer Titel mit Datum.
- Keine technische Dataclass-Ausgabe.
- Nummerierte Aufgabenliste.
- Pro Aufgabe:
  - Titel,
  - Faelligkeit oder `kein Faelligkeitsdatum`,
  - Prioritaet,
  - Grund.
- Abschlusshinweis:
  - nur lokale Vorschau,
  - nichts geaendert,
  - keine externen Aktionen.

## Geplante Tests

Neue Testdatei:

```text
friday/tests/test_day_planning_renderer.py
```

Tests:

- leere Preview rendert freundliche Leeransicht,
- Preview mit Aufgaben rendert Titel, Datum und nummerierte Liste,
- Aufgaben ohne Faelligkeitsdatum werden verstaendlich angezeigt,
- Safety-Hinweis ist enthalten,
- Renderer verwendet kein `print()` und kein `input()`,
- Renderer veraendert Preview-Objekte nicht.

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

- Dieser Step ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
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

Naechster sinnvoller Build Step: **Local Day Planning Preview Renderer Model**.

Ziel:

- Renderer-Funktion bauen,
- nur String-Ausgabe zurueckgeben,
- keine CLI-Anbindung,
- Tests fuer deutsche Textausgabe und Safety ergaenzen.
