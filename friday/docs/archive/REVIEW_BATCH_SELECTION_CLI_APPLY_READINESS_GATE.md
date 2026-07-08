# Review Batch Selection CLI Apply Readiness Gate

## Ziel

Dieses Gate nimmt die lokale Review-Batch-CLI-Apply-Implementierung ab.

Der Review-Bereich kann nun nach einer Batch-Auswahl und Vorschau lokale Batch-Aktionen ausfuehren, aber nur nach:

- sichtbarer Preview,
- Safety Smoke,
- Apply Guard,
- hartem Token.

## Gepruefte Artefakte

| Artefakt | Ergebnis |
|---|---|
| `friday/app/interface.py` | CLI-Apply-Pfad fuer Review-Batch-Auswahl vorhanden |
| `friday/app/review_batch_selection_parser.py` | Parser fuer Batch-Auswahl vorhanden |
| `friday/app/review_batch_selection_preview.py` | Preview-Renderer vorhanden |
| `friday/app/review_batch_apply_guard.py` | Guard mit harten Tokens vorhanden |
| `friday/app/review_batch_apply_model.py` | Lokales Apply-Modell vorhanden |
| `friday/tests/test_interface_combined_review.py` | CLI-Fokus-Tests fuer Batch-Apply vorhanden |
| `friday/docs/REVIEW_BATCH_SELECTION_CLI_APPLY_IMPLEMENTATION.md` | Implementierung dokumentiert |

## Abgenommene CLI-Faehigkeiten

- Review-Option `5` zeigt weiterhin zuerst eine Batch-Auswahl-Vorschau.
- Nur bei gueltiger Auswahl wird eine lokale Batch-Aktion angeboten.
- Nachrichten-Vorschlaege koennen lokal freigegeben werden.
- Nachrichten- und Aufgaben-Vorschlaege koennen lokal abgelehnt werden.
- Aufgaben-Vorschlaege koennen lokal in Aufgaben umgewandelt werden.
- Falscher Token blockiert die Aktion und Vorschlaege bleiben pending.
- Safety Smoke ist Pflicht vor Apply.
- Apply Guard ist Pflicht vor Apply.

## Harte Tokens

| Aktion | Token |
|---|---|
| Nachrichten-Vorschlaege lokal freigeben | `BATCH FREIGEBEN` |
| Vorschlaege lokal ablehnen | `BATCH ABLEHNEN` |
| Aufgaben lokal erstellen | `BATCH AUFGABEN ERSTELLEN` |

## Nicht freigegeben

- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine externen Provider.
- Keine Netzwerkaktionen.
- Keine Auto-Approval-Logik.
- Keine Standing Approvals.
- Keine Datenbankschema-Aenderung.

## Teststatus

Fokus-Tests:

```bash
python -m pytest friday/tests/test_interface_combined_review.py friday/tests/test_review_batch_apply_guard.py friday/tests/test_review_batch_apply_model.py friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py
```

Ergebnis:

```text
79 passed
```

Full Regression:

```bash
python -m pytest friday/tests
```

Ergebnis:

```text
832 passed
```

Weitere Checks:

```bash
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

Ergebnis:

- Compilecheck erfolgreich.
- Safety Smoke: `Overall: PASS`.
- Diff-Check sauber.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Guard und harte Tokens sind Pflicht.
- Safety Smoke ist Pflicht.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Gate-Ergebnis

Die lokale Review-Batch-CLI-Apply-Implementierung ist abgenommen.

Freigegeben ist nur lokales Review-Batch-Apply fuer bestehende lokale Vorschlaege und lokale Aufgaben-Erstellung. Externe Aktionen bleiben deaktiviert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Batch Selection User Guide Integration**.

Ziel:

- Nutzer-Doku fuer Batch-Auswahl im Review-Bereich ergaenzen,
- harte Tokens dokumentieren,
- lokale Safety-Grenzen klar erklaeren,
- keine neue Produktlogik.
