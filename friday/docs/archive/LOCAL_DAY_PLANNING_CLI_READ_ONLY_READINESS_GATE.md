# Local Day Planning CLI Read-Only Readiness Gate

## Ziel

Dieses Gate prueft die read-only CLI-Anbindung der lokalen Tagesplanung im Aufgabenmenue.

Geprueft wurden:

- Menuefuehrung,
- Ruecksprung-Verhalten,
- read-only Datenfluss,
- Ausgabe,
- Safety-Grenzen,
- Testabdeckung.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/menu.py` | Aufgabenmenue enthaelt `11. Lokale Tagesplanung anzeigen` und `12. Zurück zum Hauptmenü` |
| `friday/app/interface.py` | `_show_local_day_plan_preview()` ist angebunden |
| `friday/app/day_planning_preview.py` | Preview-Modell bleibt isoliert und read-only |
| `friday/app/day_planning_renderer.py` | Renderer gibt nur deutschen Text zurueck |
| `friday/tests/test_menu.py` | Menueoptionen aktualisiert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Pfad fuer Tagesplan-Anzeige getestet |
| `friday/docs/LOCAL_DAY_PLANNING_CLI_READ_ONLY_IMPLEMENTATION.md` | Implementierung dokumentiert |
| `friday/docs/cli_documentation_index_12l.md` | aktualisiert |

## Readiness-Ergebnis

| Bereich | Ergebnis |
|---|---|
| Aufgabenmenue erweitert | bestanden |
| Rueckkehr ueber `12` | bestanden |
| Tagesplanung ueber `11` | bestanden |
| Nutzt `TaskAgent.get_open_tasks()` | bestanden |
| Nutzt `build_day_plan_preview(...)` | bestanden |
| Nutzt `render_day_plan_preview(...)` | bestanden |
| Keine Aufgabe wird erstellt | bestanden |
| Keine Aufgabe wird geaendert | bestanden |
| Keine Aufgabe wird erledigt | bestanden |
| Keine Aufgabe wird archiviert | bestanden |
| Keine Aufgabe wird geloescht | bestanden |
| Keine Tagesliste wird gespeichert | bestanden |
| Keine externen Aktionen | bestanden |
| Safety-Flags unveraendert | bestanden |

## Abgesicherte Verhaltensweisen

- Das Aufgabenmenue zeigt die lokale Tagesplanung.
- Die lokale Tagesplanung rendert deutsche Preview-Texte.
- Die Tagesplanung bleibt im Aufgabenmenue und kehrt danach stabil zurueck.
- Der bestehende Task-Flow bleibt kompatibel.
- Quick Add, Markdown Export und Full Local Task Journey bleiben gruen.
- Die Anzeige veraendert den Task-Zustand nicht.

## Nicht freigegeben

- Kein Hauptmenuepunkt fuer Tagesplanung.
- Keine automatische Tagesplanung.
- Keine Speicherung einer Tagesliste.
- Keine Aenderung an Aufgabenstatus.
- Keine echte Kalenderintegration.
- Keine KI-/Provider-Nutzung.
- Keine Obsidian-Schreiboperation.
- Keine externen Aktionen.

## Safety-Bewertung

- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Schreiboperationen durch die Tagesplan-Anzeige.
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
python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_day_planning_preview.py friday/tests/test_day_planning_renderer.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Local Day Planning User Guide Update**.

Ziel:

- `README_USER.md` um die neue Tagesplan-Anzeige im Aufgabenmenue ergaenzen.
- Kurz erklaeren, dass die Ansicht read-only ist.
- Keine Produktlogik aendern.
