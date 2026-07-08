# Review Activity Search User Guide

## Wofuer ist die Suche da?

Die Review Activity Search zeigt dir lokale Review-Eintraege, die zu einem Suchbegriff passen.

Friday durchsucht nur bereits sichtbare lokale Review-Detail-Felder:

- Typ,
- lokale ID,
- Status,
- Label,
- gekuerzter Vorschautext,
- verknuepfte lokale Aufgaben-ID.

## So nutzt du die Suche

1. Starte Friday.
2. Oeffne den Review-Bereich.
3. Waehle `10. Review-Aktivitaet durchsuchen`.
4. Gib einen Suchbegriff mit mindestens zwei Zeichen ein.

Beispiele:

| Eingabe | Erwartete Treffer |
|---|---|
| `converted` | lokal konvertierte Aufgaben-Vorschlaege |
| `message` | lokale Nachrichten-Vorschlaege |
| `task` | lokale Aufgaben-Vorschlaege |
| `12` | sichtbare lokale ID `12`, wenn vorhanden |

Leere Eingabe oder `z` fuehrt zurueck zur Review-Uebersicht.

## Was passiert bei ungueltigen Eingaben?

Friday zeigt eine sichere Fehlermeldung:

`Ungueltiger Review-Suchbegriff.`

Das gilt auch fuer zu kurze Suchbegriffe.

## Was passiert ohne Treffer?

Friday zeigt:

`Keine lokalen Review-Details fuer diesen Suchbegriff gefunden.`

Es werden keine Vorschlaege veraendert.

## Safety

Die Review Activity Search ist read-only. Sie nutzt nur vorhandene lokale Daten aus Friday und fuehrt keine externen Aktionen aus.

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

- Die Suche nutzt keine KI.
- Die Suche nutzt keine Cloud.
- Die Suche nutzt kein Netzwerk.
- Die Suche ist keine Regex- oder Wildcard-Suche.
- Die Suche ist keine Volltextsuche in Rohdaten.
- Die Suche kombiniert noch nicht mit Status- oder Typfilter.
- Es gibt keinen Export.
- Es werden keine Aufgaben erstellt.
- Es werden keine Nachrichten gesendet.
- Es werden keine Kalendertermine erstellt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Search Documentation Readiness Gate.
