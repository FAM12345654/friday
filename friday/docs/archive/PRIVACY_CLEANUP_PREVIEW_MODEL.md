# Privacy Cleanup Preview Model

## Ziel

Dieser Schritt setzt ein isoliertes read-only Modell fuer spaetere Privacy-Cleanup-Vorschauen um.

Das Modell beschreibt nur, welche Bereiche theoretisch bereinigt werden koennten oder blockiert bleiben.

## Umsetzung

Neue Datei:

- `friday/app/privacy_cleanup_preview.py`

Neue Tests:

- `friday/tests/test_privacy_cleanup_preview.py`

Das Modell erzeugt ein `PrivacyCleanupPreview` mit:

- `items`: geplante oder blockierte Cleanup-Preview-Eintraege,
- `blocked_actions`: eindeutige Blockiergruende,
- `writes_performed = False`,
- `deletes_performed = False`,
- `external_lookup_used = False`.

## Abgedeckte Preview-Bereiche

| Bereich | Status |
|---|---|
| Exporte | Preview erlaubt, Root `local_data/exports` |
| Backups | Preview erlaubt, Root `local_data/backups` |
| Restore-Kopien | Preview erlaubt, Root `local_data/restores` |
| Review-Vorschlaege | Status-Preview erlaubt |
| Kontakt-Kontexte | Einzelkontakt-Preview erlaubt |
| Aufgaben | blockiert im Privacy Cleanup |
| aktive SQLite-DB | blockiert |
| `.env` / Secrets | blockiert |
| Obsidian Vault | blockiert |
| globale Loeschaktion | blockiert |

## Safety-Grenzen

- Kein Dateisystem-Scan.
- Kein Dateizugriff.
- Kein SQLite-Zugriff.
- Keine Dateioperation.
- Keine Loeschfunktion.
- Keine Exportfunktion.
- Keine CLI-Anbindung.
- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Keine Provider-Aufrufe.

## Tests

Die Tests pruefen:

- Preview bleibt read-only.
- Standardbereiche werden gelistet.
- Explizite Counts werden uebernommen.
- Harte spaetere Tokens werden markiert.
- Pfade ausserhalb erlaubter Roots werden blockiert.
- aktive SQLite-Datenbank bleibt blockiert.
- `.env` und Secrets bleiben blockiert.
- Obsidian Vault bleibt blockiert.
- globale Loeschaktion bleibt blockiert.
- unbekannte Bereiche bleiben ohne Future Gate blockiert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Loeschpfade.
- Keine neuen Exportpfade.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Cleanup Preview Model Readiness Gate`

Ziel: Pruefen und dokumentieren, dass das Preview-Modell isoliert bleibt und keine echten Cleanup-Aktionen ausfuehrt.
