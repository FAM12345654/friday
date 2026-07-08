# Privacy Cleanup DB CLI Write Preview Gate

## Ziel

Dieses Gate prueft, ob die Voraussetzungen fuer eine spaetere SQLite Privacy Cleanup DB Write-Implementierung im Privacy Dashboard ausreichend klar sind.

Der Step bestaetigt:

- DB-Preview ist vorhanden,
- DB-Guard ist vorhanden,
- DB-Writer ist vorhanden,
- read-only DB-Preview ist im Privacy Dashboard sichtbar,
- DB-Write ist noch nicht im Privacy Dashboard aktiv,
- keine automatische Bereinigung ist aktiv,
- keine externen Aktionen sind aktiv.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/privacy_cleanup_db_preview.py` | Read-only DB Preview vorhanden |
| `friday/app/privacy_cleanup_db_guard.py` | Side-effect-free DB Guard vorhanden |
| `friday/app/privacy_cleanup_db_writer.py` | Guarded DB Writer vorhanden |
| `friday/app/interface.py` | Read-only DB-Cleanup-Preview-Anzeige vorhanden |
| `friday/app/menu.py` | DB-Cleanup Preview im Privacy Dashboard sichtbar |
| `friday/docs/PRIVACY_CLEANUP_DB_CLI_WRITE_PLAN.md` | CLI-Write-Plan vorhanden |

## Preview-Gate Ergebnis

Der technische Stack ist bereit fuer eine spaetere Write-Implementierungsplanung.

Freigegeben fuer spaetere Implementierungsvorbereitung:

- eigener DB-Cleanup-Write-Menuepunkt,
- frische Preview direkt vor Write,
- Safety-Smoke-Pruefung direkt vor Write,
- Backup-Nachweis direkt vor Write,
- harte Token-Pruefung,
- Guard-Ausfuehrung,
- Writer-Ausfuehrung nur bei `guard.allowed is True`.

Noch nicht freigegeben:

- aktive DB-Write-Funktion im Privacy Dashboard,
- automatische DB-Bereinigung,
- DB-Write ohne Backup,
- DB-Write ohne Safety Smoke,
- DB-Write ohne hartes Token,
- DB-Write ohne Guard,
- Loeschung pending Vorschlaege,
- Loeschung aktiver Aufgaben, Nachrichten oder Kalenderdaten.

## Mindestanforderungen fuer spaetere Implementierung

Eine spaetere DB-Cleanup-Write-Implementierung muss:

1. Die bestehende read-only Preview beibehalten.
2. Einen separaten Write-Menuepunkt nutzen.
3. Vor jedem Write eine frische Preview erzeugen.
4. Vor jedem Write Safety Smoke ausfuehren.
5. Vor jedem Write einen Backup-Nachweis verlangen.
6. Nur exakte harte Tokens akzeptieren.
7. `ja` und `JA` blockieren.
8. Guard vor Writer ausfuehren.
9. Writer nur mit `guard.allowed is True` ausfuehren.
10. Fehlerpfade stabil ins Privacy Dashboard zurueckfuehren.

## Geplante Testanforderungen

Eine spaetere Implementierung braucht mindestens Tests fuer:

- DB-Write-Menuepunkt erscheint separat von Preview,
- Enter/z bricht stabil ab,
- falscher Token blockiert,
- `ja` blockiert,
- `JA` blockiert,
- fehlendes Backup blockiert,
- Safety-Smoke-Fehler blockiert,
- Guard-Block wird angezeigt,
- Review-History-Write loescht nur sichere Kandidaten,
- Kontakt-Kontext-Write loescht nur ausgewaehlten Kontakt,
- pending Vorschlaege bleiben erhalten,
- Aufgaben bleiben erhalten,
- Rueckkehr/Exit bleiben stabil.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine neue CLI-Write-Funktion.
- Keine SQLite-Schreiboperation in diesem Step.
- Keine SQLite-Loeschung in diesem Step.
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

## Tests

Erwartete Validierung:

```powershell
python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_privacy_cleanup_db_preview.py friday/tests/test_privacy_cleanup_db_guard.py friday/tests/test_privacy_cleanup_db_writer.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Write Implementation Plan**.

Ziel:

- konkrete Implementierung der spaeteren DB-Cleanup-Write-Anbindung planen,
- noch keine Write-Funktion bauen,
- genaue Menueoption, Inputs, Fehlermeldungen und Tests definieren.
