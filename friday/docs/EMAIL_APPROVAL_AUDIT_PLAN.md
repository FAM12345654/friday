# Email Approval and Audit Plan

## Ziel

Dieses Dokument plant spaetere Freigabe- und Audit-Regeln fuer E-Mail-Flows.

Der aktuelle Friday-1.0-Stand bleibt:

- lokale Entwurfsanzeige,
- keine Persistenz,
- kein Provider,
- kein Versand.

## Approval-Grundsatz

Ein spaeterer echter E-Mail-Versand darf niemals durch `ja`, `JA`, Enter oder automatische Modellantworten freigegeben werden.

Ein spaeterer Send-Token muesste in einem eigenen Gate definiert werden.

## Audit-Grundsatz

Riskante E-Mail-Aktionen brauchen vor einem echten Versand einen lokalen Audit Trail.

Geplante Audit-Felder:

| Feld | Bedeutung |
|---|---|
| `action_type` | z. B. `email_send_preview` |
| `draft_id` | lokale Entwurfsreferenz, falls Persistenz spaeter erlaubt wird |
| `recipient_label` | sichtbarer Empfaengerhinweis |
| `approved_by_user` | explizite Nutzerfreigabe |
| `approval_token_used` | spaeterer harter Token |
| `provider_used` | Providername, falls spaeter erlaubt |
| `external_call_used` | ob ein externer Call stattfand |
| `created_at` | lokaler Zeitstempel |

## Nicht erlaubt in diesem Plan

- Versand-Token einfuehren,
- Provider anbinden,
- Audit-DB-Schema bauen,
- Drafts speichern,
- externe Aktionen ausloesen.

## Tests fuer spaetere Umsetzung

- weiche Tokens blockieren,
- fehlender Audit blockiert,
- Draft-only bleibt ohne Audit-Write,
- echter Versand bleibt ohne eigenes Gate unmoeglich.

## Safety-Bewertung

- Keine Produktlogik.
- Keine Provider.
- Keine Secrets.
- Keine Netzwerkaktion.
- Keine Datenbankschema-Aenderung.

## Empfehlung fuer den naechsten Build Step

Nach Friday 1.0: Approval-/Audit-Modell zuerst als Preview planen und isoliert testen, bevor irgendein Real-Provider existiert.
