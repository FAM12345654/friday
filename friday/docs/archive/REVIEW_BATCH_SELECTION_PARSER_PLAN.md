# Review Batch Selection Parser Plan

## Ziel

Dieses Dokument plant einen isolierten Parser fuer spaetere Batch-Auswahlen im lokalen Review-Flow.

Der Schritt ist bewusst planend:

- keine Produktlogik-Aenderung,
- keine neue CLI-Anbindung,
- keine Review-Aktion,
- keine Statusaenderung an Vorschlaegen,
- keine Datenbankoperation,
- keine externen Aktionen.

## Ausgangslage

Friday kann Nachrichten- und Aufgaben-Vorschlaege lokal einzeln pruefen. Fuer spaetere produktivere Review-Flows soll zuerst sicher geplant werden, wie mehrere sichtbare Vorschlaege ausgewaehlt werden koennen.

Der Parser soll spaeter nur Eingaben interpretieren. Er darf keine Aktionen ausfuehren.

## Geplante Eingaben

| Eingabe | Bedeutung |
|---|---|
| `1,2,3` | konkrete sichtbare Vorschlags-IDs auswaehlen |
| `1, 2, 3` | wie oben, Whitespace wird toleriert |
| `all` | alle sichtbaren Vorschlaege auswaehlen |
| `none` | keine Vorschlaege auswaehlen |
| `z` | Ruecksprung / Abbruch |
| leer | keine Auswahl oder Rueckkehr, je nach spaeterem UI-Kontext |
| andere Eingabe | invalid |

## Geplantes Ergebnis-Modell

Ein spaeteres Parser-Modell kann ein Ergebnis mit klaren Statuswerten liefern:

```text
selected
all
none
back
empty
invalid
```

Moegliche Felder:

```text
status
selected_ids
invalid_tokens
message
```

## Parser-Regeln

- Eingabe wird mit `strip()` normalisiert.
- `z` bleibt Ruecksprung.
- `all` und `none` sind eigene Statuswerte.
- Kommagetrennte Zahlen werden als ID-Liste gelesen.
- Doppelte IDs werden dedupliziert oder als kontrollierter Fehler dokumentiert.
- Negative Zahlen sind invalid.
- Dezimalzahlen sind invalid.
- Sonderzeichen sind invalid.
- IDs, die nicht in der sichtbaren Vorschlagsliste enthalten sind, sind invalid.
- Der Parser akzeptiert keine freien Aktionen wie `a`, `r`, `JA` oder `SPEICHERN`.

## Sichtbare Vorschlaege als Sicherheitsgrenze

Der Parser darf nur IDs akzeptieren, die ihm als sichtbare Vorschlags-IDs uebergeben werden.

Beispiel:

```text
visible_ids = [1, 2, 3]
input = "1,4"
```

Erwartung:

```text
invalid, weil 4 nicht sichtbar ist
```

Dadurch kann ein Nutzer nicht versehentlich versteckte oder alte Vorschlaege per Batch auswaehlen.

## Nicht-Ziele

Dieser Plan baut noch nicht:

- keine Parser-Datei,
- keine Tests,
- keine CLI-Anbindung,
- keine Batch-Aktion,
- keine Approve-/Reject-/Convert-Logik,
- keine neue Persistenz,
- keine Datenbankschema-Aenderung,
- keine externen Integrationen.

## Vorgeschlagene spaetere Datei

```text
friday/app/review_batch_selection_parser.py
```

## Vorgeschlagene spaetere Tests

```text
friday/tests/test_review_batch_selection_parser.py
```

Testziele fuer den spaeteren Model-Step:

- `1,2,3` liefert `selected` mit `[1, 2, 3]`.
- Whitespace wird stabil verarbeitet.
- `all` liefert `all`.
- `none` liefert `none`.
- `z` liefert `back`.
- leere Eingabe liefert `empty`.
- Sonderzeichen liefern `invalid`.
- unbekannte IDs liefern `invalid`.
- negative und dezimale IDs liefern `invalid`.
- Parser hat keine Seiteneffekte.
- Parser nutzt kein `input()` und kein `print()`.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Batch-Aktionen ausgefuehrt.
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

Naechster Build Step: **Review Batch Selection Parser Model**.

Ziel:

- isolierten Parser in Python bauen,
- fokussierte Unit-Tests ergaenzen,
- keine CLI-Anbindung,
- keine Review-Aktionen,
- keine Persistenz,
- keine externen Aktionen.
