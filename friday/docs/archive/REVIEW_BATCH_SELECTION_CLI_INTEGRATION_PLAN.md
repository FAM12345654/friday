# Review Batch Selection CLI Integration Plan

## Ziel

Dieses Dokument plant die spaetere CLI-Anbindung der Review-Batch-Auswahl als reine Preview.

Der Schritt bleibt bewusst planend:

- keine Produktlogik-Aenderung,
- keine neue CLI-Implementierung,
- keine Batch-Aktion,
- keine Statusaenderung an Vorschlaegen,
- keine Datenbankoperation,
- keine externen Aktionen.

## Ausgangslage

Der Review Batch Selection Stack ist bis zur read-only Preview vorbereitet:

- Parser fuer Batch-Auswahl-Eingaben,
- Preview-Renderer fuer deutsche Vorschau-Texte,
- Readiness-Gates fuer Parser und Preview.

Noch nicht vorhanden ist eine CLI-Anbindung im Review-Bereich.

## Geplanter Einstiegspunkt

Die Batch-Preview soll spaeter im lokalen Review-Bereich erscheinen, ohne bestehende Einzelpruefung zu ersetzen.

Geplanter Ort:

```text
Hauptmenue -> Vorschlaege pruefen / freigeben -> Review-Uebersicht
```

Moegliche neue Review-Option:

```text
4. Batch-Auswahl als Vorschau anzeigen
```

Wichtig: Diese Option darf nur eine Vorschau anzeigen. Sie darf keine Vorschlaege freigeben, ablehnen oder konvertieren.

## Geplanter Ablauf

```text
Vorschlaege pruefen / freigeben

1. Nachrichten-Vorschlaege pruefen
2. Aufgaben-Vorschlaege pruefen
3. Vorschlaege aktualisieren
4. Batch-Auswahl als Vorschau anzeigen
z. Zurueck zum Hauptmenue
```

Nach Auswahl von Option `4`:

```text
Welche Vorschlaege moechtest du nur als Batch-Vorschau markieren?
Eingaben: 1,2,3 / all / none / z
```

Friday zeigt danach nur:

```text
Batch-Auswahl-Vorschau

Ausgewaehlte Vorschlaege:
- ...

Es wurde noch nichts freigegeben, abgelehnt oder gesendet.
```

## Sichtbare Vorschlaege

Die CLI-Anbindung darf nur die aktuell sichtbaren pending Vorschlaege an Parser und Preview-Renderer uebergeben.

Geplante Sicherheitsregel:

```text
visible_ids = IDs der gerade angezeigten offenen Vorschlaege
```

IDs ausserhalb dieser Liste muessen invalid bleiben.

## UX-Regeln

- Bestehende Einzel-Review-Flows bleiben unveraendert.
- Die Batch-Preview ist sichtbar als Preview beschriftet.
- Jede Ausgabe enthaelt den Hinweis:

```text
Es wurde noch nichts freigegeben, abgelehnt oder gesendet.
```

- Ungueltige Eingaben nutzen:

```text
Ungültige Auswahl. Bitte erneut versuchen.
```

- `z` kehrt stabil zur Review-Uebersicht zurueck.
- Leere Eingabe fuehrt zu keiner Aktion.
- Harte Tokens wie `JA`, `SPEICHERN` oder `KONTAKT LÖSCHEN` haben keine Batch-Wirkung.

## Safety-Grenzen

Die spaetere CLI-Integration darf:

- pending Vorschlaege lokal lesen,
- sichtbare IDs an den Parser uebergeben,
- Preview-Text anzeigen,
- zur Review-Uebersicht zurueckkehren.

Die spaetere CLI-Integration darf nicht:

- Vorschlaege freigeben,
- Vorschlaege ablehnen,
- Aufgaben-Vorschlaege konvertieren,
- Nachrichten senden,
- Kalendertermine erstellen,
- DB-Status aendern,
- externe Dienste aufrufen,
- eine neue Approval-Policy einfuehren.

## Vorgeschlagene spaetere Tests

Fuer einen spaeteren Implementierungs-Step:

- Review-Uebersicht zeigt Batch-Preview-Option.
- Batch-Preview mit `1,2` zeigt nur ausgewaehlte sichtbare Vorschlaege.
- Batch-Preview mit `all` zeigt alle sichtbaren Vorschlaege.
- Batch-Preview mit `none` zeigt keine Auswahl.
- Batch-Preview mit `z` kehrt stabil zurueck.
- Ungueltige ID zeigt Standardmeldung.
- Vorschlaege bleiben pending.
- Keine lokale Aufgabe wird erstellt.
- Keine Nachricht wird gesendet.
- Keine externe Aktion wird ausgeloest.

## Nicht-Ziele

Dieser Plan baut noch nicht:

- keine neue Review-Menueoption,
- keine CLI-Methode,
- keine Batch-Freigabe,
- keine Batch-Ablehnung,
- keine Task-Konvertierung,
- keine Persistenz,
- keine Datenbankschema-Aenderung.

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

Naechster Build Step: **Review Batch Selection CLI Preview Implementation**.

Ziel:

- Batch-Preview im Review-Bereich read-only anbinden,
- Parser und Preview-Renderer nutzen,
- Vorschlaege pending lassen,
- keine Batch-Aktionen,
- keine Statusaenderungen,
- keine externen Aktionen.
