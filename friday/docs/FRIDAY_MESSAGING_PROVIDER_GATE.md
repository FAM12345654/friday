# Friday Messaging Provider Gate

## Ziel

Dieses Gate beschreibt den sicheren Weg von lokalen Weiterleiten-Entwuerfen zu spaeterem echten Versand per E-Mail oder WhatsApp.

Aktueller Stand:

- Kontakte koennen lokal gespeichert werden.
- Aufgaben koennen an Kontakte als Entwurf vorbereitet werden.
- Kanal-Auswahl `E-Mail` oder `WhatsApp` ist vorhanden.
- Es wird noch nichts echt gesendet.

## Nicht-Ziele dieses Gates

- Kein echter E-Mail-Versand.
- Kein echter WhatsApp-Versand.
- Kein SMS-Versand.
- Kein Provider-Login.
- Kein OAuth.
- Kein API-Key.
- Keine Cloud-AI.
- Kein automatisches Senden.

## Erforderliche Sicherheitsstufen vor echtem Versand

| Stufe | Zweck | Status |
|---|---|---|
| 1. Lokale Kontakte | Personen lokal speichern | vorhanden |
| 2. Entwurf | Nachricht lokal formulieren | vorhanden |
| 3. Zieladresse | E-Mail-Adresse oder WhatsApp-/Telefon-Ziel lokal erfassen | offen |
| 4. Provider-Auswahl | Anbieter bewusst konfigurieren | offen |
| 5. Mock Provider | Versand simulieren, ohne externen Effekt | offen |
| 6. Approval Screen | finalen Text vor Versand anzeigen | offen |
| 7. Harter Token | Versand nur nach exaktem Token | offen |
| 8. Audit | Versandversuch lokal protokollieren | offen |
| 9. Live Provider | echter Versand nur nach separatem Live-Gate | offen |

## Harte Tokens fuer spaeteren Versand

Vorschlag fuer spaetere Gates:

```text
EMAIL SENDEN
WHATSAPP SENDEN
```

Diese Tokens duerfen nicht durch `ja`, `JA`, Enter oder unklare Bestaetigungen ersetzt werden.

## Kontakt-Zieldaten

Vor echtem Versand muessen Kontakte getrennte optionale Felder bekommen:

- `email_address`
- `whatsapp_target`

Diese Felder duerfen erst in einem eigenen lokalen Persistenz-Gate eingefuehrt werden.

## Provider-Regeln

E-Mail:

- zuerst Draft-only,
- dann Mock-Provider,
- dann echter Provider nur mit Login/OAuth-Gate,
- kein Send ohne Vorschau und harten Token.

WhatsApp:

- zuerst Draft-only,
- dann Mock-Provider,
- echte WhatsApp-API nur nach Provider-Gate,
- kein Send ohne Vorschau und harten Token.

## KI-/Text-Regeln

Aktuell wird der Entwurf lokal durch eine einfache Vorlage erzeugt.

Spaeter moegliche KI-Unterstuetzung:

- nur lokal oder explizit freigegeben,
- keine sensiblen Kontaktdaten ohne Zustimmung an externe Modelle,
- Ausgabe muss vor Versand sichtbar sein,
- Nutzer muss final bestaetigen.

## Safety-Bewertung

- Externe Aktionen bleiben deaktiviert.
- Keine echten Nachrichten werden gesendet.
- Keine Provider-Zugangsdaten werden gespeichert.
- Keine Datenbankschema-Aenderung in diesem Gate.
- Aktueller Mobile-Flow bleibt Draft-only.

## Naechster sinnvoller Build-Step

`Messaging Contact Target Fields`

Ziel:

- Kontakte um lokale Ziel-Felder vorbereiten,
- weiterhin kein Versand,
- Mobile-UI fuer E-Mail-Adresse/WhatsApp-Ziel,
- Tests fuer lokale Speicherung,
- Safety-Status weiterhin klar anzeigen.

Status: umgesetzt in `FRIDAY_MESSAGING_CONTACT_TARGET_FIELDS.md`.

Mock Provider Status: umgesetzt in `FRIDAY_MESSAGING_MOCK_PROVIDER.md`.

Approval Screen Status: umgesetzt in `FRIDAY_MESSAGING_APPROVAL_SCREEN.md`.
