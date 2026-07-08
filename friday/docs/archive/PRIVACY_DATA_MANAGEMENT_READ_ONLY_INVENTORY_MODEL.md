# Privacy Data Management Read-Only Inventory Model

## Ziel

Dieser Schritt setzt ein isoliertes read-only Inventory-Modell fuer spaetere lokale Privacy-Datenpflege um.

Das Modell beschreibt nur:

- lokale Datenbereiche,
- relevante lokale Pfade,
- sichtbare Zusammenfassungen,
- spaetere Pflegeideen,
- blockierte riskante Aktionen,
- Safety-Grenzen.

## Umsetzung

Neue Datei:

- `friday/app/privacy_data_management.py`

Neue Tests:

- `friday/tests/test_privacy_data_management.py`

Das Modell erzeugt ein `PrivacyDataManagementInventory` mit:

- `areas`: lokale Datenbereiche,
- `blocked_actions`: bewusst blockierte Aktionen,
- `writes_performed = False`,
- `deletes_performed = False`,
- `exports_performed = False`,
- `external_lookup_used = False`.

## Abgedeckte Datenbereiche

| Bereich | Status |
|---|---|
| Aufgaben | read-only inventarisiert |
| Kontakt-Kontexte | read-only inventarisiert |
| Review-Vorschlaege | read-only inventarisiert |
| Exporte | read-only inventarisiert |
| Backups | read-only inventarisiert |
| Restore-Kopien | read-only inventarisiert |
| Import-Reviews | read-only inventarisiert |
| Obsidian-Previews/Writes | read-only inventarisiert |
| Safety-Scanner | read-only inventarisiert |

## Bewusst blockierte Aktionen

- Datenbereich direkt loeschen.
- Aktive SQLite-Datenbank ersetzen.
- Secrets oder `.env` exportieren.
- Obsidian Vault scannen.
- Externe Provider pruefen.

## Safety-Bewertung

- Keine CLI-Anbindung.
- Keine Dateioperation.
- Keine Datenbankabfrage.
- Keine Datenbankschema-Aenderung.
- Keine Loeschfunktion.
- Keine Exportfunktion.
- Keine externe Aktion.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Tests

Die Tests pruefen:

- Inventory bleibt read-only.
- Es werden keine lokalen Pfade erstellt.
- Erwartete Datenbereiche sind vorhanden.
- Sensitive Details bleiben verborgen.
- Keine Management-Writes oder Management-Deletes sind freigegeben.
- Zusammenfassungszahlen koennen explizit uebergeben werden.
- Riskante Aktionen bleiben blockiert.
- Lokale Pfade koennen fuer Tests ueberschrieben werden.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Data Management Readiness Gate`

Ziel: Pruefen und dokumentieren, dass das Inventory-Modell isoliert bleibt und nicht an CLI, Datenbank, Export, Delete oder externe Aktionen angebunden ist.
