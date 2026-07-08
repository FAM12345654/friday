# Review Batch Selection Apply Guard Model

## Ziel

Dieses Dokument beschreibt das isolierte Guard-Modell fuer spaetere lokale Review-Batch-Aktionen.

Der Step baut nur eine side-effect-free Pruefung:

- keine CLI-Anbindung,
- keine Batch-Aktion,
- keine Statusaenderung,
- keine Datenbankoperation,
- keine externen Aktionen.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/review_batch_apply_guard.py` | Side-effect-free Guard fuer spaetere Batch-Aktionen |
| `friday/tests/test_review_batch_apply_guard.py` | Unit-Tests fuer Token, IDs, Preview, Safety und Action Types |

## Guard-Aufgabe

Der Guard entscheidet nur:

```text
allowed: True/False
blocked_reasons: [...]
```

Er fuehrt keine Aktion selbst aus.

## Erlaubte lokale Action Types

| Action Type | Token |
|---|---|
| `approve_messages` | `BATCH FREIGEBEN` |
| `reject_suggestions` | `BATCH ABLEHNEN` |
| `create_tasks` | `BATCH AUFGABEN ERSTELLEN` |

## Blockgruende

| Blockgrund | Bedeutung |
|---|---|
| `preview_missing` | Vor der Aktion wurde keine Preview gezeigt |
| `invalid_action_type` | Aktion ist unbekannt oder verboten |
| `missing_selection` | Keine IDs ausgewaehlt |
| `ids_not_visible` | Auswahl enthaelt nicht sichtbare IDs |
| `ids_not_pending` | Auswahl enthaelt nicht pending Vorschlaege |
| `mixed_types_not_allowed` | Aktion passt nicht zu gemischten Vorschlagstypen |
| `invalid_token` | Harter Token fehlt oder ist falsch |
| `scanner_smoke_failed` | Safety Smoke ist fehlgeschlagen |
| `external_actions_enabled` | Externe Aktionen sind aktiv oder nicht sicher deaktiviert |
| `already_processed` | Auswahl enthaelt bereits verarbeitete Vorschlaege |

## Safe Flags

Jedes Guard-Ergebnis enthaelt:

- `preview_only = True`
- `persisted = False`
- `external_action_used = False`

## Tests

Die Tests pruefen:

- erlaubte Action Types mit exaktem Token,
- falsche Tokens inklusive `JA` und `SPEICHERN`,
- fehlende Preview,
- fehlende Auswahl,
- nicht sichtbare / nicht pending IDs,
- gemischte Typen fuer Message-Approval und Task-Creation,
- bereits verarbeitete Vorschlaege,
- Safety-Smoke-Fehler,
- aktivierte externe Aktionen,
- verbotene Action Types,
- Deduplizierung von IDs,
- Safe Flags.

## Nicht umgesetzt

Dieser Step baut bewusst nicht:

- keine CLI-Apply-Option,
- keine Batch-Freigabe,
- keine Batch-Ablehnung,
- keine Task-Erstellung,
- keine Persistenz,
- keine Datenbankschema-Aenderung,
- keine externen Integrationen.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine CLI-Anbindung.
- Keine Persistenz.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Apply Guard Readiness Gate**.

Ziel:

- Guard-Modell final pruefen,
- Tests und Safety Smoke bestaetigen,
- dokumentieren, dass weiterhin keine Batch-Aktion freigegeben ist.
