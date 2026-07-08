# Privacy Cleanup DB User Guide Update

## Ziel

Dieses Dokument haelt fest, dass die Nutzer-Dokumentation fuer den SQLite Privacy Cleanup DB Block aktualisiert wurde.

## Aktualisierte Nutzerbereiche

| Bereich | Aktualisierung |
|---|---|
| `README_USER.md` Privacy Dashboard | DB-Cleanup Preview und DB-Cleanup Ausfuehrung ergaenzt |
| `README_USER.md` Privacy Cleanup Preview | Rueckkehr-Option auf `11` aktualisiert |
| `README_USER.md` Privacy Cleanup ausfuehren | Datei-Cleanup und DB-Cleanup klar getrennt |
| `README_USER.md` DB-Cleanup Preview | Neuer Abschnitt fuer read-only SQLite-Preview |
| `README_USER.md` DB-Cleanup ausfuehren | Neuer Abschnitt fuer gegatete SQLite-Cleanup-Ausfuehrung |

## Nutzererklaerung

Friday zeigt jetzt im Privacy Dashboard zwei DB-Cleanup-bezogene Punkte:

```text
9. DB-Cleanup Preview anzeigen
10. DB-Cleanup ausführen
11. Zurück zum Hauptmenü
```

Die Preview ist read-only und loescht nichts.

Die Ausfuehrung ist nur erlaubt, wenn alle Schutzschritte erfuellt sind:

- frische Preview,
- lokaler Backup-Nachweis,
- Safety Smoke `PASS`,
- exakter harter Token,
- DB Guard,
- DB Writer.

## Erlaubte DB-Cleanup-Bereiche

| Bereich | Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Nur Nutzer-Dokumentation aktualisiert.
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

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup DB Documentation Finalization**.

Ziel:

- DB-Cleanup-Dokumente, README und Doku-Index final auf Konsistenz pruefen.
