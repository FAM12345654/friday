# Review Activity Summary Model

## Ziel

Dieses Dokument beschreibt das isolierte read-only Modell fuer die lokale Review-Aktivitaetsuebersicht.

Der Step baut nur eine Modellfunktion:

- keine CLI-Anbindung,
- keine Schreiboperation,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/review_activity_summary.py` | Reines Summary-Modell fuer lokale Review-Vorschlaege |
| `friday/tests/test_review_activity_summary.py` | Unit-Tests fuer Zaehllogik, letzte Aenderungen und Safety-Flags |

## Modellfunktion

```python
build_review_activity_summary(message_suggestions, task_suggestions, recent_limit=5)
```

Die Funktion nimmt bereits geladene lokale Vorschlagslisten entgegen und gibt eine strukturierte `ReviewActivitySummary` zurueck.

## Gezaehlte Bereiche

Nachrichten-Vorschlaege:

- `pending` und `edited` als offen,
- `approved`,
- `rejected`,
- Gesamtzahl.

Aufgaben-Vorschlaege:

- `pending` und `edited` als offen,
- `approved`,
- `rejected`,
- `converted`,
- Vorschlaege mit gesetzter `created_task_id`,
- Gesamtzahl.

## Zuletzt geaenderte Vorschlaege

Das Modell sortiert Vorschlaege mit `updated_at` oder ersatzweise `created_at` absteigend.

Es gibt nur strukturierte Metadaten zurueck:

- Vorschlagstyp,
- Vorschlags-ID,
- Status,
- `updated_at`,
- `created_task_id` bei Aufgaben-Vorschlaegen.

## Safety-Bewertung

- Das Modell liest nur uebergebene Daten.
- Das Modell greift nicht auf SQLite zu.
- Das Modell schreibt nichts.
- Das Modell ruft keine externen Dienste auf.
- Das Modell nutzt kein `input()` und kein `print()`.
- Ergebnis-Flags bleiben:
  - `preview_only = True`,
  - `persisted = False`,
  - `external_action_used = False`.

## Tests

Die Tests pruefen:

- Statuszaehlung fuer Nachrichten-Vorschlaege,
- Statuszaehlung fuer Aufgaben-Vorschlaege,
- Zaehlen von `created_task_id`,
- Sortierung der zuletzt geaenderten Vorschlaege,
- `recent_limit`,
- sichere read-only Flags.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Activity Summary Model Readiness Gate**.

Ziel:

- Modell final pruefen,
- Fokus-Tests und Full Regression bestaetigen,
- dokumentieren, dass noch keine CLI-Anbindung freigegeben ist.
