# Review Activity Type Filter User Guide

## Wofuer ist der Typfilter da?

Der Review Activity Type Filter zeigt dir lokale Review-Eintraege nach Typ.

Du kannst damit getrennt ansehen:

- alle Review-Eintraege,
- nur Nachrichten-Vorschlaege,
- nur Aufgaben-Vorschlaege.

## So nutzt du den Typfilter

1. Starte Friday.
2. Oeffne den Review-Bereich.
3. Waehle `9. Review-Aktivitaet nach Typ filtern`.
4. Gib einen Typfilter ein.

Erlaubte Filter:

| Eingabe | Anzeige |
|---|---|
| `all` | Alle lokalen Review-Details |
| `message` | Nur Nachrichten-Vorschlaege |
| `task` | Nur Aufgaben-Vorschlaege |

Leere Eingabe oder `z` fuehrt zurueck zur Review-Uebersicht.

## Was passiert bei ungueltigen Eingaben?

Friday zeigt eine sichere Fehlermeldung:

`Ungueltiger Review-Typfilter.`

Es werden keine Vorschlaege veraendert.

## Safety

Der Review Activity Type Filter ist read-only. Er nutzt nur vorhandene lokale Daten aus Friday und fuehrt keine externen Aktionen aus.

Unveraenderte Safety-Flags:

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

## Grenzen

- Der Typfilter kombiniert noch nicht mit dem Statusfilter.
- Es gibt noch keine Suche.
- Es gibt keinen Export.
- Es werden keine Aufgaben erstellt.
- Es werden keine Nachrichten gesendet.
- Es werden keine Kalendertermine erstellt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Type Filter Documentation Readiness Gate.
