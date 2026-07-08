# Review Batch Selection CLI Preview Implementation Readiness Gate

## Ziel

Dieses Gate prueft die read-only CLI-Anbindung der Review-Batch-Auswahlpreview.

Der angebundene CLI-Pfad ist nur fuer Vorschau freigegeben. Er fuehrt weiterhin keine Batch-Aktion aus.

## Gepruefte Artefakte

| Artefakt | Ergebnis |
|---|---|
| `friday/app/review_batch_selection_parser.py` | vorhanden und side-effect-free |
| `friday/app/review_batch_selection_preview.py` | vorhanden und read-only |
| `friday/app/interface.py` | Batch-Preview im Review-Bereich read-only angebunden |
| `friday/tests/test_review_batch_selection_parser.py` | vorhanden |
| `friday/tests/test_review_batch_selection_preview.py` | vorhanden |
| `friday/tests/test_interface_combined_review.py` | um Batch-Preview-Tests erweitert |
| `friday/docs/REVIEW_BATCH_SELECTION_CLI_PREVIEW_IMPLEMENTATION.md` | vorhanden |

## Abgenommener Nutzerpfad

```text
Hauptmenue -> 6. Vorschlaege pruefen / freigeben -> 5. Batch-Auswahl als Vorschau anzeigen
```

Der Pfad zeigt nur eine Auswahl-Vorschau.

## Abgenommene CLI-Faehigkeiten

| Verhalten | Status |
|---|---|
| Review-Uebersicht zeigt Batch-Preview-Option | abgenommen |
| Batch-Preview nutzt sichtbare pending Nachrichten-Vorschlaege | abgenommen |
| Batch-Preview nutzt sichtbare pending Aufgaben-Vorschlaege | abgenommen |
| virtuelle sichtbare IDs verhindern ID-Kollisionen | abgenommen |
| `1,2` zeigt ausgewaehlte sichtbare Vorschlaege | abgenommen |
| invalid ID zeigt Standardmeldung | abgenommen |
| Safety-Hinweis wird angezeigt | abgenommen |
| Vorschlaege bleiben pending | abgenommen |
| keine lokale Aufgabe wird erstellt | abgenommen |

## Safety-Hinweis

Die Batch-Preview zeigt weiterhin:

```text
Es wurde noch nichts freigegeben, abgelehnt oder gesendet.
```

## Read-only-Grenzen

Der angebundene CLI-Pfad darf:

- pending Vorschlaege lokal lesen,
- virtuelle sichtbare IDs erzeugen,
- den Parser aufrufen,
- den Preview-Renderer aufrufen,
- deutschen Vorschau-Text anzeigen,
- zur Review-Uebersicht zurueckkehren.

Der angebundene CLI-Pfad darf nicht:

- Vorschlaege freigeben,
- Vorschlaege ablehnen,
- Aufgaben-Vorschlaege konvertieren,
- lokale Aufgaben erstellen,
- Nachrichten senden,
- Kalendertermine erstellen,
- DB-Status aendern,
- externe Dienste aufrufen.

## Tests

Abgenommene Validierung:

```powershell
python -m pytest friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py friday/tests/test_interface_combined_review.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Nicht freigegeben

Dieses Gate gibt weiterhin nicht frei:

- Batch-Freigabe,
- Batch-Ablehnung,
- Batch-Konvertierung von Aufgaben-Vorschlaegen,
- echte Nachrichten,
- echte Kalendertermine,
- externe Provider,
- Datenbankschema-Aenderungen,
- neue Standing Approvals.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine Batch-Apply-Funktion.
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

Die Review Batch Selection CLI Preview ist als read-only Produktpfad abgenommen.

Der Review-Bereich kann Batch-Auswahlen sichtbar vorschauen, ohne Vorschlaege zu veraendern oder externe Aktionen auszuloesen.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Apply Policy Plan**.

Ziel:

- planen, ob und wie spaetere Batch-Aktionen ueberhaupt erlaubt werden duerfen,
- harte Safety-Grenzen fuer Approve/Reject/Convert definieren,
- keine Batch-Aktion implementieren,
- keine Statusaenderung,
- keine externen Aktionen.
