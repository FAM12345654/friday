# Friday Messaging Persistent Audit Preview Model

## Ziel

Friday hat ein isoliertes Python-Modell fuer Messaging-Audit-Vorschauen.

Das Modell erzeugt strukturierte Audit-Daten, schreibt sie aber nicht in SQLite und sendet nichts.

## Neue Dateien

- `friday/app/messaging_audit_preview.py`
- `friday/tests/test_messaging_audit_preview.py`

## Abgedeckte Felder

- `created_at`
- `task_id`
- `task_title`
- `contact_id`
- `contact_name`
- `channel`
- `target`
- `draft_text`
- `approval_token`
- `mode`
- `status`
- `provider`
- `external_message_id`

## Safety

- Keine DB-Persistenz.
- Keine API-Anbindung.
- Keine Mobile-Schreibaktion.
- Kein Provider.
- Kein OAuth/Login.
- Kein echter Versand.
- `persisted = False`
- `external_send_enabled = False`

## Tests

Die Tests pruefen:

- Kernfelder werden gesetzt.
- Preview ist nicht persistiert.
- externe Sends bleiben deaktiviert.
- ungueltige Kanaele werden abgelehnt.
- leerer Entwurf wird abgelehnt.
- `external_message_id` ist ausserhalb von Live-Modus blockiert.

## Naechster sinnvoller Build-Step

`Messaging Persistent Audit Repository Plan`

Ziel:

- planen, wie ein lokales SQLite-Repository fuer Audit-Events aussehen duerfte,
- noch keine Mobile-Anbindung,
- weiterhin kein echter Versand.
