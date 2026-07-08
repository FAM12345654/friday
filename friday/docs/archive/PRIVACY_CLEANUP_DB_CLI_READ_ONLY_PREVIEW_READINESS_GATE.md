# Privacy Cleanup DB CLI Read-Only Preview Readiness Gate

## Ziel

Dieses Gate prueft die neue read-only DB-Cleanup-Preview-Anzeige im Privacy Dashboard.

Der Step bestaetigt:

- DB-Cleanup-Preview ist im Privacy Dashboard sichtbar,
- Anzeige ist read-only,
- kein Guard wird ausgefuehrt,
- kein Writer wird ausgefuehrt,
- keine SQLite-Loeschung ueber CLI,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/menu.py` | Privacy-Dashboard-Menue enthaelt DB-Cleanup Preview |
| `friday/app/interface.py` | Read-only Anzeige nutzt `build_privacy_cleanup_db_preview` |
| `friday/tests/test_menu.py` | Menueoptionen abgesichert |
| `friday/tests/test_interface_main_menu_e2e.py` | DB-Cleanup-Preview-Anzeige abgesichert |
| `friday/app/privacy_cleanup_db_preview.py` | Read-only DB-Preview-Modell vorhanden |
| `friday/app/privacy_cleanup_db_guard.py` | Guard-Modell vorhanden, aber nicht durch Anzeige ausgefuehrt |
| `friday/app/privacy_cleanup_db_writer.py` | Writer-Modell vorhanden, aber nicht durch Anzeige ausgefuehrt |

## Readiness-Ergebnis

Die read-only DB-Cleanup-Preview-Anzeige ist bereit als sichere Privacy-Dashboard-Funktion.

Freigegeben ist:

- Anzeige der DB-Cleanup-Kandidaten,
- Anzeige von Tabellen, Filtern und Kandidatenzahlen,
- Anzeige harter Tokens,
- Anzeige von Backup-/Transaktions-/Rollback-Anforderungen,
- Anzeige blockierter Bereiche.

Nicht freigegeben ist:

- DB-Cleanup-Write ueber CLI,
- Guard-Ausfuehrung ueber die Anzeige,
- Writer-Ausfuehrung ueber die Anzeige,
- automatische Bereinigung,
- Loeschung ohne eigenes spaeteres Gate.

## Menue-Stand

```text
Privacy Dashboard
1. Lokale Datenbereiche anzeigen
2. Safety-Flags anzeigen
3. Externe Aktionen anzeigen
4. Gated Actions anzeigen
5. Safety Scanner anzeigen
6. Privacy Data Management Inventory anzeigen
7. Privacy Cleanup Preview anzeigen
8. Privacy Cleanup ausführen
9. DB-Cleanup Preview anzeigen
10. Zurück zum Hauptmenü
```

## Safety-Bewertung

- Keine Produktlogik fuer DB-Write aktiviert.
- Keine SQLite-Schreiboperation ueber CLI.
- Keine SQLite-Loeschung ueber CLI.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Write Plan**.

Ziel:

- planen, ob und wie ein DB-Cleanup-Write spaeter sicher im Privacy Dashboard angeboten werden duerfte,
- zuerst nur Planung,
- keine neue Write-Funktion ohne eigenes Gate.
