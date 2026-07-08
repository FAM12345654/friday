# Review Batch Selection CLI Preview Readiness Gate

## Ziel

Dieses Gate prueft den read-only Preview-Renderer fuer spaetere Review-Batch-Auswahlen.

Der Renderer ist nur fuer deutsche Vorschau-Texte freigegeben. Er fuehrt keine Review-Aktion aus.

## Gepruefte Artefakte

| Artefakt | Ergebnis |
|---|---|
| `friday/app/review_batch_selection_parser.py` | vorhanden und side-effect-free |
| `friday/app/review_batch_selection_preview.py` | vorhanden und read-only |
| `friday/tests/test_review_batch_selection_parser.py` | vorhanden |
| `friday/tests/test_review_batch_selection_preview.py` | vorhanden |
| `friday/docs/REVIEW_BATCH_SELECTION_CLI_PREVIEW_PLAN.md` | vorhanden |
| `friday/docs/REVIEW_BATCH_SELECTION_CLI_PREVIEW_MODEL.md` | vorhanden |

## Abgenommene Preview-Faehigkeiten

| Verhalten | Status |
|---|---|
| ausgewaehlte sichtbare Vorschlaege anzeigen | abgenommen |
| `all` als alle sichtbaren Vorschlaege anzeigen | abgenommen |
| `none` als keine Auswahl anzeigen | abgenommen |
| `z` als Rueckkehrtext anzeigen | abgenommen |
| leere Eingabe stabil anzeigen | abgenommen |
| invalid Eingaben mit Standardmeldung anzeigen | abgenommen |
| fehlende sichtbare Vorschlaege stabil behandeln | abgenommen |
| String-IDs in sichtbaren Vorschlaegen fuer Preview akzeptieren | abgenommen |
| Safety-Hinweis in jeder Ausgabe anzeigen | abgenommen |

## Safety-Hinweis

Jede Preview enthaelt:

```text
Es wurde noch nichts freigegeben, abgelehnt oder gesendet.
```

## Safety-Grenzen

Der Preview-Renderer bleibt strikt begrenzt:

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

## Nicht freigegeben

Dieses Gate gibt weiterhin nicht frei:

- Batch-Freigabe von Nachrichten-Vorschlaegen,
- Batch-Ablehnung von Nachrichten-Vorschlaegen,
- Batch-Konvertierung von Aufgaben-Vorschlaegen,
- neue Review-Menueoptionen,
- echte Nachrichten,
- echte Kalendertermine,
- externe Provider,
- Datenbankschema-Aenderungen.

## Tests

Abgenommene Validierung:

```powershell
python -m pytest friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Keine Produktlogik nach dem Preview-Modell erweitert.
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

Der Review Batch Selection Preview-Renderer ist als read-only, side-effect-free Baustein abgenommen.

Er darf im naechsten Schritt geplant in den Review-Flow eingebettet werden, solange weiterhin nur eine Vorschau gezeigt wird und keine Batch-Aktionen ausgefuehrt werden.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection CLI Integration Plan**.

Ziel:

- planen, an welcher Stelle im Review-Menue die Batch-Preview sichtbar wird,
- keine Batch-Aktion ausfuehren,
- keine Statusaenderung,
- keine Persistenz,
- keine externen Aktionen.
