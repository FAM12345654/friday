# Friday Mobile Task Delegation Draft Flow

## Ziel

Friday Mobile kann Aufgaben lokal fuer Kolleginnen oder Kollegen vorbereiten.

Der Ablauf:

1. Kontakt lokal speichern.
2. Aufgabe oeffnen.
3. `Weiterleiten` antippen.
4. Kontakt auswaehlen.
5. Kanal auswaehlen:
   - E-Mail
   - WhatsApp
6. Friday erzeugt einen automatischen Nachrichtenentwurf.

## Wichtig

Der Flow sendet noch nichts.

E-Mail und WhatsApp sind aktuell nur Kanal-Auswahl fuer den Entwurf.

## Lokale Kontakte

Im Kontakte-Tab gibt es ein Formular:

- Name der Person
- Notiz, zum Beispiel E-Mail-Adresse oder WhatsApp-Name

Diese Daten werden lokal in Friday gespeichert.

## Weiterleiten-Entwurf

Friday formuliert lokal einen einfachen Entwurf:

```text
Hallo <Name>,

kannst du bitte die Aufgabe "<Aufgabe>" uebernehmen?

Danke dir!

Entwurf fuer <Kanal> - noch nicht gesendet.
```

## Safety

- Keine echte E-Mail wird gesendet.
- Keine echte WhatsApp-Nachricht wird gesendet.
- Keine SMS wird gesendet.
- Keine externen Provider werden genutzt.
- Kein Login wird verwendet.
- Kein OAuth wird verwendet.
- Keine Cloud-AI wird aufgerufen.

## Spaeteres Gate fuer echten Versand

Echter Versand braucht ein separates Gate:

- Provider-Auswahl,
- Login/OAuth,
- Kontakt-Zieladresse oder Telefonnummer,
- harter Approval-Token,
- Versand-Audit,
- Tests mit Mock-Provider vor Live-Betrieb.
