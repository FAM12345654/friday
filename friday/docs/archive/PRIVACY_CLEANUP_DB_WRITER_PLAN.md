# Privacy Cleanup DB Writer Plan

## Ziel

Dieses Dokument plant einen spaeteren SQLite-basierten Privacy-Cleanup-Writer.

Der Schritt bleibt bewusst reine Planung:

- keine Produktlogik,
- keine Tests,
- kein Writer-Code,
- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine CLI-Anbindung,
- keine externen Aktionen.

## Ausgangslage

Der DB-Cleanup-Block hat bisher sichere Vorstufen:

- DB-Cleanup-Policy-Plan,
- DB-Cleanup-Preview-Plan,
- isoliertes read-only DB-Cleanup-Preview-Modell,
- DB-Cleanup-Preview-Readiness-Gate,
- DB-Cleanup-Guard-Plan,
- isoliertes DB-Cleanup-Guard-Modell,
- DB-Cleanup-Guard-Readiness-Gate.

Ein spaeterer Writer darf nur geplant werden, weil Preview und Guard bereits klare Grenzen definieren. Dieser Step fuehrt noch keine Bereinigung aus.

## Geplante Writer-Verantwortung

Ein spaeterer DB-Cleanup-Writer duerfte nur:

- ein freigegebenes Guard-Ergebnis akzeptieren,
- eine SQLite-Transaktion oeffnen,
- nur bekannte Tabellen und sichere Statusfilter verwenden,
- betroffene Datensaetze loeschen,
- bei Fehler vollstaendig rollbacken,
- nach Erfolg committen,
- nur sichere Zaehler als Ergebnis zurueckgeben,
- keine sensiblen Inhalte ausgeben.

## Erlaubte spaetere Writer-Bereiche

| Bereich | Tabellen | Filter | Token |
|---|---|---|---|
| Review-History | `message_suggestions` | `status = rejected` | `REVIEW AUFRAEUMEN` |
| Review-History | `task_suggestions` | `status = converted` und `created_task_id` existiert in `tasks` | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `contact_contexts` | exakt ausgewaehlter `contact_id` | `KONTAKT LÖSCHEN` |

## Nicht erlaubte Writer-Bereiche

Ein spaeterer Writer muss blockieren:

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
- beliebige Raw-SQL-Anfragen,
- globale Cleanup-Anfragen,
- Obsidian Vault,
- Secrets.

## Geplanter Ablauf

1. Read-only Preview liegt vor.
2. Guard wird mit Preview, Backup-Nachweis, Safety-Smoke-Status und hartem Token ausgefuehrt.
3. Writer akzeptiert nur `guard.allowed is True`.
4. Writer oeffnet SQLite.
5. Writer startet explizite Transaktion.
6. Writer fuehrt nur bekannte parameterisierte Deletes aus.
7. Writer prueft betroffene Zeilenanzahl.
8. Writer committet nur bei vollstaendigem Erfolg.
9. Writer rollt bei jedem Fehler zurueck.
10. Writer gibt nur sichere Ergebniszaehler zurueck.

## Geplante Ergebnisdaten

Ein spaeterer Writer sollte strukturiert zurueckgeben:

| Feld | Bedeutung |
|---|---|
| `allowed` | Guard war freigegeben |
| `cleanup_area` | Bereinigter Bereich |
| `deleted_counts` | Zaehler pro Tabelle |
| `transaction_used` | Transaktion wurde verwendet |
| `rollback_performed` | Rollback wurde bei Fehler ausgefuehrt |
| `schema_changed` | Muss immer `False` bleiben |
| `external_action_used` | Muss immer `False` bleiben |
| `sensitive_content_returned` | Muss immer `False` bleiben |

## Sicherheitsregeln fuer SQL

Ein spaeterer Writer darf nur:

- parameterisierte SQL-Anweisungen verwenden,
- bekannte Tabellen direkt im Code definieren,
- keine Tabellen- oder Spaltennamen aus Nutzereingaben uebernehmen,
- keine Wildcard-Loeschung ohne Filter ausfuehren,
- keine `DROP`, `ALTER`, `CREATE`, `TRUNCATE` oder Migration ausfuehren,
- keine pending Status loeschen.

## Rollback-Regeln

Rollback ist Pflicht, wenn:

- Guard nicht erlaubt,
- SQLite-Fehler auftritt,
- unbekannter Bereich angefordert wird,
- betroffene Zeilen nicht zur Preview passen,
- Transaktion nicht sauber abgeschlossen werden kann,
- unerwartete Exception auftritt.

## Nicht-Ziele dieses Schritts

- Kein DB-Writer-Modell.
- Kein SQL-Write.
- Keine SQLite-Loeschung.
- Keine CLI-Anbindung.
- Keine Migration.
- Keine externen Aktionen.
- Keine automatische Bereinigung.

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

Naechster sinnvoller Build Step: **Privacy Cleanup DB Writer Model**.

Ziel:

- isoliertes SQLite-Writer-Modell mit Guard-Pflicht und Transaktion bauen,
- nur bekannte sichere Tabellen und Statusfilter,
- keine CLI-Anbindung,
- keine Datenbankschema-Aenderung.
