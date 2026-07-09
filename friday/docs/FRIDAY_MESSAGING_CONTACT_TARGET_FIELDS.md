# Friday Messaging Contact Target Fields

## Ziel

Kontakte koennen jetzt lokale Ziel-Felder fuer spaetere Nachrichten-Entwuerfe enthalten:

- `email_address`
- `whatsapp_target`

Diese Felder helfen Friday, einen Weiterleiten-Entwurf klarer vorzubereiten.

## Verhalten

Im Mobile-Kontakte-Tab kann ein Kontakt lokal gespeichert werden mit:

- Name
- optionale E-Mail-Adresse
- optionales WhatsApp-Ziel
- optionale Notiz

Beim Weiterleiten einer Aufgabe zeigt der Entwurf:

- gewaehlter Kanal,
- gespeichertes Ziel,
- Aufgabe,
- Hinweis, dass nichts gesendet wurde.

## Datenhaltung

Die Felder werden lokal in SQLite gespeichert.

Die Migration ist additiv:

- vorhandene Kontakte bleiben erhalten,
- fehlende Spalten werden idempotent ergaenzt,
- keine externen Dienste werden angesprochen.

## Safety

- Es wird keine E-Mail gesendet.
- Es wird keine WhatsApp-Nachricht gesendet.
- Es wird kein Provider aktiviert.
- Es wird kein OAuth/Login genutzt.
- Es wird keine Cloud-AI genutzt.
- Die Felder dienen nur lokalen Entwuerfen.

## Naechster sinnvoller Build-Step

`Messaging Mock Provider`

Ziel:

- Versand weiterhin simulieren,
- keine echten Provider,
- Entwurf plus Ziel pruefen,
- harte Tokens fuer spaeteren Live-Versand vorbereiten.
