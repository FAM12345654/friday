# Privacy Cleanup DB CLI Plan

## Ziel

Dieses Dokument plant, ob und wie der isolierte SQLite Privacy Cleanup DB Stack spaeter sicher in die CLI bzw. das Privacy Dashboard eingebunden werden duerfte.

Der Schritt bleibt bewusst reine Planung:

- keine Produktlogik,
- keine Tests,
- keine CLI-Anbindung,
- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Der DB-Cleanup-Stack ist technisch isoliert vorhanden:

- read-only DB Preview,
- DB Guard,
- DB Writer,
- Readiness-Gates fuer Preview, Guard und Writer.

Noch nicht vorhanden:

- CLI-Menuepunkt,
- Privacy-Dashboard-Anbindung,
- Nutzerfuehrung fuer DB-Cleanup,
- Live-Ausfuehrung ueber die App.

## Geplante CLI-Position

Eine spaetere CLI-Anbindung duerfte nur im Privacy Dashboard liegen.

Vorgeschlagener Pfad:

```text
Hauptmenue
7. Datenschutz / Sicherheit
   4. Privacy Cleanup
      3. Datenbank-Cleanup Vorschau
      4. Datenbank-Cleanup ausfuehren
```

Wichtig:

- Die bestehende Hauptmenue-Struktur darf nicht unkontrolliert verschoben werden.
- Die DB-Cleanup-Ausfuehrung darf nicht als Standardaktion erscheinen.
- Preview muss immer vor Write erscheinen.

## Geplanter Nutzerfluss

### 1. DB-Cleanup Preview

Der Nutzer waehlt einen Bereich:

```text
DB-Cleanup Vorschau
1. Review-History
2. Einzelner Kontakt-Kontext
3. Zurueck
```

Die Preview zeigt nur sichere Metadaten:

- Bereich,
- Kandidatenanzahl,
- Backup erforderlich,
- harter Token,
- ob sensible Inhalte ausgeblendet wurden.

### 2. Guard-Pruefung

Vor Write muss die CLI pruefen:

- Preview wurde direkt vorher gezeigt,
- Backup ist vorhanden,
- Safety Smoke ist `PASS`,
- Bereich ist erlaubt,
- keine externen Aktionen aktiv,
- harter Token passt exakt.

### 3. Write-Bestaetigung

Die CLI darf keine allgemeinen Tokens akzeptieren.

Erlaubte Tokens:

| Bereich | Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

Explizit blockiert:

- leere Eingabe,
- `ja`,
- `JA`,
- Tokens mit fuehrenden oder folgenden Leerzeichen,
- Token fuer anderen Bereich.

## Geplante CLI-Safety-Texte

Beispiel fuer Review-History:

```text
DB-Cleanup Vorschau
Bereich: Review-History
Kandidaten: 3
Es werden nur abgelehnte oder bereits konvertierte Vorschlaege beruecksichtigt.
Pending Vorschlaege, Aufgaben, Nachrichten und Kalenderdaten bleiben erhalten.

Zum Ausfuehren tippe exakt: REVIEW AUFRAEUMEN
Enter bricht ab.
```

Beispiel fuer Kontakt-Kontext:

```text
DB-Cleanup Vorschau
Bereich: Kontakt-Kontext
Kontakt-ID: contact-01
Kandidaten: 1
Es wird nur dieser lokale Kontakt-Kontext geloescht.

Zum Ausfuehren tippe exakt: KONTAKT LÖSCHEN
Enter bricht ab.
```

## Bedingungen fuer eine spaetere Implementierung

Eine spaetere CLI-Implementierung darf nur erfolgen, wenn:

- Preview-Modell genutzt wird,
- Guard-Modell genutzt wird,
- Writer-Modell genutzt wird,
- Safety Smoke vor Write bestanden ist,
- ein aktuelles Backup vorhanden oder unmittelbar vorher erstellt wurde,
- harter Token exakt eingegeben wurde,
- alle Fehlerpfade stabil zum Menue zurueckkehren.

## Nicht-Ziele dieses Schritts

- Keine CLI-Implementierung.
- Kein Menuepunkt.
- Keine SQLite-Loeschung.
- Keine Tests.
- Keine neue Nutzeraktion.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine SQLite-Schreiboperation.
- Keine SQLite-Loeschung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Preview Gate**.

Ziel:

- pruefen, ob Preview, Guard, Writer und Privacy Dashboard fuer eine spaetere CLI-Anbindung ausreichend vorbereitet sind,
- noch keine CLI-Write-Funktion bauen.
