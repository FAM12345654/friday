# Privacy Cleanup DB Preview Readiness Gate

## Ziel

Dieses Gate prueft den Stand des isolierten read-only SQLite-Cleanup-Preview-Modells.

Der Step bestaetigt:

- DB-Preview ist nur Vorschau,
- keine SQLite-Loeschung,
- keine SQLite-Schreiboperation,
- keine Datenbankschema-Aenderung,
- keine CLI-Anbindung,
- keine externen Aktionen.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/privacy_cleanup_db_preview.py` | Read-only Preview-Modell vorhanden |
| `friday/tests/test_privacy_cleanup_db_preview.py` | Fokus-Tests vorhanden |
| `friday/docs/PRIVACY_CLEANUP_DB_PREVIEW_PLAN.md` | Plan-Doku vorhanden |
| `friday/docs/PRIVACY_CLEANUP_DB_PREVIEW_MODEL.md` | Modell-Doku vorhanden |
| `friday/docs/cli_documentation_index_12l.md` | Index auf aktuellen Stand erweitert |

## Readiness-Ergebnis

Das DB-Preview-Modell ist bereit als isolierter lokaler Baustein.

Freigegeben ist nur:

- bekannte SQLite-Tabellen read-only oeffnen,
- sichere Cleanup-Kandidaten zaehlen,
- sensible Inhalte ausblenden,
- erlaubte Bereiche als `preview_only` markieren,
- gesperrte Bereiche als `blocked` markieren.

Nicht freigegeben ist:

- Loeschen,
- Schreiben,
- Migration,
- Schema-Aenderung,
- CLI-Ausfuehrung,
- automatisches Cleanup,
- externe Aktion.

## Abgesicherte Bereiche

| Bereich | Status | Begrenzung |
|---|---|---|
| Review-History | read-only preview | Nur `rejected` Nachrichten-Vorschlaege und `converted` Aufgaben-Vorschlaege mit vorhandener Aufgabe |
| Kontakt-Kontext | read-only preview | Nur exakt ausgewaehlter `contact_id` |
| Aufgaben | blocked | Braucht separates Task-Cleanup-Gate |
| Nachrichten | blocked | Braucht separates Message-Cleanup-Gate |
| Kalender | blocked | Braucht separates Calendar-Cleanup-Gate |
| Datenbankschema | blocked | Keine Schema-Aenderung erlaubt |

## Safety-Bewertung

- Keine Produktlogik mit CLI-Anbindung.
- Keine SQLite-Schreiboperation.
- Keine SQLite-Loeschung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine sensiblen Inhalte in der Preview-Ausgabe.
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
python -m pytest friday/tests/test_privacy_cleanup_db_preview.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup DB Guard Plan**.

Ziel:

- planen, welche Guard-Regeln vor einem spaeteren DB-Cleanup-Write gelten muessen,
- weiterhin keine SQLite-Loeschung,
- weiterhin keine CLI-Anbindung.
