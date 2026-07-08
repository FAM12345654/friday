# Review Batch Selection CLI Preview Model

## Ziel

Dieses Dokument beschreibt den reinen Preview-Renderer fuer spaetere Review-Batch-Auswahlen.

Der Step baut nur deutsche Vorschau-Texte:

- keine CLI-Anbindung,
- keine Batch-Aktion,
- keine Statusaenderung,
- keine Datenbankoperation,
- keine externen Aktionen.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/review_batch_selection_preview.py` | Read-only Preview-Renderer fuer Parser-Ergebnisse und sichtbare Vorschlaege |
| `friday/tests/test_review_batch_selection_preview.py` | Unit-Tests fuer Preview-Texte und Safety-Hinweis |

## Preview-Verhalten

Der Renderer verarbeitet ein `ReviewBatchSelectionParseResult` und eine Liste sichtbarer Vorschlaege.

| Parser-Status | Preview |
|---|---|
| `selected` | zeigt nur die ausgewaehlten sichtbaren Vorschlaege |
| `all` | zeigt alle sichtbaren Vorschlaege |
| `none` | zeigt, dass keine Vorschlaege ausgewaehlt wurden |
| `back` | zeigt Rueckkehr zum Review-Bereich |
| `empty` | zeigt, dass keine Batch-Auswahl eingegeben wurde |
| `invalid` | zeigt die Standardmeldung `Ungültige Auswahl. Bitte erneut versuchen.` |

Jede Ausgabe enthaelt den Safety-Hinweis:

```text
Es wurde noch nichts freigegeben, abgelehnt oder gesendet.
```

## Sicherheitsgrenzen

Der Preview-Renderer darf:

- Parser-Ergebnisse lesen,
- sichtbare Vorschlaege in Text umwandeln,
- einen deutschen Preview-Text zurueckgeben.

Der Preview-Renderer darf nicht:

- `input()` nutzen,
- `print()` nutzen,
- Vorschlaege freigeben,
- Vorschlaege ablehnen,
- Aufgaben-Vorschlaege konvertieren,
- Nachrichten senden,
- Kalendertermine erstellen,
- DB-Status aendern,
- externe Dienste nutzen.

## Tests

Die Tests pruefen:

- ausgewaehlte IDs werden angezeigt,
- `all` zeigt alle sichtbaren Vorschlaege,
- `none`, `z`, leer und invalid bleiben read-only,
- Standard-Fehlermeldung bleibt konsistent,
- fehlende sichtbare Vorschlaege werden stabil behandelt,
- String-IDs werden fuer die Preview akzeptiert,
- jede Ausgabe enthaelt den Safety-Hinweis.

## Nicht umgesetzt

Dieser Step baut bewusst nicht:

- keine CLI-Methode,
- keine Menueoption,
- keine Batch-Freigabe,
- keine Batch-Ablehnung,
- keine Task-Konvertierung,
- keine Persistenz,
- keine Datenbankschema-Aenderung.

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

Naechster Build Step: **Review Batch Selection CLI Preview Readiness Gate**.

Ziel:

- Preview-Renderer pruefen,
- Tests und Safety Smoke bestaetigen,
- dokumentieren, dass weiterhin keine CLI-Anbindung und keine Batch-Aktion freigegeben ist.
