# Local Data Export CLI Approval Implementation

## Ziel

Dieser Schritt bindet den lokalen Datenexport kontrolliert an die CLI an.

Der Export bleibt hart gegated:

- Preview zuerst,
- Safety Smoke vor Token,
- exakter Token `DATEN EXPORTIEREN`,
- Guard-Pruefung,
- Writer nur unter `local_data/exports`.

## Umgesetzter CLI-Ablauf

Im Backup-/Restore-Menue nutzt Option `5` jetzt folgenden Ablauf:

1. Lokale Datenexport-Preview anzeigen.
2. Geplanten Zielordner anzeigen.
3. Ausgeschlossene Inhalte anzeigen.
4. Safety Smoke lokal ausfuehren.
5. Bei Safety Smoke FAIL abbrechen.
6. Harten Token abfragen.
7. Bei leerer Eingabe abbrechen.
8. Bei falschem Token Guard-Blockierung anzeigen.
9. Bei exakt `DATEN EXPORTIEREN` lokalen Export schreiben.

## Exportierte lokale Bereiche

Der CLI-Export uebergibt nur explizit zusammengestellte lokale Daten an den Writer:

- lokale Aufgaben,
- lokale Kontakt-Kontexte,
- lokale offene Review-/Task-Vorschlaege,
- lokaler Safety-Status.

Der Writer filtert Kontakt- und Review-Felder weiterhin.

## Nicht exportiert

Nicht exportiert werden:

- aktive SQLite-Datenbank als Rohdatei,
- `.env`,
- Secrets,
- API-Keys,
- Obsidian Vault,
- Cache-Dateien,
- volle private Roh-Nachrichtentexte,
- sensible Kontakt-Freitexte,
- externe Providerdaten.

## Tests

Ergaenzt wurden CLI-E2E-Tests fuer:

- Preview + Enter bricht ohne Export ab,
- falscher Token `JA` erstellt keinen Export,
- exakter Token `DATEN EXPORTIEREN` erstellt lokalen Export,
- Manifest und Aufgaben-Export werden geschrieben,
- rohe aktive Datenbank wird nicht exportiert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Keine Cloud.
- Keine echten Nachrichten.
- Keine echten Kalenderaktionen.
- Keine Datenbankschema-Aenderung.
- Export nur unter `local_data/exports`.
- Export nur nach Safety Smoke PASS.
- Export nur nach hartem Token `DATEN EXPORTIEREN`.
- Delete-Policy unveraendert.
- Safety-Flags unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export CLI Approval Readiness Gate` folgen.

Das Gate sollte pruefen:

- CLI-Export bleibt lokal,
- falsche Tokens schreiben nichts,
- Safety Smoke FAIL blockiert,
- Guard blockiert erwartbar,
- Exportdateien enthalten keine ausgeschlossenen Rohdaten,
- Full Regression und Safety Smoke bleiben gruen.
