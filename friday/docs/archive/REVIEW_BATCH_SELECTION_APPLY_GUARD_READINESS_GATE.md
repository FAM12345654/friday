# Review Batch Selection Apply Guard Readiness Gate

## Ziel

Dieses Gate prueft das isolierte Review Batch Selection Apply Guard Model.

Der Guard ist nur als side-effect-free Sicherheitspruefung freigegeben. Er fuehrt keine Batch-Aktion aus.

## Gepruefte Artefakte

| Artefakt | Ergebnis |
|---|---|
| `friday/app/review_batch_apply_guard.py` | vorhanden und side-effect-free |
| `friday/tests/test_review_batch_apply_guard.py` | vorhanden und fokussiert |
| `friday/docs/REVIEW_BATCH_SELECTION_APPLY_POLICY_PLAN.md` | vorhanden |
| `friday/docs/REVIEW_BATCH_SELECTION_APPLY_GUARD_PLAN.md` | vorhanden |
| `friday/docs/REVIEW_BATCH_SELECTION_APPLY_GUARD_MODEL.md` | vorhanden |

## Abgenommene Guard-Faehigkeiten

| Verhalten | Status |
|---|---|
| erlaubte lokale Action Types pruefen | abgenommen |
| harte Tokens pro Action Type pruefen | abgenommen |
| `JA`, `SPEICHERN` und einfache Actions blockieren | abgenommen |
| fehlende Preview blockieren | abgenommen |
| fehlende Auswahl blockieren | abgenommen |
| nicht sichtbare IDs blockieren | abgenommen |
| nicht pending IDs blockieren | abgenommen |
| gemischte Typen fuer Message-Approval blockieren | abgenommen |
| gemischte Typen fuer Task-Creation blockieren | abgenommen |
| bereits verarbeitete Vorschlaege blockieren | abgenommen |
| Safety-Smoke-Fehler blockieren | abgenommen |
| aktivierte externe Aktionen blockieren | abgenommen |
| verbotene Action Types blockieren | abgenommen |
| IDs deduplizieren | abgenommen |
| Safe Flags setzen | abgenommen |

## Safe Flags

Jedes Guard-Ergebnis enthaelt:

- `preview_only = True`
- `persisted = False`
- `external_action_used = False`

## Safety-Grenzen

Der Guard darf:

- Action Type pruefen,
- harte Tokens pruefen,
- sichtbare pending IDs pruefen,
- Safety-Smoke-Status pruefen,
- externe Aktionsflags pruefen,
- Blockgruende zurueckgeben.

Der Guard darf nicht:

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
python -m pytest friday/tests/test_review_batch_apply_guard.py friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py friday/tests/test_interface_combined_review.py
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

Das Review Batch Selection Apply Guard Model ist als isolierter Sicherheitswaechter abgenommen.

Es darf in einem spaeteren Apply-Modell genutzt werden, solange der Apply-Step getrennt geplant, getestet und weiterhin lokal-only gehalten wird.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Apply Model Plan**.

Ziel:

- planen, wie ein spaeteres lokales Batch-Apply-Modell aussehen darf,
- Guard-Pflicht vor jeder Aktion definieren,
- keine Batch-Aktion implementieren,
- keine CLI-Anbindung,
- keine externen Aktionen.
