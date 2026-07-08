# Privacy Cleanup DB Cleanup Policy Plan

## Ziel

Dieses Dokument plant, ob und wie spaetere SQLite-basierte Privacy-Cleanup-Aktionen fuer Review-History und Kontakt-Kontexte sicher aussehen duerften.

Dieser Schritt ist bewusst nur Planung:

- keine Produktlogik,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine CLI-Anbindung,
- keine Tests,
- keine externen Aktionen.

## Ausgangslage

Der aktuelle Privacy-Cleanup-Block ist fuer lokale Datei-Cleanup-Ziele final angenommen:

- Exporte,
- Backups,
- Restore-Kopien.

Weiterhin blockiert:

- Kontakt-Kontext-Cleanup,
- Review-History-Cleanup,
- Obsidian-Cleanup,
- aktive SQLite-Datenbank,
- Datenbankschema-Aenderungen.

## Grundsatz fuer spaetere DB-Cleanup-Aktionen

SQLite-Cleanup darf nur mit eigenem spaeterem Gate geplant und umgesetzt werden.

Vor jeder DB-Cleanup-Aktion muessen gelten:

1. Read-only Preview.
2. Konkrete Auswahl einzelner Daten.
3. Kein Massenloeschen ohne Filter.
4. Backup-Pflicht.
5. SQLite-Transaktion.
6. Rollback-Pflicht bei Fehler.
7. Exakter harter Token.
8. Guard-Freigabe.
9. Ergebnisbericht ohne sensible Inhalte.

## Potenziell bereinigbare Bereiche

| Bereich | Status | Bedingung |
|---|---|---|
| Abgelehnte Nachrichten-Vorschlaege | spaeter denkbar | Nur alte `rejected` Vorschlaege, keine pending Vorschlaege |
| Konvertierte Aufgaben-Vorschlaege | spaeter denkbar | Nur `converted` Vorschlaege mit vorhandener lokaler Aufgabe |
| Einzelner Kontakt-Kontext | spaeter denkbar | Nur exakt ausgewaehlter Kontakt mit hartem Token |
| Session Suppression Entries | spaeter denkbar | Nur falls spaeter persistiert; aktuell meist in-memory |

## Weiterhin gesperrte DB-Bereiche

Diese Bereiche duerfen nicht durch einen allgemeinen DB-Cleanup geloescht werden:

- offene Aufgaben,
- erledigte Aufgaben ohne eigenes Task-Gate,
- aktive Nachrichtendaten,
- pending Nachrichten-Vorschlaege,
- pending Aufgaben-Vorschlaege,
- Kalenderdaten,
- aktive SQLite-Hauptdatei,
- Safety-Status,
- Audit-/Backup-Metadaten,
- Datenbankschema,
- unbekannte Tabellen.

## Geplante harte Tokens

| Bereich | Token |
|---|---|
| Review-History-Cleanup | `REVIEW AUFRAEUMEN` |
| Einzelnen Kontakt vergessen | `KONTAKT LÖSCHEN` |

Token-Regeln:

- `ja` ist nie ausreichend.
- `JA` ist nie ausreichend.
- Leere Eingabe bricht ab.
- Token muessen exakt passen.

## Geplante Preview-Regeln

Eine spaetere DB-Cleanup-Preview muss zeigen:

- Bereich,
- Anzahl der geplanten Datensaetze,
- Statusfilter,
- ob Backup erforderlich ist,
- ob Rollback moeglich ist,
- ob pending Daten betroffen waeren,
- ob sensible Inhalte ausgeblendet wurden.

Die Preview darf nicht anzeigen:

- private Nachrichtentexte,
- sensible Kontakt-Freitexte,
- Secrets,
- API-Schluessel,
- private Rohdaten.

## Geplante Guard-Regeln

Ein spaeterer DB-Cleanup-Guard muss blockieren, wenn:

- kein Backup bereit ist,
- keine Transaktion moeglich ist,
- kein Rollback moeglich ist,
- pending Vorschlaege betroffen sind,
- aktive Aufgaben betroffen sind,
- unbekannte Tabellen betroffen sind,
- Datenbankschema-Aenderung erforderlich waere,
- Token nicht exakt passt,
- Safety Smoke nicht `PASS` ist,
- externe Aktionen aktiviert waeren.

## Geplante Writer-Regeln

Ein spaeterer DB-Cleanup-Writer duerfte nur:

- mit Guard-Freigabe laufen,
- innerhalb einer SQLite-Transaktion arbeiten,
- einzelne bekannte Tabellen und Statusfilter nutzen,
- bei Fehler komplett rollbacken,
- Ergebniszahlen liefern,
- keine sensiblen Inhalte in Ausgaben schreiben.

## Nicht-Ziele dieses Schritts

- Kein DB-Cleanup-Modell.
- Kein DB-Cleanup-Guard.
- Kein DB-Cleanup-Writer.
- Keine CLI-Anbindung.
- Keine SQLite-Loeschung.
- Keine Migration.
- Keine externen Aktionen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB Preview Plan**.

Ziel:

- planen, wie eine read-only DB-Cleanup-Preview fuer Review-History und Kontakt-Kontexte aussehen koennte,
- keine Implementierung,
- keine SQLite-Loeschung.
