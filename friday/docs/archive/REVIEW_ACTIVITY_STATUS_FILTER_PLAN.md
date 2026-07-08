# Review Activity Status Filter Plan

## Ziel

Dieser Schritt plant einen lokalen read-only Statusfilter fuer Review-Aktivitaet in Friday.

Der Filter soll vorhandene lokale Review-Detail-Eintraege nach Status anzeigen, ohne Vorschlaege zu veraendern, Aufgaben zu erstellen, Dateien zu schreiben oder externe Aktionen auszufuehren.

## Erlaubte Filterwerte

| Filter | Bedeutung |
|---|---|
| `all` | Alle lokalen Review-Detail-Eintraege |
| `open` | Offene Eintraege, aktuell `pending` und `edited` |
| `pending` | Nur pending Eintraege |
| `edited` | Nur edited Eintraege |
| `approved` | Lokal freigegebene Nachrichten-Vorschlaege |
| `rejected` | Lokal abgelehnte Vorschlaege |
| `converted` | In lokale Aufgaben umgewandelte Aufgaben-Vorschlaege |

## Nicht-Ziele

- Keine Statusaenderung.
- Keine Freigabe oder Ablehnung.
- Keine Batch-Aktion.
- Keine Aufgabe erstellen.
- Kein Export.
- Keine Datei-Schreiboperation.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.

## Safety-Bewertung

- Planung bleibt local-only.
- Geplanter Filter bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Status Filter Model.
