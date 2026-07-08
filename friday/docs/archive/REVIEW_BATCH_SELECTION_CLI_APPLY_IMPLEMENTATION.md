# Review Batch Selection CLI Apply Implementation

## Ziel

Dieser Step bindet das bestehende guarded Review-Batch-Apply-Modell lokal in den Review-CLI-Flow ein.

Die Implementierung bleibt bewusst local-only:

- keine echten Nachrichten,
- keine echten Kalendertermine,
- keine externen Provider,
- keine Datenbankschema-Aenderung,
- kein Auto-Approval.

## Geaenderte Bereiche

| Datei | Aenderung |
|---|---|
| `friday/app/interface.py` | Batch-Auswahl-Preview kann nach Safety Smoke, Guard und hartem Token lokale Batch-Aktionen ausfuehren |
| `friday/tests/test_interface_combined_review.py` | E2E-nahe CLI-Tests fuer erlaubte und blockierte Batch-Apply-Pfade |

## CLI-Ablauf

Der Review-Bereich nutzt weiterhin Option `5` fuer Batch-Auswahl.

Der Ablauf ist jetzt:

1. Offene Vorschlaege werden mit virtuellen IDs angezeigt.
2. Nutzer gibt eine Batch-Auswahl ein, z. B. `1`, `1,2`, `all`, `none` oder `z`.
3. Friday zeigt zuerst die Batch-Auswahl-Vorschau.
4. Nur bei `selected` oder `all` wird eine lokale Aktion angeboten.
5. Friday fuehrt Safety Smoke aus.
6. Friday zeigt den erforderlichen harten Token.
7. Nur bei exakt passendem Token gibt der Guard die Aktion frei.
8. Das Apply-Modell fuehrt ausschliesslich lokale Aenderungen aus.

## Lokale Aktionen

| Auswahl | Aktion | Token | Effekt |
|---|---|---|---|
| `1` | Nachrichten-Vorschlaege lokal freigeben | `BATCH FREIGEBEN` | Status lokal auf `approved`, kein Versand |
| `2` | Vorschlaege lokal ablehnen | `BATCH ABLEHNEN` | Status lokal auf `rejected` |
| `3` | Aufgaben lokal erstellen | `BATCH AUFGABEN ERSTELLEN` | lokale Aufgaben erstellen und Vorschlaege auf `converted` setzen |

## Blockierungen

Die Aktion wird blockiert, wenn:

- keine Preview gezeigt wurde,
- keine Auswahl vorhanden ist,
- IDs nicht sichtbar oder nicht pending sind,
- ein falscher Token eingegeben wird,
- Safety Smoke fehlschlaegt,
- externe Aktionen aktiviert waeren,
- eine Aktion nicht zum Vorschlagstyp passt,
- ein Aufgaben-Vorschlag bereits converted ist.

## Tests

Ergaenzte Tests pruefen:

- Nachrichten-Vorschlag wird mit `BATCH FREIGEBEN` lokal freigegeben.
- Falscher Token blockiert und Vorschlag bleibt pending.
- Aufgaben-Vorschlag wird mit `BATCH AUFGABEN ERSTELLEN` lokal als Aufgabe erstellt.
- Safety Smoke wird im Test stabil gemockt.
- Bestehende read-only Batch-Preview bleibt erhalten.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Guard und harter Token sind Pflicht vor lokalem Apply.
- Safety Smoke ist Pflicht vor lokalem Apply.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Batch Selection CLI Apply Readiness Gate**.

Ziel:

- neue CLI-Apply-Pfade final pruefen,
- Fokus-Tests und Full Regression bestaetigen,
- Safety-Grenzen dokumentieren,
- entscheiden, ob danach ein User-Guide-Update sinnvoll ist.
