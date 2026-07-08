# Privacy Cleanup DB CLI Read-Only Preview Implementation

## Ziel

Dieser Step bindet die SQLite Privacy Cleanup DB Preview als reine Anzeige in das Privacy Dashboard ein.

Die neue CLI-Option ist read-only:

- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- kein Guard-Aufruf,
- kein Writer-Aufruf,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/menu.py` | Privacy-Dashboard-Menue um DB-Cleanup Preview erweitert |
| `friday/app/interface.py` | Read-only DB-Cleanup-Preview-Anzeige ergänzt |
| `friday/tests/test_menu.py` | Menueoptionen angepasst |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Test fuer read-only DB-Cleanup-Preview ergänzt |

## Neue Privacy-Dashboard-Option

```text
9. DB-Cleanup Preview anzeigen
10. Zurück zum Hauptmenü
```

## Angezeigte Informationen

Die Anzeige zeigt nur sichere Metadaten:

- Bereich,
- Tabelle,
- Filter,
- Kandidatenanzahl,
- erforderlicher Token,
- Status,
- Backup-/Transaktions-/Rollback-Anforderung,
- Blockierungsgruende.

## Nicht ausgefuehrt

Die Anzeige fuehrt nicht aus:

- kein DB-Write,
- kein DB-Delete,
- kein Guard,
- kein Writer,
- kein Safety-Smoke-Lauf,
- keine externe Aktion.

## Safety-Bewertung

- Nur read-only Preview im Privacy Dashboard.
- Keine aktive DB-Cleanup-Ausfuehrung.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Read-Only Preview Readiness Gate**.

Ziel:

- neue read-only DB-Preview-Anzeige final pruefen und dokumentieren,
- weiterhin keine DB-Write-Funktion im Menue.
