# Privacy Data Management CLI Read-Only Implementation

## Ziel

Dieser Schritt bindet das Privacy Data Management Inventory read-only in das bestehende Privacy Dashboard ein.

Die Anzeige bleibt rein informativ:

- keine Loeschfunktion,
- keine Exportfunktion,
- keine Importfunktion,
- keine Restore-Funktion,
- keine externe Aktion,
- keine Datenbankschema-Aenderung.

## Umsetzung

Geaenderte Dateien:

- `friday/app/menu.py`
- `friday/app/interface.py`
- `friday/tests/test_menu.py`
- `friday/tests/test_interface_main_menu_e2e.py`

Neue Dokumentation:

- `friday/docs/PRIVACY_DATA_MANAGEMENT_CLI_READ_ONLY_IMPLEMENTATION.md`

## CLI-Verhalten

Das Privacy Dashboard hat jetzt einen zusaetzlichen read-only Menuepunkt:

| Menuepunkt | Funktion | Schreibt Daten? |
|---|---|---|
| `6` | Privacy Data Management Inventory anzeigen | Nein |
| `7` | Zurueck zum Hauptmenue | Nein |

Die Anzeige listet:

- lokale Datenbereiche,
- Speicherart,
- Pfad,
- Sichtbarkeit,
- aktueller Zugriff,
- spaetere Pflegeidee,
- Safety-Grenze,
- Count-Label,
- blockierte riskante Aktionen.

## Abgesicherte Safety-Grenzen

- Das Inventory wird nur angezeigt.
- Es werden keine Dateien erstellt.
- Es werden keine Daten geloescht.
- Es werden keine Daten exportiert.
- Es werden keine Daten importiert.
- Es wird keine Datenbankstruktur geaendert.
- Es werden keine externen Dienste genutzt.
- Sensitive Details werden nicht angezeigt.

## Tests

Ergaenzte Tests pruefen:

- Privacy Dashboard Menueoptionen enthalten den neuen Inventory-Punkt.
- Bestehende Privacy Dashboard Untermenues bleiben erreichbar.
- Rueckkehr erfolgt jetzt ueber `7`.
- Inventory-Ausgabe enthaelt lokale Bereiche und blockierte Aktionen.
- Run-Loop mit Privacy Dashboard und Exit bleibt stabil.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine Loeschfunktion.
- Keine Exportfunktion.
- Keine Importfunktion.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Data Management CLI Read-Only Readiness Gate`

Ziel: Pruefen und dokumentieren, dass die neue CLI-Anzeige weiterhin read-only bleibt und keine Datenpflege-Aktionen freischaltet.
