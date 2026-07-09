# Friday Messaging Audit Preview

## Ziel

Friday Mobile zeigt nach einer erfolgreichen Mock-Freigabe eine lokale Audit-Vorschau.

Die Vorschau dokumentiert, was spaeter bei echtem Versand protokolliert werden koennte.

## Verhalten

Nach korrektem Token:

- `EMAIL SENDEN`
- `WHATSAPP SENDEN`

zeigt Friday:

- Zeit,
- Aufgabe,
- Kontakt,
- Kanal,
- Ziel,
- verwendeter Token,
- Status.

## Wichtig

Die Audit-Vorschau schreibt noch kein dauerhaftes Audit.

Sie ist nur eine Anzeige in der App.

## Safety

- Kein echter Versand.
- Kein Provider.
- Kein OAuth/Login.
- Keine externe Netzwerkaktion fuer Nachrichten.
- Kein persistentes Versand-Audit.
- Keine Cloud-AI.

## Naechster sinnvoller Build-Step

`Messaging Persistent Audit Plan`

Ziel:

- planen, wie ein lokales Audit spaeter gespeichert werden duerfte,
- weiterhin kein echter Versand,
- Datenschutz und Loeschregeln definieren.
