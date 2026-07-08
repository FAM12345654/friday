# Review Activity Status Filter User Guide

## Ziel

Der Review Activity Status Filter zeigt dir lokale Review-Eintraege nach Status.

Er ist nur eine Anzeige. Er gibt nichts frei, lehnt nichts ab, erstellt keine Aufgabe und sendet keine Nachricht.

## Wo finde ich den Filter?

1. Starte Friday.
2. Oeffne im Hauptmenue den Bereich `Vorschlaege pruefen / freigeben`.
3. Waehle dort `8. Review-Aktivitaet nach Status filtern`.
4. Gib einen Statusfilter ein.

## Erlaubte Filter

- `all`
- `open`
- `pending`
- `edited`
- `approved`
- `rejected`
- `converted`

## Was passiert dabei nicht?

- Es wird keine echte Nachricht gesendet.
- Es wird kein echter Kalendertermin erstellt.
- Es wird kein externer Dienst aufgerufen.
- Es wird keine neue Aufgabe erstellt.
- Es wird kein Vorschlag freigegeben oder abgelehnt.
- Es wird nichts am Datenbankschema geaendert.

## Safety-Hinweis

Der Review Activity Status Filter ist read-only. Er nutzt nur vorhandene lokale Daten aus Friday und fuehrt keine externen Aktionen aus.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Status Filter Documentation Readiness Gate.
