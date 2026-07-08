# Review Batch Selection Apply Model Readiness Gate

## Ziel

Dieses Gate prueft den aktuellen Stand des guarded lokalen Review-Batch-Apply-Modells.

Der Stand wird nur als isolierter lokaler Baustein freigegeben:

- keine CLI-Apply-Option,
- keine externen Aktionen,
- keine echten Nachrichten,
- keine echten Kalendertermine,
- keine Datenbankschema-Aenderung.

## Gepruefte Artefakte

| Artefakt | Ergebnis |
|---|---|
| `friday/app/review_batch_apply_guard.py` | Guard-Pflicht fuer Batch-Aktionen vorhanden |
| `friday/app/review_batch_apply_model.py` | Lokales Apply-Modell mit Guard-Pflicht vorhanden |
| `friday/tests/test_review_batch_apply_guard.py` | Guard-Fokus-Tests vorhanden |
| `friday/tests/test_review_batch_apply_model.py` | Apply-Modell-Fokus-Tests vorhanden |
| `friday/docs/REVIEW_BATCH_SELECTION_APPLY_MODEL.md` | Modell-Dokumentation vorhanden |

## Abgenommene Faehigkeiten

- Guard-Block verhindert lokale Aenderungen.
- Nachrichten-Vorschlaege koennen lokal auf `approved` gesetzt werden, ohne Versand.
- Nachrichten- und Aufgaben-Vorschlaege koennen lokal auf `rejected` gesetzt werden.
- Aufgaben-Vorschlaege koennen lokal in Aufgaben umgewandelt und auf `converted` gesetzt werden.
- Fehlender `TaskAgent` blockiert Task-Erstellung.
- Bereits konvertierte Aufgaben-Vorschlaege erzeugen keine Duplikate.
- Fehlende sichtbare Items blockieren das Apply.
- Ergebnis-Flags bleiben sicher:
  - `preview_only = False` nur bei ausgefuehrtem lokalem Apply,
  - `persisted = True` nur fuer lokale SQLite-Aenderungen,
  - `external_action_used = False` immer.

## Safety-Grenzen

Das Apply-Modell darf:

- lokale Vorschlagsstatus aendern,
- lokale Aufgaben aus Aufgaben-Vorschlaegen erstellen,
- lokale `created_task_id`-Werte setzen.

Das Apply-Modell darf nicht:

- CLI-Eingaben lesen,
- direkt Ausgaben drucken,
- echte Nachrichten senden,
- echte Kalendertermine erstellen,
- externe Dienste oder Provider aufrufen,
- Safety-Flags veraendern,
- Datenbankschema aendern,
- Standing Approvals einfuehren.

## Nicht freigegeben

- Keine CLI-Apply-Option.
- Keine Batch-Sendeaktion.
- Keine Kalenderaktion.
- Keine externen Integrationen.
- Keine Auto-Approval-Logik.
- Kein In-Place-Import oder Restore.

## Teststatus

Auszufuehrende Checks fuer dieses Gate:

```bash
python -m pytest friday/tests/test_review_batch_apply_model.py friday/tests/test_review_batch_apply_guard.py
python -m pytest friday/tests/test_review_batch_selection_parser.py friday/tests/test_review_batch_selection_preview.py friday/tests/test_interface_combined_review.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Gate-Ergebnis

Das guarded lokale Review-Batch-Apply-Modell ist als isolierter lokaler Baustein bereit.

Freigegeben ist nur die lokale Modellschicht. Eine CLI-Anbindung fuer Batch-Apply ist noch nicht freigegeben und muss separat geplant werden.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Batch Selection CLI Apply Plan**.

Ziel:

- planen, wie das guarded Apply-Modell spaeter sicher im Review-CLI sichtbar wird,
- harte Tokens und Safety Smoke fuer CLI-Apply definieren,
- keine CLI-Implementierung in diesem Plan-Schritt,
- keine externen Aktionen.
