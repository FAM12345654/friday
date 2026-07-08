# Review Batch Selection Apply Guard Plan

## Ziel

Dieses Dokument plant ein spaeteres Guard-Modell fuer lokale Review-Batch-Aktionen.

Der Schritt bleibt bewusst planend:

- keine Produktlogik-Aenderung,
- keine Guard-Implementierung,
- keine Batch-Aktion,
- keine Statusaenderung an Vorschlaegen,
- keine Datenbankoperation,
- keine externen Aktionen.

## Ausgangslage

Der Review-Batch-Stack hat aktuell:

- Parser fuer Batch-Auswahlen,
- read-only Preview-Renderer,
- read-only CLI-Preview im Review-Bereich,
- Apply-Policy mit harten Token-Regeln.

Ein spaeteres Guard-Modell soll vor jeder Batch-Aktion pruefen, ob die Aktion lokal und sicher erlaubt ist.

## Geplante Guard-Aufgabe

Der Guard soll spaeter nur entscheiden:

```text
allowed: True/False
blocked_reasons: [...]
```

Er darf keine Aktion selbst ausfuehren.

## Geplante Eingaben

Ein spaeteres Guard-Modell braucht voraussichtlich:

```text
action_type
selected_ids
visible_pending_ids
preview_was_shown
approval_token
scanner_smoke_passed
external_actions_enabled
contains_mixed_suggestion_types
contains_already_processed_suggestions
```

## Geplante Action Types

| Action Type | Beschreibung | Erlaubbar? |
|---|---|---|
| `approve_messages` | Nachrichten-Vorschlaege lokal freigeben, ohne Versand | ja, spaeter |
| `reject_suggestions` | Vorschlaege lokal ablehnen | ja, spaeter |
| `create_tasks` | Aufgaben-Vorschlaege lokal in Aufgaben umwandeln | ja, spaeter mit hoeherer Vorsicht |
| `send_messages` | echte Nachrichten senden | nein |
| `create_calendar_events` | echte Termine erstellen | nein |

## Geplante harte Tokens

| Action Type | Erforderlicher Token |
|---|---|
| `approve_messages` | `BATCH FREIGEBEN` |
| `reject_suggestions` | `BATCH ABLEHNEN` |
| `create_tasks` | `BATCH AUFGABEN ERSTELLEN` |

Folgende Eingaben muessen immer blockiert werden:

- leer,
- `ja`,
- `JA`,
- `ok`,
- `SPEICHERN`,
- `KONTAKT LÖSCHEN`,
- einzelne Review-Actions wie `a`, `r`, `s`.

## Geplante Blockgruende

Der Guard soll spaeter klare Blockgruende liefern.

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

## Pflichtregeln

Ein spaeterer Guard darf nur `allowed=True` liefern, wenn alle Bedingungen erfuellt sind:

- Preview wurde unmittelbar vorher gezeigt.
- Aktion ist lokal erlaubt.
- Mindestens eine sichtbare ID wurde ausgewaehlt.
- Alle IDs sind sichtbar.
- Alle IDs sind pending.
- Token passt exakt zum Action Type.
- Safety Smoke ist `PASS`.
- Externe Aktionen sind deaktiviert.
- Keine bereits verarbeiteten Vorschlaege sind enthalten.

## Scope-Regeln

- `approve_messages` darf nur Nachrichten-Vorschlaege betreffen.
- `create_tasks` darf nur Aufgaben-Vorschlaege betreffen.
- `reject_suggestions` kann spaeter gemischt erlaubt werden, muss aber klar dokumentiert und getestet werden.
- Gemischte Auswahl darf nicht versehentlich zu Task-Erstellung oder Nachrichtenfreigabe fuehren.

## Nicht-Ziele

Dieser Plan baut noch nicht:

- keine Guard-Datei,
- keine Tests,
- keine CLI-Anbindung,
- keine Apply-Funktion,
- keine Statusaenderung,
- keine Task-Erstellung,
- keine Datenbankschema-Aenderung,
- keine externen Integrationen.

## Vorgeschlagene spaetere Datei

```text
friday/app/review_batch_apply_guard.py
```

## Vorgeschlagene spaetere Tests

```text
friday/tests/test_review_batch_apply_guard.py
```

Testziele:

- korrekter Token erlaubt nur passende lokale Aktion,
- falscher Token blockiert,
- `JA` blockiert,
- `SPEICHERN` blockiert,
- fehlende Preview blockiert,
- nicht sichtbare IDs blockieren,
- nicht pending IDs blockieren,
- gemischte Auswahl blockiert bei `approve_messages` und `create_tasks`,
- Safety Smoke Fail blockiert,
- externe Aktionen aktiv blockieren,
- verbotene Action Types blockieren.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Apply Guard Model**.

Ziel:

- isoliertes side-effect-free Guard-Modell bauen,
- fokussierte Unit-Tests ergaenzen,
- keine CLI-Anbindung,
- keine Batch-Aktion,
- keine Statusaenderung,
- keine externen Aktionen.
