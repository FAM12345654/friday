# Review Batch Selection Parser Readiness Gate

## Ziel

Dieses Gate prueft den isolierten Review Batch Selection Parser nach dem Parser-Model-Step.

Der Parser ist nur fuer spaetere Batch-Auswahl-Vorbereitung freigegeben. Er fuehrt keine Review-Aktion aus.

## Gepruefte Artefakte

| Artefakt | Ergebnis |
|---|---|
| `friday/app/review_batch_selection_parser.py` | vorhanden und side-effect-free |
| `friday/tests/test_review_batch_selection_parser.py` | vorhanden und fokussiert |
| `friday/docs/REVIEW_BATCH_SELECTION_PARSER_PLAN.md` | vorhanden |
| `friday/docs/REVIEW_BATCH_SELECTION_PARSER_MODEL.md` | vorhanden |
| `friday/docs/cli_documentation_index_12l.md` | auf Parser-Model und Readiness-Gate aktualisiert |

## Abgenommene Parser-Faehigkeiten

| Verhalten | Status |
|---|---|
| konkrete sichtbare IDs parsen | abgenommen |
| Whitespace stabil behandeln | abgenommen |
| doppelte IDs deduplizieren | abgenommen |
| `all` erkennen | abgenommen |
| `none` erkennen | abgenommen |
| `z` als Ruecksprung erkennen | abgenommen |
| leere Eingabe als `empty` erkennen | abgenommen |
| unbekannte IDs ablehnen | abgenommen |
| negative/dezimale IDs ablehnen | abgenommen |
| Sonderzeichen ablehnen | abgenommen |
| Review-Actions wie `a`/`r` ablehnen | abgenommen |
| harte Tokens wie `JA`/`SPEICHERN` ablehnen | abgenommen |

## Safety-Grenzen

Der Parser bleibt strikt begrenzt:

- keine CLI-Anbindung,
- keine Batch-Aktion,
- keine Freigabe,
- keine Ablehnung,
- keine Task-Konvertierung,
- keine Statusaenderung,
- keine Datenbankoperation,
- keine externe Aktion,
- kein `input()`,
- kein `print()`.

## Safe Flags

Parser-Ergebnisse bleiben als sicherer Preview-Stand markiert:

- `preview_only = True`
- `persisted = False`
- `external_action_used = False`

## Tests

Abgenommene Validierung:

```powershell
python -m pytest friday/tests/test_review_batch_selection_parser.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Nicht freigegeben

Dieses Gate gibt weiterhin nicht frei:

- Batch-Freigabe von Nachrichten-Vorschlaegen,
- Batch-Ablehnung von Nachrichten-Vorschlaegen,
- Batch-Konvertierung von Aufgaben-Vorschlaegen,
- CLI-Menuefuehrung fuer Batch Review,
- echte Nachrichten,
- echte Kalendertermine,
- externe Provider,
- Datenbankschema-Aenderungen.

## Safety-Bewertung

- Keine Produktlogik nach dem Parser-Modell erweitert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine Persistenz.
- Safety-Flags unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Ergebnis

Der Review Batch Selection Parser ist als isoliertes, side-effect-free Modell abgenommen.

Er darf im naechsten Schritt geplant in einen Preview-/CLI-Kontext eingebettet werden, solange weiterhin keine Batch-Aktionen ausgefuehrt werden.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection CLI Preview Plan**.

Ziel:

- planen, wie der Parser spaeter im Review-Bereich sichtbar gemacht wird,
- nur Preview-Verhalten planen,
- keine Batch-Aktionen ausfuehren,
- keine Statusaenderungen,
- keine Persistenz,
- keine externen Aktionen.
