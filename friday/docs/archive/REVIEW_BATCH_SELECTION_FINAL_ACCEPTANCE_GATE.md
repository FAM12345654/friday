# Review Batch Selection Final Acceptance Gate

## Ziel

Dieses Gate nimmt den gesamten lokalen Review-Batch-Selection-Block final ab.

Der Block umfasst:

- Parser fuer Batch-Auswahl,
- read-only Preview,
- CLI-Preview-Integration,
- Apply-Policy,
- Apply-Guard,
- Apply-Modell,
- CLI-Apply-Integration,
- Nutzer-Doku,
- Tests und Safety Checks.

## Gepruefte Artefakte

| Artefakt | Status |
|---|---|
| `friday/app/review_batch_selection_parser.py` | umgesetzt |
| `friday/app/review_batch_selection_preview.py` | umgesetzt |
| `friday/app/review_batch_apply_guard.py` | umgesetzt |
| `friday/app/review_batch_apply_model.py` | umgesetzt |
| `friday/app/interface.py` | Review-Batch-Preview und guarded Apply angebunden |
| `friday/tests/test_review_batch_selection_parser.py` | gruen |
| `friday/tests/test_review_batch_selection_preview.py` | gruen |
| `friday/tests/test_review_batch_apply_guard.py` | gruen |
| `friday/tests/test_review_batch_apply_model.py` | gruen |
| `friday/tests/test_interface_combined_review.py` | gruen |
| `friday/docs/README_USER.md` | Nutzer-Doku aktualisiert |

## Final abgenommene Funktionen

- Batch-Auswahl im Review-Bereich ueber Bereich `5`.
- Auswahl per `1`, `1,2,3`, `all`, `none` oder `z`.
- Vorschau wird immer vor Apply angezeigt.
- Batch-Apply ist nur nach Safety Smoke, Guard und hartem Token moeglich.
- Nachrichten-Vorschlaege koennen lokal freigegeben werden.
- Nachrichten- und Aufgaben-Vorschlaege koennen lokal abgelehnt werden.
- Aufgaben-Vorschlaege koennen lokal in Aufgaben umgewandelt werden.
- Falsche Tokens blockieren ohne Statusaenderung.
- Stale oder nicht passende Vorschlaege werden vom Guard/Apply-Modell blockiert.

## Harte Tokens

| Aktion | Token |
|---|---|
| Nachrichten-Vorschlaege lokal freigeben | `BATCH FREIGEBEN` |
| Vorschlaege lokal ablehnen | `BATCH ABLEHNEN` |
| Aufgaben lokal erstellen | `BATCH AUFGABEN ERSTELLEN` |

## Safety-Grenzen

Freigegeben ist nur lokales Arbeiten mit bestehenden lokalen Vorschlaegen.

Nicht freigegeben:

- echte Nachrichten senden,
- echte Kalendertermine erstellen,
- externe Provider aufrufen,
- Netzwerkaktionen,
- Auto-Approval,
- Standing Approval fuer Review-Batches,
- Datenbankschema-Aenderungen.

## Teststatus

Fokus-Tests:

```bash
python -m pytest friday/tests/test_interface_combined_review.py
python -m pytest friday/tests/test_review_batch_apply_guard.py friday/tests/test_review_batch_apply_model.py
python -m pytest friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py
```

Full Regression:

```bash
python -m pytest friday/tests
```

Weitere Checks:

```bash
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Final Gate Ergebnis

Der Review-Batch-Selection-Block ist final abgenommen.

Friday kann lokale Review-Batches sicher auswaehlen, anzeigen und nach harten Tokens lokal anwenden. Externe Aktionen bleiben deaktiviert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Next Local Product Feature Planning after Review Batch**.

Ziel:

- naechstes kleines lokales Produktfeature planen,
- vorhandene Safety- und Testbasis beruecksichtigen,
- keine sofortige Implementierung ohne Plan.
