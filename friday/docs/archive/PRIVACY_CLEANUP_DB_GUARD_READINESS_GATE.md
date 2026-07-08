# Privacy Cleanup DB Guard Readiness Gate

## Ziel

Dieses Gate prueft den Stand des isolierten SQLite Privacy Cleanup DB Guard Models.

Der Step bestaetigt:

- Guard ist side-effect-free,
- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine CLI-Anbindung,
- keine externen Aktionen.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/privacy_cleanup_db_preview.py` | Read-only Preview-Modell vorhanden |
| `friday/app/privacy_cleanup_db_guard.py` | Side-effect-free Guard-Modell vorhanden |
| `friday/tests/test_privacy_cleanup_db_preview.py` | Preview-Fokus-Tests vorhanden |
| `friday/tests/test_privacy_cleanup_db_guard.py` | Guard-Fokus-Tests vorhanden |
| `friday/docs/PRIVACY_CLEANUP_DB_GUARD_PLAN.md` | Guard-Plan vorhanden |
| `friday/docs/PRIVACY_CLEANUP_DB_GUARD_MODEL.md` | Guard-Modell dokumentiert |

## Readiness-Ergebnis

Das DB Guard Model ist bereit als isolierter lokaler Sicherheitsbaustein.

Freigegeben ist nur:

- vorhandene Preview-Ergebnisse bewerten,
- bekannte Cleanup-Bereiche pruefen,
- harte Tokens pruefen,
- Backup-/Transaktions-/Rollback-Anforderungen pruefen,
- Safety-Smoke-Status pruefen,
- externe Aktionen blockieren,
- sichere Blockierungsgruende zurueckgeben.

Nicht freigegeben ist:

- SQLite oeffnen,
- Datensaetze loeschen,
- Datensaetze schreiben,
- Datenbankschema aendern,
- Migration ausfuehren,
- CLI-Ausfuehrung,
- automatisches Cleanup,
- externe Aktion.

## Abgesicherte Guard-Regeln

| Regel | Status |
|---|---|
| Missing Preview blockiert | abgesichert |
| Unbekannter Bereich blockiert | abgesichert |
| Falscher Token blockiert | abgesichert |
| `ja` und `JA` blockieren | abgesichert |
| Fehlendes Backup blockiert | abgesichert |
| Fehlende Transaktion blockiert | abgesichert |
| Fehlender Rollback blockiert | abgesichert |
| Safety-Smoke-Fehler blockiert | abgesichert |
| Externe Aktionen blockieren | abgesichert |
| Unsichere Preview-Filter blockieren | abgesichert |
| Sichtbare sensible Inhalte blockieren | abgesichert |
| Leere Kandidatenmenge blockiert | abgesichert |

## Safety-Bewertung

- Keine Produktlogik mit CLI-Anbindung.
- Keine SQLite-Schreiboperation.
- Keine SQLite-Loeschung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine sensiblen Inhalte in Guard-Ausgaben.
- Tests nutzen lokale `tmp_path` SQLite-Datenbanken fuer Preview-Fixtures.
- Guard selbst oeffnet keine SQLite-Verbindung.
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
python -m pytest friday/tests/test_privacy_cleanup_db_preview.py friday/tests/test_privacy_cleanup_db_guard.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup DB Writer Plan**.

Ziel:

- planen, wie ein spaeterer DB-Cleanup-Writer aussehen duerfte,
- weiterhin keine SQLite-Loeschung,
- weiterhin keine CLI-Anbindung,
- zuerst nur Planung.
