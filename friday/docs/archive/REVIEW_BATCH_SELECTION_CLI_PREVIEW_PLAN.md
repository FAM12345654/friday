# Review Batch Selection CLI Preview Plan

## Ziel

Dieses Dokument plant eine spaetere read-only CLI-Preview fuer Review-Batch-Auswahlen.

Der Schritt bleibt bewusst planend:

- keine Produktlogik-Aenderung,
- keine neue CLI-Implementierung,
- keine Batch-Aktion,
- keine Statusaenderung an Vorschlaegen,
- keine Datenbankoperation,
- keine externen Aktionen.

## Ausgangslage

Der isolierte Review Batch Selection Parser ist vorhanden und als side-effect-free Modell abgenommen.

Er kann Eingaben wie diese interpretieren:

```text
1,2,3
all
none
z
```

Der naechste sinnvolle Produktschritt ist eine sichere CLI-Preview, die dem Nutzer zeigt, welche Vorschlaege eine Batch-Auswahl betreffen wuerde, ohne irgendetwas anzuwenden.

## Geplantes CLI-Verhalten

Die Preview soll spaeter im lokalen Review-Bereich sichtbar sein.

Moeglicher Ablauf:

```text
Vorschlaege pruefen / freigeben

Offene Nachrichten-Vorschlaege:
1. ...
2. ...
3. ...

Batch-Auswahl eingeben (z. B. 1,2,3 / all / none / z):
```

Danach zeigt Friday nur eine Vorschau:

```text
Auswahl-Vorschau:
- Vorschlag 1
- Vorschlag 2

Es wurde noch nichts freigegeben, abgelehnt oder gesendet.
```

## Geplante erlaubte Eingaben

| Eingabe | Preview-Verhalten |
|---|---|
| `1,2,3` | gewaehlte sichtbare Vorschlaege anzeigen |
| `all` | alle sichtbaren Vorschlaege anzeigen |
| `none` | keine Auswahl anzeigen |
| `z` | zurueck zum Review-Bereich |
| leer | ohne Aktion zurueck oder Hinweis anzeigen |
| invalid | Standard-Fehlermeldung anzeigen |

## Wichtige UX-Regeln

- Die Preview muss klar sagen, dass noch nichts angewendet wurde.
- Sichtbare Vorschlaege bleiben pending.
- Ungueltige Eingaben nutzen die bestehende Standardmeldung:

```text
Ungültige Auswahl. Bitte erneut versuchen.
```

- `JA`, `SPEICHERN`, `a` und `r` duerfen in der Batch-Auswahl nicht als Aktion wirken.
- Nutzer muessen spaeter fuer echte Batch-Aktionen einen getrennten, expliziten Schritt bekommen.

## Safety-Grenzen

Die geplante CLI-Preview darf:

- den Parser aufrufen,
- sichtbare Vorschlaege anzeigen,
- eine Auswahl-Vorschau rendern,
- bei invalid Eingaben eine Fehlermeldung zeigen.

Die geplante CLI-Preview darf nicht:

- Vorschlaege freigeben,
- Vorschlaege ablehnen,
- Aufgaben-Vorschlaege konvertieren,
- Nachrichten senden,
- Kalendertermine erstellen,
- DB-Status aendern,
- echte externe Aktionen ausloesen.

## Vorgeschlagene spaetere Tests

Fuer einen spaeteren CLI-Preview-Model- oder Implementation-Step:

- Batch-Preview zeigt ausgewaehlte sichtbare Vorschlaege.
- `all` zeigt alle sichtbaren Vorschlaege.
- `none` zeigt keine Auswahl.
- `z` kehrt stabil zurueck.
- Ungueltige Eingaben zeigen Standardmeldung.
- Vorschlaege bleiben pending.
- Keine lokale Aufgabe wird erstellt.
- Keine Nachricht wird gesendet.
- Keine externe Aktion wird ausgeloest.

## Nicht-Ziele

Dieser Plan baut noch nicht:

- keine CLI-Methode,
- keine Menueoption,
- keine Batch-Apply-Funktion,
- keine Statusaenderung,
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

Naechster Build Step: **Review Batch Selection CLI Preview Model**.

Ziel:

- reinen Renderer/Preview-Baustein fuer Batch-Auswahl bauen,
- Parser-Ergebnis und sichtbare Vorschlaege in deutschen Preview-Text umwandeln,
- keine CLI-Anbindung,
- keine Review-Aktionen,
- keine Persistenz,
- keine externen Aktionen.
