# Review Activity Summary Model Readiness Gate

## Ziel

Dieses Gate nimmt das isolierte read-only Review Activity Summary Model ab.

Freigegeben wird nur die Modellschicht:

- keine CLI-Anbindung,
- keine Schreiboperation,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Gepruefte Artefakte

| Artefakt | Ergebnis |
|---|---|
| `friday/app/review_activity_summary.py` | Modell vorhanden |
| `friday/tests/test_review_activity_summary.py` | Fokus-Tests vorhanden |
| `friday/docs/REVIEW_ACTIVITY_SUMMARY_MODEL.md` | Modell-Doku vorhanden |
| `MessageSuggestionRepository.get_all_suggestions()` | als spaetere Datenquelle geeignet |
| `TaskSuggestionRepository.get_all_task_suggestions()` | als spaetere Datenquelle geeignet |

## Abgenommene Faehigkeiten

- Nachrichten-Vorschlaege werden nach Status gezaehlt.
- Aufgaben-Vorschlaege werden nach Status gezaehlt.
- `pending` und `edited` zaehlen als offen.
- Aufgaben-Vorschlaege mit `converted` werden separat gezaehlt.
- Gesetzte `created_task_id` werden fuer Aufgaben-Vorschlaege gezaehlt.
- Zuletzt geaenderte Vorschlaege werden nach `updated_at` sortiert.
- `recent_limit` begrenzt die Liste zuletzt geaenderter Vorschlaege.
- Ergebnis-Flags bleiben read-only:
  - `preview_only = True`,
  - `persisted = False`,
  - `external_action_used = False`.

## Safety-Grenzen

Das Modell darf:

- uebergebene lokale Vorschlagslisten lesen,
- Statuswerte zaehlen,
- strukturierte Summary-Daten zurueckgeben.

Das Modell darf nicht:

- SQLite direkt lesen,
- SQLite schreiben,
- Vorschlaege aendern,
- Aufgaben erstellen,
- Nachrichten senden,
- Kalendertermine erstellen,
- externe Dienste aufrufen,
- CLI-Eingaben lesen,
- direkt Ausgaben drucken.

## Nicht freigegeben

- Keine CLI-Anzeige.
- Keine Review-Menue-Erweiterung.
- Keine Exportfunktion.
- Kein Undo.
- Keine Statusaenderung.
- Keine Datenbankschema-Aenderung.

## Teststatus

Fokus-Tests:

```bash
python -m pytest friday/tests/test_review_activity_summary.py friday/tests/test_message_suggestion_repository.py friday/tests/test_task_suggestion_repository.py
```

Full Checks:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Gate-Ergebnis

Das Review Activity Summary Model ist als isolierter read-only Baustein bereit.

Eine CLI-Anbindung ist noch nicht freigegeben und muss separat geplant werden.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Activity Summary CLI Plan**.

Ziel:

- planen, wo die read-only Summary im Review-Menue angezeigt wird,
- Texte und Ruecksprungverhalten festlegen,
- Tests fuer spaetere CLI-Anbindung planen,
- keine CLI-Implementierung im Plan-Step.
