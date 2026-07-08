# Privacy Cleanup DB CLI Write Implementation

## Ziel

Dieser Step bindet den guarded SQLite Privacy Cleanup DB Writer in das Privacy Dashboard ein.

Die DB-Cleanup-Ausfuehrung ist nur mit mehreren Schutzschritten moeglich:

- frische Preview,
- lokaler Backup-Nachweis,
- Safety Smoke `PASS`,
- exakter harter Token,
- Guard-Freigabe,
- Writer-Ausfuehrung mit Transaktion.

## Umgesetzte Dateien

| Datei | Zweck |
|---|---|
| `friday/app/menu.py` | Privacy-Dashboard-Menue um DB-Cleanup-Write erweitert |
| `friday/app/interface.py` | Guarded DB-Cleanup-Write-Flow ergänzt |
| `friday/tests/test_menu.py` | Menueoptionen angepasst |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Tests fuer Blockierungs- und Erfolgspfade ergänzt |

## Neuer Menue-Stand

```text
9. DB-Cleanup Preview anzeigen
10. DB-Cleanup ausführen
11. Zurück zum Hauptmenü
```

## Sicherheitsablauf

1. Bereich auswaehlen.
2. Frische DB-Cleanup-Preview erzeugen.
3. Backup-Nachweis in `local_data/backups/` pruefen.
4. Safety Smoke ausfuehren.
5. Harten Token abfragen.
6. DB Guard ausfuehren.
7. DB Writer nur bei Guard-Freigabe ausfuehren.
8. Sichere Ergebniszaehler anzeigen.

## Erlaubte Bereiche

| Bereich | Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

## Tests

Die Tests pruefen:

- fehlendes Backup blockiert,
- falscher Token blockiert,
- Review-History-Cleanup loescht nur sichere Kandidaten,
- pending Vorschlaege bleiben erhalten,
- lokale Aufgaben bleiben erhalten,
- Kontakt-Kontext-Cleanup loescht nur ausgewaehlten Kontakt.

## Safety-Bewertung

- DB-Write nur nach Preview, Backup, Safety Smoke, Token und Guard.
- Keine externen Aktionen.
- Keine Datenbankschema-Aenderung.
- Keine automatische Bereinigung.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Write Readiness Gate**.

Ziel:

- neue guarded DB-Cleanup-Write-Anbindung final pruefen und dokumentieren.
