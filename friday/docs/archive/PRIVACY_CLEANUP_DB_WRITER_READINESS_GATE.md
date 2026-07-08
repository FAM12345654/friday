# Privacy Cleanup DB Writer Readiness Gate

## Ziel

Dieses Gate prueft den Stand des isolierten SQLite Privacy Cleanup DB Writer Models.

Der Step bestaetigt:

- Writer laeuft nur mit Guard-Freigabe,
- Writer nutzt eine SQLite-Transaktion,
- Writer rollt bei Kandidaten-Abweichung zurueck,
- Writer ist nicht an CLI oder Privacy Dashboard angebunden,
- Writer aendert kein Datenbankschema,
- Writer nutzt keine externen Aktionen.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/privacy_cleanup_db_preview.py` | Read-only Preview-Modell vorhanden |
| `friday/app/privacy_cleanup_db_guard.py` | Side-effect-free Guard-Modell vorhanden |
| `friday/app/privacy_cleanup_db_writer.py` | Guarded Writer-Modell vorhanden |
| `friday/tests/test_privacy_cleanup_db_preview.py` | Preview-Fokus-Tests vorhanden |
| `friday/tests/test_privacy_cleanup_db_guard.py` | Guard-Fokus-Tests vorhanden |
| `friday/tests/test_privacy_cleanup_db_writer.py` | Writer-Fokus-Tests vorhanden |
| `friday/docs/PRIVACY_CLEANUP_DB_WRITER_MODEL.md` | Writer-Modell dokumentiert |

## Readiness-Ergebnis

Das DB Writer Model ist bereit als isolierter lokaler Baustein.

Freigegeben ist nur:

- SQLite-Cleanup nach explizit erlaubtem Guard-Ergebnis,
- Loeschung von sicheren Review-History-Kandidaten,
- Loeschung eines exakt ausgewaehlten Kontakt-Kontexts,
- Ausfuehrung in expliziter Transaktion,
- Rollback bei Kandidaten-Abweichung,
- Rueckgabe sicherer Zaehler.

Nicht freigegeben ist:

- CLI-Ausfuehrung,
- Privacy-Dashboard-Anbindung,
- automatische Bereinigung,
- Loeschung aktiver Aufgaben,
- Loeschung aktiver Nachrichten,
- Loeschung pending Vorschlaege,
- Loeschung von Kalenderdaten,
- Datenbankschema-Aenderung,
- externe Aktion.

## Abgesicherte Writer-Regeln

| Regel | Status |
|---|---|
| Nicht erlaubter Guard blockiert | abgesichert |
| Review-History loescht nur sichere Kandidaten | abgesichert |
| Pending Vorschlaege bleiben erhalten | abgesichert |
| Lokale Aufgaben bleiben erhalten | abgesichert |
| Kontakt-Kontext braucht exakte Auswahl | abgesichert |
| Nur ausgewaehlter Kontakt-Kontext wird geloescht | abgesichert |
| Kandidaten-Abweichung fuehrt zu Rollback | abgesichert |
| Ergebnis enthaelt keine sensiblen Inhalte | abgesichert |
| Keine Datenbankschema-Aenderung | abgesichert |
| Keine externen Aktionen | abgesichert |

## Safety-Bewertung

- SQLite-Deletes nur isoliert und mit Guard-Freigabe.
- Keine CLI-Anbindung.
- Keine automatische Bereinigung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine sensiblen Inhalte in Writer-Ergebnissen.
- Tests nutzen lokale `tmp_path` SQLite-Datenbanken.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Plan**.

Ziel:

- planen, ob und wie die DB-Cleanup-Funktion spaeter ins Privacy Dashboard eingebunden werden duerfte,
- zuerst nur Planung,
- keine neue CLI-Write-Anbindung ohne eigenes Gate.
