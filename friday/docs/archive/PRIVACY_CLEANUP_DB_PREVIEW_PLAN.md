# Privacy Cleanup DB Preview Plan

## Ziel

Dieses Dokument plant eine spaetere read-only SQLite-Cleanup-Preview fuer sensible lokale Datenbereiche.

Der Schritt bleibt bewusst reine Planung:

- keine Produktlogik,
- keine Tests,
- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine CLI-Anbindung,
- keine externen Aktionen.

## Ausgangslage

Der vorherige DB-Cleanup-Policy-Plan definiert, dass spaetere Datenbank-Cleanup-Aktionen nur mit klarer Preview, Guard, Backup-Pflicht, Transaktion und hartem Token erlaubt sein duerfen.

Diese Preview-Planung konkretisiert nur, wie Friday spaeter ungefaehr anzeigen duerfte, welche lokalen SQLite-Daten fuer eine Bereinigung in Frage kaemen.

## Geplante Preview-Bereiche

| Bereich | Preview erlaubt? | Bedingung |
|---|---|---|
| Abgelehnte Nachrichten-Vorschlaege | ja | Nur Status `rejected`, keine pending Vorschlaege |
| Konvertierte Aufgaben-Vorschlaege | ja | Nur Status `converted`, mit vorhandener `created_task_id` |
| Einzelner Kontakt-Kontext | ja | Nur nach exakter Kontakt-Auswahl, ohne sensible Freitexte |
| Session Suppression Entries | spaeter | Nur falls diese spaeter persistent gespeichert werden |

## Nicht in der Preview enthalten

Diese Daten duerfen in einer allgemeinen DB-Cleanup-Preview nicht als Cleanup-Ziel angeboten werden:

- offene Aufgaben,
- erledigte Aufgaben,
- archivierte Aufgaben ohne eigenes Task-Cleanup-Gate,
- pending Nachrichten-Vorschlaege,
- pending Aufgaben-Vorschlaege,
- aktive Nachrichten-Rohdaten,
- Kalenderdaten,
- aktive SQLite-Hauptdatei,
- Datenbankschema,
- unbekannte Tabellen,
- Safety-Flags,
- Audit- oder Backup-Metadaten.

## Geplante Preview-Ausgabe

Eine spaetere Preview sollte nur aggregierte, sichere Informationen zeigen:

| Feld | Beispiel |
|---|---|
| Bereich | `Review-History` |
| Filter | `status = rejected` |
| Anzahl | `3 Datensaetze` |
| Schreibaktion | `Nein, nur Vorschau` |
| Backup erforderlich | `Ja` |
| Transaktion erforderlich | `Ja` |
| Rollback erforderlich | `Ja` |
| Harte Bestaetigung | `REVIEW AUFRAEUMEN` |
| Sensible Inhalte ausgeblendet | `Ja` |

## Ausdruecklich nicht anzeigen

Die Preview darf keine sensiblen Details ausgeben:

- komplette Nachrichtentexte,
- private Kontakt-Freitexte,
- sensible Relationship-Notizen,
- Secrets,
- API-Schluessel,
- Dateiinhalte aus Backups,
- Rohdaten aus unbekannten Tabellen.

## Geplante Preview-Status

| Status | Bedeutung |
|---|---|
| `preview_only` | Es wird nur angezeigt, nichts geschrieben |
| `blocked` | Bereich ist fuer Cleanup gesperrt |
| `needs_backup` | Backup muss vor Write vorhanden sein |
| `needs_guard` | Guard-Pruefung ist vor Write erforderlich |
| `unsafe_filter` | Filter waere zu breit oder betrifft pending/aktive Daten |

## Beispiel: sichere Review-History-Preview

```text
DB-Cleanup Preview
Bereich: Review-History
Filter: status = rejected
Betroffene Datensaetze: 3
Schreibaktion: Nein
Backup erforderlich: Ja
Harter Token fuer spaeteren Write: REVIEW AUFRAEUMEN
```

## Beispiel: blockierte Preview

```text
DB-Cleanup Preview
Bereich: Aufgaben
Status: blocked
Grund: Aktive Aufgaben duerfen nicht ueber allgemeinen Privacy Cleanup geloescht werden.
Schreibaktion: Nein
```

## Geplante technische Grenzen

Eine spaetere Implementierung duerfte nur:

- bekannte Tabellen lesen,
- bekannte Statusfilter verwenden,
- aggregierte Zaehler ausgeben,
- sensible Inhalte ausblenden,
- niemals direkt loeschen,
- niemals automatisch eine Transaktion starten,
- niemals Datenbankschema aendern.

## Nicht-Ziele dieses Schritts

- Kein DB-Preview-Modell.
- Kein Repository-Code.
- Kein SQL-Code.
- Kein Writer.
- Kein Guard.
- Keine CLI-Integration.
- Keine SQLite-Aenderung.

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

Naechster sinnvoller Build Step: **Privacy Cleanup DB Preview Model**.

Ziel:

- isoliertes read-only Preview-Modell fuer erlaubte DB-Cleanup-Kandidaten planen oder bauen,
- keine SQLite-Loeschung,
- keine CLI-Anbindung,
- keine Datenbankschema-Aenderung.
