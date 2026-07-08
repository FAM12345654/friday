# Privacy Cleanup DB Guard Plan

## Ziel

Dieses Dokument plant die Guard-Regeln, die vor einem spaeteren SQLite-basierten Privacy-Cleanup-Write gelten muessen.

Der Schritt bleibt bewusst reine Planung:

- keine Produktlogik,
- keine Tests,
- kein Guard-Code,
- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine CLI-Anbindung,
- keine externen Aktionen.

## Ausgangslage

Der DB-Cleanup-Block hat bisher folgende sichere Bausteine:

- DB-Cleanup-Policy-Plan,
- DB-Cleanup-Preview-Plan,
- isoliertes DB-Cleanup-Preview-Modell,
- DB-Cleanup-Preview-Readiness-Gate.

Das Preview-Modell ist read-only und darf nur zaehlen. Ein spaeterer Write bleibt gesperrt, bis ein Guard exakt prueft, ob eine Cleanup-Aktion ueberhaupt erlaubt waere.

## Geplante Guard-Verantwortung

Ein spaeterer DB-Cleanup-Guard soll vor jedem Write pruefen:

| Pruefung | Zweck |
|---|---|
| Bereich ist erlaubt | Nur explizit freigegebene Cleanup-Bereiche |
| Preview liegt vor | Kein Write ohne vorherige read-only Preview |
| Backup ist vorhanden | Keine DB-Aenderung ohne Backup-Nachweis |
| Harte Bestaetigung passt | Kein `ja`, kein `JA`, nur exakter Bereichs-Token |
| Pending-Daten nicht betroffen | Keine offenen Vorschlaege versehentlich loeschen |
| Aktive Daten nicht betroffen | Keine aktiven Aufgaben, Nachrichten oder Kalenderdaten loeschen |
| Transaktion moeglich | Write muss atomar ausfuehrbar sein |
| Rollback moeglich | Fehler darf keine Teilbereinigung hinterlassen |
| Safety Smoke ist PASS | Scanner muessen vor Write sauber sein |
| Externe Aktionen aus | Keine Provider, kein Netzwerk, kein Versand |

## Erlaubte spaetere Guard-Bereiche

| Bereich | Voraussetzung | Token |
|---|---|---|
| Review-History | Nur `rejected` Nachrichten-Vorschlaege und `converted` Aufgaben-Vorschlaege mit vorhandener Aufgabe | `REVIEW AUFRAEUMEN` |
| Einzelner Kontakt-Kontext | Nur exakt ausgewaehlter `contact_id` | `KONTAKT LÖSCHEN` |

## Hart blockierte Bereiche

Diese Bereiche muss ein spaeterer Guard immer blockieren, bis ein eigenes Gate existiert:

- offene Aufgaben,
- erledigte Aufgaben,
- archivierte Aufgaben,
- aktive Nachrichten,
- pending Nachrichten-Vorschlaege,
- pending Aufgaben-Vorschlaege,
- Kalenderdaten,
- aktive SQLite-Hauptdatei,
- Datenbankschema,
- unbekannte Tabellen,
- Secrets,
- Obsidian Vault,
- globale Cleanup-Anfragen.

## Token-Regeln

Ein spaeterer Guard darf nur exakte Tokens akzeptieren:

| Bereich | Erlaubter Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

Explizit blockiert:

- leere Eingabe,
- `ja`,
- `JA`,
- ` Ja `,
- falscher Token,
- Token fuer anderen Bereich.

## Geplante Guard-Ergebnisse

| Status | Bedeutung |
|---|---|
| `allowed` | Alle Bedingungen fuer spaeteren Write waeren erfuellt |
| `blocked` | Mindestens eine Safety-Regel blockiert |
| `missing_preview` | Keine passende Preview vorhanden |
| `missing_backup` | Backup-Nachweis fehlt |
| `invalid_token` | Harte Bestaetigung passt nicht |
| `unsafe_scope` | Bereich oder Filter ist zu breit |
| `pending_data_blocked` | Pending-Daten waeren betroffen |
| `schema_change_blocked` | Schema-Aenderung waere erforderlich |

## Geplante Guard-Ausgabe

Ein spaeterer Guard darf nur sichere Metadaten ausgeben:

- Bereich,
- Status,
- Blockierungsgruende,
- benoetigter Token,
- Backup-Anforderung,
- Transaktions-Anforderung,
- Rollback-Anforderung.

Der Guard darf nicht ausgeben:

- komplette Nachrichtentexte,
- Kontakt-Freitexte,
- Secrets,
- DB-Rohdaten,
- private Notizen.

## Nicht-Ziele dieses Schritts

- Kein Guard-Modell.
- Kein Writer.
- Kein SQL-Write.
- Keine CLI-Anbindung.
- Keine SQLite-Loeschung.
- Keine Migration.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB Guard Model**.

Ziel:

- isoliertes Guard-Modell fuer spaetere DB-Cleanup-Writes bauen,
- keine SQLite-Loeschung,
- keine CLI-Anbindung,
- keine Datenbankschema-Aenderung.
