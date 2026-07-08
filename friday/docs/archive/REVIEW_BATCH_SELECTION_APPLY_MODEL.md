# Review Batch Selection Apply Model

## Ziel

Dieses Dokument beschreibt das isolierte lokale Review-Batch-Apply-Modell.

Der Step baut lokale Apply-Logik mit Guard-Pflicht:

- keine CLI-Anbindung,
- keine externen Aktionen,
- keine echten Nachrichten,
- keine echten Kalendertermine,
- keine Datenbankschema-Aenderung.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/review_batch_apply_model.py` | Guarded lokales Apply-Modell fuer Review-Batch-Aktionen |
| `friday/tests/test_review_batch_apply_model.py` | Unit-Tests mit tmp_path SQLite fuer lokale Apply-Pfade |

## Guard-Pflicht

Das Apply-Modell fuehrt nur Aktionen aus, wenn:

```text
guard_result.allowed == True
```

Wenn der Guard blockiert, bleibt alles unveraendert.

## Sichtbare Items

Das Apply-Modell arbeitet mit expliziten sichtbaren Items:

```text
virtual_id
suggestion_id
suggestion_type
```

Dadurch koennen virtuelle CLI-IDs sicher auf echte lokale Vorschlags-IDs abgebildet werden, ohne dass Message- und Task-Suggestion-IDs kollidieren.

## Umgesetzte lokale Action Types

| Action Type | Effekt |
|---|---|
| `approve_messages` | Nachrichten-Vorschlaege lokal auf `approved` setzen, ohne Versand |
| `reject_suggestions` | Nachrichten- und Aufgaben-Vorschlaege lokal auf `rejected` setzen |
| `create_tasks` | Aufgaben-Vorschlaege lokal in Aufgaben umwandeln und auf `converted` setzen |

## Safety-Grenzen

Das Apply-Modell darf:

- lokale Vorschlagsstatus aendern,
- lokale Aufgaben aus Aufgaben-Vorschlaegen erstellen,
- created_task_id lokal setzen.

Das Apply-Modell darf nicht:

- Nachrichten senden,
- Kalendertermine erstellen,
- externe Dienste aufrufen,
- CLI-Eingaben lesen,
- direkt drucken,
- Sicherheitsflags veraendern.

## Stale-State-Schutz

Vor jedem Apply prueft das Modell erneut:

- sichtbares Item vorhanden,
- Vorschlag ist noch pending/edited,
- Task-Vorschlag ist noch nicht converted,
- Action Type passt zum Vorschlagstyp.

Dadurch werden stale Preview-Zustaende nicht still angewendet.

## Tests

Die Tests pruefen:

- Guard-Block verhindert jede Aenderung,
- Nachrichten-Vorschlaege werden lokal approved,
- Nachrichten- und Aufgaben-Vorschlaege werden lokal rejected,
- Aufgaben-Vorschlaege werden lokal in Aufgaben umgewandelt,
- fehlender TaskAgent blockiert Task-Erstellung,
- bereits converted Task-Suggestion erzeugt keine Duplikate,
- fehlende sichtbare Items blockieren,
- Safe Flags fuer Ergebnis.

## Nicht umgesetzt

Dieser Step baut bewusst nicht:

- keine CLI-Apply-Option,
- keine Batch-Sendeaktion,
- keine Kalenderaktion,
- keine externen Integrationen,
- keine Datenbankschema-Aenderung.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine CLI-Anbindung.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Apply Model Readiness Gate**.

Ziel:

- Apply-Modell final pruefen,
- Fokus-Tests und Full Regression bestaetigen,
- dokumentieren, dass weiterhin keine CLI-Apply-Option und keine externen Aktionen freigegeben sind.
