# Privacy Cleanup DB CLI Preview Gate

## Ziel

Dieses Gate prueft, ob der SQLite Privacy Cleanup DB Stack fuer eine spaetere CLI-/Privacy-Dashboard-Anbindung ausreichend vorbereitet ist.

Der Step bestaetigt:

- Preview-Modell ist read-only vorhanden,
- Guard-Modell ist side-effect-free vorhanden,
- Writer-Modell ist isoliert vorhanden,
- CLI-Anbindung ist noch nicht aktiv,
- keine automatische Bereinigung ist aktiv,
- keine externen Aktionen sind aktiv.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/privacy_cleanup_db_preview.py` | Read-only DB Preview vorhanden |
| `friday/app/privacy_cleanup_db_guard.py` | Side-effect-free DB Guard vorhanden |
| `friday/app/privacy_cleanup_db_writer.py` | Guarded DB Writer vorhanden |
| `friday/tests/test_privacy_cleanup_db_preview.py` | Preview-Fokus-Tests vorhanden |
| `friday/tests/test_privacy_cleanup_db_guard.py` | Guard-Fokus-Tests vorhanden |
| `friday/tests/test_privacy_cleanup_db_writer.py` | Writer-Fokus-Tests vorhanden |
| `friday/docs/PRIVACY_CLEANUP_DB_CLI_PLAN.md` | CLI-Plan vorhanden |

## Preview-Gate Ergebnis

Der DB-Cleanup-Stack ist technisch vorbereitet, aber noch nicht fuer eine aktive CLI-Ausfuehrung freigegeben.

Freigegeben fuer spaetere Planung:

- DB-Cleanup-Vorschau im Privacy Dashboard,
- Anzeige sicherer Kandidatenzahlen,
- Anzeige harter Tokens,
- Anzeige von Backup-/Transaktions-/Rollback-Anforderungen.

Noch nicht freigegeben:

- Menuepunkt fuer DB-Cleanup-Write,
- direkte Ausfuehrung im Privacy Dashboard,
- automatische Bereinigung,
- Loeschung ohne unmittelbar vorherige Preview,
- Loeschung ohne Guard,
- Loeschung ohne Backup-Nachweis,
- Loeschung ohne Safety-Smoke-PASS.

## Mindestbedingungen fuer spaetere CLI-Anbindung

Eine spaetere CLI-Anbindung darf nur gebaut werden, wenn:

1. DB-Preview direkt vor dem Write angezeigt wird.
2. Nutzer den Bereich explizit auswaehlt.
3. Kontakt-Kontext nur mit exakter `contact_id` geloescht wird.
4. Guard mit Preview, Backup, Token, Rollback und Safety-Smoke ausgefuehrt wird.
5. Writer nur bei `guard.allowed is True` laeuft.
6. Fehlerpfade stabil ins Privacy-Menue zurueckkehren.
7. Ergebnis nur sichere Zaehler enthaelt.

## Geplante CLI-Testanforderungen

Eine spaetere CLI-Implementierung braucht Tests fuer:

- Preview anzeigen ohne Loeschung,
- falscher Token blockiert,
- `ja` blockiert,
- `JA` blockiert,
- exakter Token erlaubt nur nach Guard-Freigabe,
- fehlendes Backup blockiert,
- Safety-Smoke-Fehler blockiert,
- Kontakt-Kontext ohne Auswahl blockiert,
- Rueckkehr ins Privacy-Menue bleibt stabil,
- Exit bleibt stabil.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine CLI-Anbindung gebaut.
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
python -m pytest friday/tests/test_privacy_cleanup_db_preview.py friday/tests/test_privacy_cleanup_db_guard.py friday/tests/test_privacy_cleanup_db_writer.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Read-Only Preview Implementation**.

Ziel:

- nur die DB-Cleanup-Preview im Privacy Dashboard anzeigen,
- keine Write-Ausfuehrung,
- keine SQLite-Loeschung ueber CLI.
