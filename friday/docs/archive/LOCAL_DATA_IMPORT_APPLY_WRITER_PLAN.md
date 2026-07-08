# Local Data Import Apply Writer Plan

## Ziel

Dieses Dokument plant einen moeglichen spaeteren lokalen Import-Apply-Writer.

Der Schritt ist bewusst plan-only:

- keine Produktlogik,
- keine Tests,
- kein Writer-Code,
- kein Import,
- kein aktiver SQLite-Write,
- keine Datenbankschema-Aenderung,
- keine CLI-Abfrage von `IMPORT ANWENDEN`.

## Ausgangsstand

Bereits vorhanden sind:

- read-only Manifest Reader,
- read-only Import Dry-Run,
- read-only Import Review CLI,
- read-only Import Apply Preview,
- side-effect-free Import Apply Write Guard,
- Guard Readiness Gate.

Der echte Import bleibt weiterhin nicht freigegeben.

## Writer-Grundregel

Ein spaeterer Writer darf nur ausgefuehrt werden, wenn der Import-Apply-Write-Guard `allowed = True` liefert.

Der Writer darf niemals:

- die aktive SQLite-Datei direkt ersetzen,
- einen In-Place-Restore ausfuehren,
- ohne vorherige Preview schreiben,
- ohne Backup-Schutz schreiben,
- bei Guard-Blockiergruenden schreiben,
- externe Dienste aufrufen,
- private Roh-Nachrichten importieren,
- Secrets importieren,
- sensible Kontakt-Freitexte importieren.

## Vorgeschlagene Writer-Pipeline

| Schritt | Bedingung | Ergebnis |
|---|---|---|
| 1. Exportordner pruefen | liegt unter `local_data/exports/` | Quelle ist lokal begrenzt |
| 2. Manifest Reader nutzen | Manifest ist valide | Import-Grundlage bekannt |
| 3. Import Dry-Run nutzen | Dry-Run ist erlaubt | Dateien sind read-only geprueft |
| 4. Apply Preview nutzen | Preview ist tokenfaehig | Nutzer sieht geplante Sektionen |
| 5. Guard ausfuehren | Guard erlaubt | Write darf theoretisch starten |
| 6. SQLite-Transaktion starten | nur lokale DB | atomarer Write vorbereitet |
| 7. Datensaetze validieren | Pflichtfelder und Scope geprueft | ungueltige Daten blockieren |
| 8. Merge ausfuehren | nur erlaubte Bereiche | lokale Daten werden kontrolliert ergaenzt |
| 9. Commit oder Rollback | Fehler fuehrt zu Rollback | keine Teilimporte |
| 10. Ergebnis zusammenfassen | lokaler Bericht | Nutzer sieht Import-Ergebnis |

## Erlaubte spaetere Writer-Bereiche

| Bereich | Status | Bedingung |
|---|---|---|
| Aufgaben | spaeter denkbar | nur neue oder konfliktfreie Aufgaben |
| Kontakt-Kontexte | spaeter denkbar | nur Consent, keine sensiblen Freitexte |
| Review-Status | spaeter optional | nur lokale Statusdaten, keine externe Aktion |

## Verbotene Writer-Bereiche

| Bereich | Grund |
|---|---|
| aktive SQLite-Rohdatei | niemals direkt ersetzen |
| Safety-Status | nur anzeigen, nicht importieren |
| `.env` / Secrets / Tokens | immer ausgeschlossen |
| Obsidian Vault | nicht Teil des Imports |
| private Roh-Nachrichten | Datenschutzrisiko |
| externe Kontakte | kein Kontaktimport aus externen Quellen |

## Transaktions- und Rollback-Regel

Ein spaeterer Writer muss atomar arbeiten:

- vor dem Commit alle Datensaetze validieren,
- bei Fehlern Rollback,
- keine Teilimporte,
- nach erfolgreichem Commit lokales Ergebnisobjekt,
- keine externen Aktionen nach dem Commit.

## Konfliktstrategie

Default fuer spaetere Implementation:

| Konflikt | Verhalten |
|---|---|
| gleiche Task-ID | blockieren |
| gleicher Task-Titel mit anderem Status | blockieren |
| identischer Task-Datensatz | ueberspringen mit Hinweis |
| gleicher Kontaktname mit anderem Kontext | blockieren |
| fehlendes Pflichtfeld | blockieren |
| unbekannte Sektion | blockieren |

## Vorgeschlagenes Writer-Ergebnis

Ein spaeteres Writer-Modell sollte ein strukturiertes Ergebnis liefern:

| Feld | Bedeutung |
|---|---|
| `applied` | `True` nur nach erfolgreichem Commit |
| `status` | `applied`, `blocked`, `rolled_back`, `invalid` |
| `created_counts` | neu angelegte lokale Datensaetze |
| `skipped_counts` | kontrolliert uebersprungene Datensaetze |
| `blocked_reasons` | harte Blockiergruende |
| `rollback_used` | `True` bei Fehler-Rollback |
| `external_action_used` | muss immer `False` sein |
| `database_schema_changed` | muss fuer diesen Block `False` bleiben |

## Nicht-Ziele

Dieser Plan baut nicht:

- Writer-Code,
- Import-Write,
- CLI-Token-Abfrage,
- Datenbankmigration,
- Konfliktloesungs-UI,
- In-Place-Restore,
- externe Provider,
- Netzwerkaktionen.

## Empfohlene Tests fuer einen spaeteren Writer-Model-Step

Wenn der Writer spaeter implementiert wird, sollten Tests mindestens pruefen:

- blockiert, wenn Guard `allowed = False`,
- schreibt nur bei Guard `allowed = True`,
- schreibt nur erlaubte lokale Bereiche,
- ueberspringt identische Datensaetze kontrolliert,
- blockiert Konflikte,
- blockiert sensible Kontakt-Freitexte,
- blockiert Secrets und private Roh-Nachrichten,
- nutzt SQLite-Transaktion,
- rollback bei Fehler,
- keine Teilimporte,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein Writer implementiert.
- Kein Import implementiert.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Writer Model.

Dieser Schritt sollte einen isolierten Writer-Prototyp mit tmp_path-SQLite und Tests bauen, aber noch keine CLI-Anbindung freigeben.
