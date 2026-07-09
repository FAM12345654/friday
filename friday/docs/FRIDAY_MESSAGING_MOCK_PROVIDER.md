# Friday Messaging Mock Provider

## Ziel

Friday Mobile kann jetzt lokal simulieren, was bei einem spaeteren Versand passieren wuerde.

Der Mock Provider sendet nichts.

## Verhalten

Im Weiterleiten-Flow:

1. Aufgabe auswaehlen.
2. Kontakt auswaehlen.
3. Kanal `E-Mail` oder `WhatsApp` auswaehlen.
4. Entwurf pruefen.
5. `Senden simulieren` antippen.

Friday zeigt dann lokal:

```text
Simulation: Wuerde per <Kanal> an <Ziel> gesendet. Es wurde nichts echt gesendet.
```

## Safety

- Keine echte E-Mail.
- Keine echte WhatsApp-Nachricht.
- Keine SMS.
- Kein Provider.
- Kein OAuth/Login.
- Keine Cloud-AI.
- Keine externe Netzwerkaktion fuer den Versand.

## Naechster sinnvoller Build-Step

`Messaging Approval Screen`

Ziel:

- finalen Entwurf sichtbar bestaetigen,
- harte Tokens `EMAIL SENDEN` / `WHATSAPP SENDEN` vorbereiten,
- weiterhin nur Mock Provider,
- kein echter Versand.

Status: umgesetzt in `FRIDAY_MESSAGING_APPROVAL_SCREEN.md`.
