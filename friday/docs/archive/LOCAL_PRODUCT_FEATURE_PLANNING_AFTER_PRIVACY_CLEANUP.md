# Local Product Feature Planning After Privacy Cleanup

## Ziel

Dieses Dokument plant den naechsten kleinen lokalen Produktfortschritt nach dem abgeschlossenen Privacy-Cleanup-Block.

Der Schritt bleibt bewusst Planungsarbeit:

- keine Produktlogik aendern,
- keine Tests aendern,
- keine Datenbankschema-Aenderung,
- keine externen Integrationen,
- keine echten Nachrichten,
- keine echten Kalendertermine.

## Ausgangslage

Abgeschlossen und stabil:

- lokales Aufgabenmenue,
- Task Create/Edit/Search/Done/Archive/Delete,
- Review-/Suggestion-Flows,
- lokaler Export-/Import-/Backup-/Restore-Stack,
- Safety Scanner / Smoke,
- Obsidian Preview/Guard-Bausteine,
- Privacy Dashboard,
- Datei-Cleanup und DB-Cleanup mit Guards und harten Tokens.

Der Privacy-Cleanup-Block ist als stabiler Baustein abgeschlossen und sollte nur bei echten Regressionen oder Safety-Anpassungen erneut geaendert werden.

## Bewertete naechste Produktoptionen

| Option | Nutzen | Risiko | Testaufwand | Safety-Komplexitaet | Bewertung |
|---|---|---|---|---|---|
| Local Day Planning Preview | Hoch: Nutzer sieht direkt eine sortierte Tagesplanung | Niedrig: kann read-only starten | Mittel: Task-Sortierung, leere Liste, erledigte/archivierte Aufgaben | Niedrig: nur lokale SQLite-Aufgaben, keine Writes | empfohlen |
| Review Batch Actions | Mittel: schnellerer Review-Flow | Mittel bis hoch: Statusuebergaenge komplex | Hoch: Message-, Task-Suggestion- und Combined-Review | Mittel: lokale Statuswrites, keine externen Sends | spaeter |
| Contact CLI Read-Only Menu | Mittel: Kontaktbereich sichtbarer machen | Niedrig bis mittel: Repository/CLI-Verknuepfung | Mittel | Niedrig: read-only | gut, aber weniger direkt nutzbar |
| Obsidian Write Approval | Mittel: echter lokaler Brain-Write | Hoeher: Dateisystem-Write und Pfad-Safety | Hoch | Mittel: harter Token, Vault-Pfade, Dedupe | erst nach eigenem Gate |
| Local Model Logic Check Integration | Hoch: spaeter mehr Intelligenz | Mittel bis hoch: Validierung/Provider-Grenzen | Hoch | Mittel: keine Cloud, Mock/Local only | spaeter |

## Empfohlener naechster Produkt-Step

**Name:** Local Day Planning Preview

**Ziel:** Friday erstellt eine lokale, read-only Tagesplan-Vorschau aus vorhandenen Aufgaben.

Der erste technische Schritt soll keine Aufgaben veraendern. Er soll nur eine sortierte Vorschau erzeugen, zum Beispiel:

```text
Heute empfohlen:
1. Rechnung pruefen [high] faellig: 2026-07-08
2. Einkauf planen [medium] faellig: 2026-07-09
```

## Warum dieser Step sinnvoll ist

- Nutzer bekommt einen echten Alltagsnutzen.
- Bestehende lokale Task-Daten reichen aus.
- Kein externer Kalender notwendig.
- Keine KI-Provider notwendig.
- Keine Datenbankschema-Aenderung notwendig.
- Kann zuerst read-only umgesetzt werden.
- Gut testbar mit `tmp_path` SQLite.
- Passt zum bisherigen local-first Safety-Modell.

## Nicht-Ziele

- Keine echte Kalenderintegration.
- Keine automatische Terminplanung.
- Keine KI-Modellbewertung.
- Keine Aenderung an Aufgabenstatus.
- Keine Persistenz einer Tagesliste.
- Keine neuen externen Provider.
- Keine Benachrichtigungen.
- Keine Obsidian-Schreiboperation.

## Grober Zielumfang fuer den naechsten technischen Step

Naechster Step sollte ein isoliertes Preview-Modell bauen:

```text
friday/app/day_planning_preview.py
friday/tests/test_day_planning_preview.py
friday/docs/LOCAL_DAY_PLANNING_PREVIEW_MODEL.md
```

Moegliche Datenstruktur:

```python
DayPlanItem
DayPlanPreview
```

Moegliche Funktion:

```python
build_day_plan_preview(tasks, today)
```

Sortierlogik fuer die erste Version:

1. offene Aufgaben zuerst,
2. faellige oder ueberfaellige Aufgaben zuerst,
3. Prioritaet `high`, dann `medium`, dann `low`,
4. frueheres Faelligkeitsdatum zuerst,
5. Titel als stabiler Tie-Breaker.

## Teststrategie fuer den naechsten Step

Fokus-Tests:

- leere Aufgabenliste erzeugt leere Preview,
- erledigte und archivierte Aufgaben werden nicht empfohlen,
- ueberfaellige Aufgaben erscheinen vor spaeteren Aufgaben,
- `high` erscheint vor `medium` und `low`,
- fehlendes Faelligkeitsdatum bleibt stabil,
- gleiche Prioritaet wird deterministisch sortiert,
- Preview schreibt nichts in SQLite,
- keine externen Aktionen.

Validierung:

```powershell
python -m pytest friday/tests/test_day_planning_preview.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Keine Produktlogik in diesem Planungsstep geaendert.
- Keine Tests in diesem Planungsstep geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Wetter- oder Musik-Aktionen.
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

Naechster sinnvoller Build Step: **Local Day Planning Preview Model**.

Ziel:

- isoliertes read-only Preview-Modell fuer Tagesplanung bauen,
- keine CLI-Anbindung,
- keine Persistenz,
- keine externen Aktionen,
- Tests fuer Sortierung und Safety ergaenzen.
