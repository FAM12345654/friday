# Local Day Planning Preview Readiness Gate

## Ziel

Dieses Gate prueft das isolierte read-only Tagesplan-Preview-Modell vor einer spaeteren CLI-Anbindung.

Geprueft wurden:

- Modellgrenzen,
- Sortierlogik,
- Ausschlussregeln,
- Safety-Grenzen,
- Testabdeckung,
- Dokumentation.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/day_planning_preview.py` | vorhanden, isoliert, read-only |
| `friday/tests/test_day_planning_preview.py` | vorhanden, Fokus-Tests gruen |
| `friday/docs/LOCAL_DAY_PLANNING_PREVIEW_MODEL.md` | vorhanden, Modell und Safety dokumentiert |
| `friday/docs/cli_documentation_index_12l.md` | aktualisiert |

## Readiness-Ergebnis

| Bereich | Ergebnis |
|---|---|
| Keine CLI-Anbindung | bestanden |
| Keine SQLite-Verbindung | bestanden |
| Keine Repository-Nutzung | bestanden |
| Keine Persistenz | bestanden |
| Kein `input()` | bestanden |
| Kein `print()` | bestanden |
| Keine Netzwerk-/Provider-Nutzung | bestanden |
| Keine Datenbankschema-Aenderung | bestanden |
| Deterministische Sortierung | bestanden |
| Ausschluss von `done` und `archived` | bestanden |
| Safety-Flags unveraendert | bestanden |

## Abgesicherte Verhaltensweisen

- Leere Aufgabenlisten erzeugen eine leere Preview.
- Aufgaben mit Status `done` oder `archived` werden ausgeschlossen.
- Aufgaben ohne Titel werden ausgeschlossen.
- Ueberfaellige und heute faellige Aufgaben werden zuerst sortiert.
- Spaetere Aufgaben folgen danach.
- Aufgaben ohne Faelligkeitsdatum werden zuletzt einsortiert.
- Prioritaeten werden in der Reihenfolge `urgent`, `high`, `normal`/`medium`, `low` beruecksichtigt.
- Unbekannte Prioritaeten werden stabil als `normal` behandelt.
- Titel dient als deterministischer Tie-Breaker.
- `limit` begrenzt nur die Preview und schreibt nichts.

## Nicht freigegeben

- Keine CLI-Anbindung.
- Keine automatische Tagesplanung.
- Keine Statusaenderung an Aufgaben.
- Keine Speicherung einer Tagesliste.
- Keine echte Kalenderintegration.
- Keine KI-/Provider-Nutzung.
- Keine externen Aktionen.
- Keine Obsidian-Schreiboperation.

## Safety-Bewertung

- Keine Produktlogik ausserhalb des isolierten Preview-Modells geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
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

## Validierung

```powershell
python -m pytest friday/tests/test_day_planning_preview.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Local Day Planning Preview Renderer Plan**.

Ziel:

- Planen, wie die Day-Planning-Preview spaeter als deutscher CLI-Text angezeigt wird.
- Noch keine CLI-Anbindung bauen.
- Keine Aufgaben veraendern.
