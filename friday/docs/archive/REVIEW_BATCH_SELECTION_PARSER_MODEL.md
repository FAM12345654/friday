# Review Batch Selection Parser Model

## Ziel

Dieses Dokument beschreibt das isolierte Parser-Modell fuer spaetere Batch-Auswahlen im lokalen Review-Flow.

Der Step baut nur side-effect-free Parser-Logik:

- keine CLI-Anbindung,
- keine Review-Aktion,
- keine Statusaenderung,
- keine Datenbankoperation,
- keine externen Aktionen.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/review_batch_selection_parser.py` | Reiner Parser fuer Batch-Auswahl-Eingaben |
| `friday/tests/test_review_batch_selection_parser.py` | Unit-Tests fuer gueltige, leere und ungueltige Eingaben |

## Parser-Verhalten

| Eingabe | Ergebnis |
|---|---|
| `1,2,3` | `selected` mit sichtbaren IDs |
| `1, 2 , 3` | `selected`, Whitespace tolerant |
| doppelte IDs | dedupliziert, Reihenfolge der ersten Nennung bleibt erhalten |
| `all` | `all` mit allen sichtbaren IDs |
| `none` | `none` ohne Auswahl |
| `z` | `back` |
| leer / `None` | `empty` |
| unbekannte IDs | `invalid` |
| negative/dezimale IDs | `invalid` |
| Sonderzeichen | `invalid` |
| Review-Actions wie `a` oder `r` | `invalid` |
| harte Tokens wie `JA` oder `SPEICHERN` | `invalid` |

## Sicherheitsgrenze

Der Parser akzeptiert nur IDs, die als `visible_ids` uebergeben werden.

Damit koennen spaetere Review-Flows verhindern, dass unsichtbare, alte oder fremde Vorschlaege per Batch ausgewaehlt werden.

## Safe Flags

Jedes Parser-Ergebnis enthaelt:

- `preview_only = True`
- `persisted = False`
- `external_action_used = False`

## Nicht umgesetzt

Dieser Step baut bewusst nicht:

- keine CLI-Menueoption,
- keine Batch-Freigabe,
- keine Batch-Ablehnung,
- keine Task-Konvertierung,
- keine Datenbankmigration,
- keine externen Integrationen.

## Tests

Fokussierte Tests pruefen:

- konkrete ID-Auswahl,
- Whitespace,
- Deduplizierung,
- `all`, `none`, `z`, leer und `None`,
- ungueltige IDs und Sonderzeichen,
- Ablehnung von Review-Actions und harten Approval-Tokens,
- Safe Flags,
- Ergebnis-Datentyp.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine CLI-Anbindung.
- Keine Persistenz.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Parser Readiness Gate**.

Ziel:

- Parser-Modell pruefen,
- Safety-Grenzen dokumentieren,
- Tests und Scanner-Smoke bestaetigen,
- keine CLI-Anbindung bauen.
