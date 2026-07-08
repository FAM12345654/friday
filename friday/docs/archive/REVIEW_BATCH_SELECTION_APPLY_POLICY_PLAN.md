# Review Batch Selection Apply Policy Plan

## Ziel

Dieses Dokument plant die Sicherheitsregeln fuer spaetere Review-Batch-Aktionen.

Der Schritt bleibt bewusst planend:

- keine Produktlogik-Aenderung,
- keine neue CLI-Implementierung,
- keine Batch-Aktion,
- keine Statusaenderung an Vorschlaegen,
- keine Datenbankoperation,
- keine externen Aktionen.

## Ausgangslage

Friday kann im Review-Bereich Batch-Auswahlen bereits read-only anzeigen.

Aktueller Stand:

- Batch-Auswahlparser ist vorhanden.
- Batch-Preview-Renderer ist vorhanden.
- CLI-Preview ist read-only angebunden.
- Vorschlaege bleiben pending.
- Es wird nichts freigegeben, abgelehnt, gesendet oder konvertiert.

## Grundsatz

Spaetere Batch-Aktionen duerfen nur lokale Aktionen sein.

Batch-Auswahl darf niemals automatisch bedeuten:

- echte Nachricht senden,
- echten Kalendertermin erstellen,
- externe Provider aufrufen,
- Standing Approval fuer riskante Aktionen erstellen.

## Erlaubbare spaetere Batch-Aktionen

| Aktion | Spaeter grundsaetzlich erlaubt? | Bedingung |
|---|---|---|
| Nachrichten-Vorschlaege lokal freigeben | ja, aber nur lokal | Preview erforderlich, harter Token erforderlich, kein Versand |
| Nachrichten-Vorschlaege lokal ablehnen | ja | Preview erforderlich, harter Token erforderlich |
| Aufgaben-Vorschlaege lokal ablehnen | ja | Preview erforderlich, harter Token erforderlich |
| Aufgaben-Vorschlaege lokal in Aufgaben umwandeln | ja, aber hoeheres Risiko | Preview erforderlich, harter Token erforderlich, nur lokale Task-Erstellung |
| Kalender-Slots batchweise anwenden | nein | nicht freigegeben |
| echte Nachrichten senden | nein | verboten |
| echte Kalendertermine erstellen | nein | verboten |

## Nicht erlaubte Aktionen

Diese Aktionen bleiben auch fuer spaetere Batch-Flows verboten:

- echte E-Mail senden,
- echte WhatsApp senden,
- echte SMS senden,
- echten Kalendertermin erstellen,
- Wetter-/Musik-Provider aufrufen,
- Cloud-/API-Provider aufrufen,
- externe Modellaufrufe ausloesen,
- Obsidian Write ohne eigenes Obsidian-Gate,
- Import/Export/Backup/Restore-Aktionen ueber Review-Batch ausloesen.

## Harte Token-Policy

Spaetere Batch-Aktionen muessen getrennte harte Tokens verwenden.

Vorgeschlagene Tokens:

| Aktion | Token |
|---|---|
| Nachrichten-Vorschlaege lokal freigeben | `BATCH FREIGEBEN` |
| Vorschlaege lokal ablehnen | `BATCH ABLEHNEN` |
| Aufgaben-Vorschlaege lokal erstellen | `BATCH AUFGABEN ERSTELLEN` |

Nicht ausreichend:

- `ja`
- `JA`
- `ok`
- `SPEICHERN`
- Enter
- einzelne Review-Actions wie `a` oder `r`

## Pflicht-Ablauf vor spaeterem Apply

Jede spaetere Batch-Aktion muss diesen Ablauf erzwingen:

1. Pending Vorschlaege lokal lesen.
2. Sichtbare IDs erzeugen.
3. Batch-Auswahl parsen.
4. Preview anzeigen.
5. Aktion separat auswaehlen.
6. Harte Token-Bestaetigung abfragen.
7. Safety-Grenzen pruefen.
8. Nur dann lokale Aktion anwenden.

Ohne Preview darf keine Batch-Aktion ausgefuehrt werden.

## Scope-Regeln

Batch-Aktionen muessen nach Vorschlagstyp getrennt bleiben:

- Nachrichten-Vorschlaege duerfen nicht gemeinsam mit Aufgaben-Vorschlaegen konvertiert werden.
- Aufgaben-Konvertierung darf nur Aufgaben-Vorschlaege betreffen.
- Nachrichten-Freigabe darf nur Nachrichten-Vorschlaege betreffen.
- Ablehnung kann spaeter gemischt geplant werden, muss aber sichtbar bestaetigt werden.

## Daten- und Statusregeln

Spaetere Batch-Aktionen duerfen nur aktuell pending sichtbare Vorschlaege veraendern.

Nicht erlaubt:

- bereits freigegebene Vorschlaege erneut veraendern,
- bereits abgelehnte Vorschlaege erneut veraendern,
- bereits konvertierte Aufgaben-Vorschlaege erneut konvertieren,
- unsichtbare IDs anwenden,
- alte Preview-Auswahl ohne erneute Anzeige anwenden.

## UX-Regeln

Vor einem spaeteren Apply muss Friday klar anzeigen:

```text
Diese Aktion betrifft X Vorschlaege.
Es werden keine echten Nachrichten gesendet.
Es werden keine echten Kalendertermine erstellt.
```

Bei Aufgaben-Konvertierung muss Friday zusaetzlich anzeigen:

```text
Diese Aktion erstellt lokale Aufgaben.
```

Bei Abbruch:

```text
Batch-Aktion wurde abgebrochen.
```

## Vorgeschlagene spaetere Tests

Fuer spaetere Apply-Model- oder CLI-Steps:

- falscher Token fuehrt zu keiner Statusaenderung,
- `JA` fuehrt zu keiner Batch-Aktion,
- `SPEICHERN` fuehrt zu keiner Batch-Aktion,
- richtiger Token wirkt nur auf sichtbare pending IDs,
- Nachrichten-Freigabe sendet nichts,
- Aufgaben-Konvertierung erstellt nur lokale Aufgaben,
- bereits konvertierte Aufgaben-Vorschlaege werden nicht dupliziert,
- externe Aktionen bleiben deaktiviert,
- invalid Auswahl bleibt ohne Statusaenderung.

## Nicht-Ziele

Dieser Plan baut noch nicht:

- keine Apply-Funktion,
- keine CLI-Apply-Option,
- keine Statusaenderung,
- keine Task-Erstellung,
- keine Datenbankschema-Aenderung,
- keine externen Integrationen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Apply Guard Plan**.

Ziel:

- Guard-Regeln fuer spaetere Batch-Aktionen planen,
- harte Tokens und sichtbare pending IDs absichern,
- keine Batch-Aktion implementieren,
- keine Statusaenderung,
- keine externen Aktionen.
