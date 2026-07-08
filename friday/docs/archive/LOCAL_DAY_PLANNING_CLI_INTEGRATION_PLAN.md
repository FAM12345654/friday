# Local Day Planning CLI Integration Plan

## Ziel

Dieses Dokument plant die spaetere read-only CLI-Anbindung der lokalen Tagesplanung.

Es wird noch keine CLI-Anbindung gebaut.

## Ausgangslage

Vorhandene Bausteine:

- `friday/app/day_planning_preview.py`
- `friday/app/day_planning_renderer.py`
- `friday/tests/test_day_planning_preview.py`
- `friday/tests/test_day_planning_renderer.py`
- `LOCAL_DAY_PLANNING_PREVIEW_READINESS_GATE.md`
- `LOCAL_DAY_PLANNING_PREVIEW_RENDERER_READINESS_GATE.md`

Aktuelle Menues:

- Hauptmenue: `1-12`
- Aufgabenmenue: `1-10`

## Empfohlene CLI-Position

Empfohlen wird eine read-only Anbindung im Aufgabenmenue:

```text
11. Lokale Tagesplanung anzeigen
```

Begruendung:

- Die Tagesplanung basiert auf lokalen Aufgaben.
- Das Hauptmenue bleibt stabil.
- Nutzer findet die Funktion dort, wo Aufgaben bereits verwaltet werden.
- Der erste CLI-Step bleibt klein und gut testbar.

Danach sollte die Rueckkehr-Option verschoben werden auf:

```text
12. Zurück zum Hauptmenü
```

## Geplanter Datenfluss

```text
Aufgabenmenue
-> Lokale Tagesplanung anzeigen
-> TaskAgent.get_open_tasks()
-> build_day_plan_preview(tasks, today)
-> render_day_plan_preview(preview)
-> Text anzeigen
-> zurueck ins Aufgabenmenue
```

## Geplante Produktdateien

| Datei | Geplante Änderung |
|---|---|
| `friday/app/menu.py` | Aufgabenmenue um Tagesplan-Punkt erweitern |
| `friday/app/interface.py` | Methode `_show_local_day_plan_preview()` ergaenzen |
| `friday/tests/test_menu.py` | Aufgabenmenue-Option pruefen |
| `friday/tests/test_interface_main_menu_e2e.py` | read-only Tagesplan-CLI-Pfad pruefen |

## Geplante Interface-Methode

```python
def _show_local_day_plan_preview(self) -> None:
    tasks = self.task_agent.get_open_tasks()
    preview = build_day_plan_preview(tasks, today=config.DEMO_DATE)
    print(render_day_plan_preview(preview))
```

Hinweis:

- Wenn `USE_REAL_TODAY` spaeter aktiv ist, kann `today` ueber TaskAgent oder Config-Logik angepasst werden.
- Fuer die erste CLI-Anbindung bleibt der Datenfluss read-only.

## Geplante Tests

Fokus-Tests:

- Aufgabenmenue zeigt `Lokale Tagesplanung anzeigen`.
- Auswahl im Aufgabenmenue rendert lokale Tagesplanung.
- Ausgabe enthaelt Titel, Aufgabe, Prioritaet und Safety-Hinweis.
- Leerer TaskAgent zeigt freundliche Leeransicht.
- Nach Anzeige bleibt Aufgabenmenue stabil.
- Keine Aufgabe wird erstellt, geaendert, erledigt, archiviert oder geloescht.

Validierung:

```powershell
python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_day_planning_preview.py friday/tests/test_day_planning_renderer.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Nicht-Ziele

- Kein Hauptmenuepunkt in diesem ersten CLI-Step.
- Keine automatische Tagesplanung.
- Keine Speicherung einer Tagesliste.
- Keine Aenderung an Aufgabenstatus.
- Keine echte Kalenderintegration.
- Keine KI-/Provider-Nutzung.
- Keine Obsidian-Schreiboperation.

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

Naechster sinnvoller Build Step: **Local Day Planning CLI Read-Only Implementation**.

Ziel:

- Tagesplanung read-only im Aufgabenmenue anzeigen.
- Keine Aufgaben veraendern.
- Keine Persistenz.
- Keine externen Aktionen.
