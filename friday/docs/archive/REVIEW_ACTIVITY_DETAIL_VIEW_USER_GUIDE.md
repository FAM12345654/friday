# Review Activity Detail View User Guide

## Ziel

Die Review Activity Detail View zeigt dir lokale Review-Eintraege als kurze Liste.

Sie ergaenzt die Review Activity Summary: Die Summary zeigt Zaehler, die Detail View zeigt die einzelnen lokalen Eintraege.

Die Detail View ist nur eine Anzeige. Sie gibt nichts frei, lehnt nichts ab, erstellt keine Aufgabe und sendet keine Nachricht.

## Wo finde ich die Anzeige?

1. Starte Friday.
2. Oeffne im Hauptmenue den Bereich `Vorschlaege pruefen / freigeben`.
3. Waehle dort `7. Review-Aktivitaet im Detail anzeigen`.

## Was wird angezeigt?

| Bereich | Bedeutung |
|---|---|
| Nachrichten-Vorschlaege | Lokale Nachrichten-Vorschlaege mit ID, Status, Absender und kurzem Textauszug |
| Aufgaben-Vorschlaege | Lokale Aufgaben-Vorschlaege mit ID, Status, Titel und kurzem Auszug |
| Konvertierte Aufgaben | Aufgaben-Vorschlaege, die bereits mit einer lokalen Aufgabe verknuepft sind |
| Leere Bereiche | Eine klare Meldung, wenn keine lokalen Details vorhanden sind |

## Beispiel

```text
Review-Aktivitaet im Detail

Nachrichten-Vorschlaege:
- #1 [pending] Chef: Kannst du morgen den Termin...

Aufgaben-Vorschlaege:
- #2 [converted] Rechnung pruefen: Bitte lokal pruefen. -> Aufgabe 7
```

## Was passiert dabei nicht?

- Es wird keine echte Nachricht gesendet.
- Es wird kein echter Kalendertermin erstellt.
- Es wird kein externer Dienst aufgerufen.
- Es wird keine neue Aufgabe erstellt.
- Es wird kein Vorschlag freigegeben oder abgelehnt.
- Es wird nichts am Datenbankschema geaendert.

## Wann ist die Anzeige hilfreich?

- Wenn du sehen willst, welche Review-Eintraege hinter den Summary-Zaehlern stehen.
- Wenn du eine lokale Aufgaben-Verknuepfung schnell erkennen willst.
- Wenn du pruefen willst, ob lokale Review-Status plausibel aussehen.
- Wenn du nach Batch-Aktionen einzelne lokale Eintraege kontrollieren willst.

## Safety-Hinweis

Die Review Activity Detail View ist read-only. Sie nutzt nur vorhandene lokale Daten aus Friday und fuehrt keine externen Aktionen aus.

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

Naechster sinnvoller Build Step: Review Activity Detail View Documentation Readiness Gate.
