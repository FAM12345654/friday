# Local Day Planning CLI Read-Only Implementation

## Ziel

Dieses Dokument beschreibt die read-only CLI-Anbindung der lokalen Tagesplanung im Aufgabenmenue.

## Geaenderte Dateien

| Datei | Änderung |
|---|---|
| `friday/app/menu.py` | Aufgabenmenue um `11. Lokale Tagesplanung anzeigen` erweitert |
| `friday/app/interface.py` | Read-only Methode `_show_local_day_plan_preview()` ergaenzt |
| `friday/tests/test_menu.py` | Aufgabenmenue-Optionen aktualisiert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Test fuer Tagesplan-Anzeige ergaenzt |

## CLI-Pfad

```text
Hauptmenue -> 1. Aufgaben verwalten -> 11. Lokale Tagesplanung anzeigen
```

Rueckkehr:

```text
12. Zurück zum Hauptmenü
```

## Verhalten

Friday:

1. liest offene Aufgaben ueber `TaskAgent.get_open_tasks()`,
2. baut eine read-only Preview mit `build_day_plan_preview(...)`,
3. rendert deutschen Text mit `render_day_plan_preview(...)`,
4. zeigt den Text im Aufgabenmenue an.

## Read-only-Grenzen

- Keine Aufgabe wird erstellt.
- Keine Aufgabe wird geaendert.
- Keine Aufgabe wird erledigt.
- Keine Aufgabe wird archiviert.
- Keine Aufgabe wird geloescht.
- Keine Tagesliste wird gespeichert.
- Keine externe Aktion wird ausgefuehrt.
- Keine echte Kalenderintegration.
- Keine KI-/Provider-Nutzung.

## Safety-Bewertung

- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
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

Naechster sinnvoller Build Step: **Local Day Planning CLI Read-Only Readiness Gate**.

Ziel:

- CLI-Anbindung final pruefen,
- Menue-/Ruecksprung-Verhalten dokumentieren,
- Safety-Grenzen bestaetigen.
