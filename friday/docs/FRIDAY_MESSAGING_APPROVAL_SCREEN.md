# Friday Messaging Approval Screen

## Ziel

Friday Mobile bereitet jetzt den spaeteren Freigabe-Schritt fuer Nachrichtenversand vor.

Der Flow bleibt weiterhin Mock-only.

## Verhalten

Im Weiterleiten-Flow:

1. Aufgabe auswaehlen.
2. Kontakt auswaehlen.
3. Kanal auswaehlen:
   - E-Mail
   - WhatsApp
4. Entwurf pruefen.
5. Versand simulieren.
6. Freigabe-Token testen.

## Harte Tokens

Je nach Kanal erwartet Friday exakt:

```text
EMAIL SENDEN
WHATSAPP SENDEN
```

Andere Eingaben werden abgelehnt.

## Wichtig

Auch wenn der Token korrekt ist:

- Es wird keine echte E-Mail gesendet.
- Es wird keine echte WhatsApp-Nachricht gesendet.
- Es wird kein Provider genutzt.
- Es wird kein Login genutzt.

Die App zeigt nur, dass die spaetere Freigabe-Regel funktionieren wuerde.

## Safety

- Draft-only.
- Mock-only.
- Keine externen Send-Aktionen.
- Keine Provider-Aktivierung.
- Keine OAuth-/Login-Daten.
- Keine Cloud-AI.

## Naechster sinnvoller Build-Step

`Messaging Audit Preview`

Ziel:

- lokale Vorschau eines Versand-Audits,
- weiterhin kein echter Versand,
- dokumentieren, welcher Entwurf wann freigegeben wuerde.

Status: umgesetzt in `FRIDAY_MESSAGING_AUDIT_PREVIEW.md`.
