# Review Activity Summary User Guide

## Ziel

Die Review Activity Summary zeigt dir eine lokale Uebersicht ueber den aktuellen Review-Stand in Friday.

Sie ist nur eine Anzeige. Sie gibt nichts frei, lehnt nichts ab, erstellt keine Aufgabe und sendet keine Nachricht.

## Wo finde ich die Anzeige?

1. Starte Friday.
2. Oeffne im Hauptmenue den Bereich `Vorschlaege pruefen / freigeben`.
3. Waehle dort `6. Review-Aktivitaet anzeigen`.

## Was wird angezeigt?

| Bereich | Bedeutung |
|---|---|
| Nachrichten-Vorschlaege offen | Nachrichten-Vorschlaege, die noch nicht entschieden wurden |
| Nachrichten-Vorschlaege lokal freigegeben | Vorschlaege, die lokal als freigegeben markiert wurden |
| Nachrichten-Vorschlaege abgelehnt | Vorschlaege, die lokal abgelehnt wurden |
| Aufgaben-Vorschlaege offen | Aufgaben-Vorschlaege, die noch nicht entschieden wurden |
| Aufgaben-Vorschlaege abgelehnt | Aufgaben-Vorschlaege, die lokal abgelehnt wurden |
| Aufgaben-Vorschlaege umgewandelt | Vorschlaege, aus denen lokal Aufgaben erstellt wurden |
| Mit lokaler Aufgabe verknuepft | Umgewandelte Vorschlaege mit lokaler Aufgaben-ID |

## Was passiert dabei nicht?

- Es wird keine echte Nachricht gesendet.
- Es wird kein echter Kalendertermin erstellt.
- Es wird kein externer Dienst aufgerufen.
- Es wird keine neue Aufgabe erstellt.
- Es wird kein Vorschlag freigegeben oder abgelehnt.
- Es wird nichts am Datenbankschema geaendert.

## Wann ist die Anzeige hilfreich?

- Wenn du sehen willst, wie viele Review-Vorschlaege noch offen sind.
- Wenn du pruefen willst, wie viele Vorschlaege bereits lokal bearbeitet wurden.
- Wenn du nach Batch-Aktionen kontrollieren willst, ob die lokalen Zaehler plausibel sind.
- Wenn du schnell erkennen willst, welche Aufgaben-Vorschlaege schon in lokale Aufgaben umgewandelt wurden.

## Safety-Hinweis

Die Review Activity Summary ist read-only. Sie nutzt nur vorhandene lokale Daten aus Friday und fuehrt keine externen Aktionen aus.

Die Safety-Flags bleiben unveraendert:

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Summary Documentation Readiness Gate.
