# Email Draft-Only Plan

## Ziel

Dieser Plan beschreibt, wie Friday spaeter lokale E-Mail-Entwuerfe vorbereiten darf, ohne echte E-Mails zu senden.

Der Schritt bleibt reine Planung:

- kein SMTP,
- kein Gmail,
- kein Outlook,
- kein Login,
- keine Secrets,
- kein Netzwerk,
- kein echter Versand,
- keine Produktlogik,
- keine Datenbankschema-Aenderung.

## Grundprinzip

Friday darf zuerst nur einen lokalen Entwurfstext erstellen und anzeigen.

Ein Entwurf ist keine E-Mail-Aktion.
Ein Entwurf darf nicht automatisch gesendet werden.
Ein Entwurf darf keinen Provider beruehren.

## Erlaubte Entwurfsdaten

| Feld | Zweck | Regel |
|---|---|---|
| `recipient_label` | sichtbarer Empfaengername oder Kontaktlabel | kein echter Versandbezug |
| `subject` | lokaler Betreffvorschlag | kurz, ohne Secrets |
| `body` | lokaler Nachrichtentext | keine sensiblen Daten automatisch einfuegen |
| `source_context` | Ursprung, z. B. Review | lokal |
| `preview_only` | Safety-Flag | immer `True` |
| `provider_used` | Provider-Hinweis | immer `False` |
| `external_send_enabled` | Send-Hinweis | immer `False` |

## Nicht erlaubte Daten

| Datenart | Regel |
|---|---|
| Passwoerter | nicht in Entwuerfe aufnehmen |
| API Keys / Tokens | nicht in Entwuerfe aufnehmen |
| private Finanzdetails | nicht automatisch uebernehmen |
| Gesundheitsdaten | nicht automatisch uebernehmen |
| politische/religioese/ethnische Daten | nicht automatisch uebernehmen |
| echte OAuth-Tokens | nicht speichern oder anzeigen |
| Provider-Konfiguration | nicht Teil des Draft-only-Modells |

## Geplanter Entwurfsstatus

| Status | Bedeutung |
|---|---|
| `drafted` | Entwurf wurde lokal erstellt |
| `edited` | Entwurf wurde lokal bearbeitet |
| `discarded` | Entwurf wurde verworfen |
| `blocked` | Entwurf wurde durch Safety-Regel blockiert |

Nicht erlaubt in diesem Block:

- `sent`,
- `queued`,
- `scheduled_send`,
- `provider_delivered`.

## UX-Entwurf

Moegliche lokale Anzeige:

```text
E-Mail-Entwurf (lokal, nicht gesendet)

An: Max Mustermann
Betreff: Rueckmeldung zu deinem Termin

Hallo Max,
...

Hinweis: Dies ist nur ein lokaler Entwurf. Es wurde nichts gesendet.
```

## Spaetere CLI-Regel

Wenn ein CLI-Flow gebaut wird, muss die Anzeige klar sagen:

- `Es wurde nichts gesendet.`
- `Kein E-Mail-Provider ist verbunden.`
- `Dies ist nur eine lokale Vorschau.`

Ein spaeterer Send-Flow ist nicht Teil dieses Plans.

## Tests fuer spaetere Umsetzung

Wenn das Modell gebaut wird, braucht es Tests fuer:

- gueltiger Entwurf wird erstellt,
- leerer Betreff wird sicher ersetzt oder blockiert,
- leerer Body wird blockiert oder klar angezeigt,
- sensible Inhalte werden blockiert,
- `preview_only` bleibt `True`,
- `provider_used` bleibt `False`,
- `external_send_enabled` bleibt `False`,
- kein `send`-Status existiert.

## Safety-Grenzen

- Keine externen Aktionen.
- Kein echter Versand.
- Kein Provider.
- Keine Secrets.
- Keine Netzwerkaktion.
- Keine Datenbankschema-Aenderung.
- Keine Modellantwort darf automatisch gesendet werden.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Schritt: `Email Draft Model`.

Ziel: Ein isoliertes Python-Datenmodell und Renderer fuer lokale E-Mail-Entwuerfe bauen, ohne Provider, Netzwerk, Login oder Versand.
