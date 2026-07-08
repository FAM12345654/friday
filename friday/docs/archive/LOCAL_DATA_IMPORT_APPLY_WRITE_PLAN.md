# Local Data Import Apply Write Plan

## Ziel

Dieses Dokument plant einen moeglichen spaeteren lokalen Import-Apply-Write.

Der Schritt ist bewusst plan-only:

- keine Produktlogik,
- keine Tests,
- kein Import,
- kein aktiver SQLite-Write,
- keine Datenbankschema-Aenderung,
- keine Abfrage von `IMPORT ANWENDEN`.

## Ausgangsstand

Bereits abgeschlossen sind:

- lokaler Datenexport unter `local_data/exports/`,
- Manifest Reader read-only,
- Import Dry-Run read-only,
- Import Review CLI read-only,
- Import Apply Preview read-only,
- Local Data Import/Export Final Acceptance Gate.

Der echte Import bleibt aktuell nicht freigegeben.

## Grundsatz fuer einen spaeteren Write

Ein spaeterer Import-Apply-Write darf nur als kontrollierter lokaler Merge geplant werden. Er darf niemals:

- die aktive SQLite-Datenbankdatei direkt ersetzen,
- einen In-Place-Restore ausfuehren,
- unbestaetigt schreiben,
- externe Dienste aufrufen,
- Secrets oder Rohdaten importieren,
- sensible Kontakt-Freitexte uebernehmen.

## Vorgeschlagene Write-Pipeline

| Schritt | Bedingung | Ergebnis |
|---|---|---|
| 1. Manifest lesen | Exportordner liegt unter `local_data/exports/` | Manifest-Daten read-only geladen |
| 2. Dry-Run ausfuehren | Manifest ist valide | Exportdateien read-only geprueft |
| 3. Apply-Vorschau erzeugen | Keine Blockiergruende | geplante Sektionen sichtbar |
| 4. Schutz-Backup pruefen | Backup-Schutz ist vorhanden | Import darf weiter geplant werden |
| 5. Konflikte pruefen | Keine offenen Konflikte | Write bleibt moeglich |
| 6. Sensible Daten pruefen | Keine sensiblen Kontakt-Freitexte | Write bleibt moeglich |
| 7. Nutzer bestaetigt | Exakter Token `IMPORT ANWENDEN` | spaeterer Write duerfte starten |
| 8. Transaktion starten | SQLite-Verbindung lokal | atomarer lokaler Merge |
| 9. Validieren | Pflichtfelder und Status pruefen | ungueltige Datensaetze blockieren |
| 10. Commit oder Rollback | Nur bei vollstaendigem Erfolg committen | keine Teilimporte |

## Erlaubte spaetere Datenbereiche

| Bereich | Spaeterer Write denkbar? | Bedingung |
|---|---|---|
| Aufgaben | ja | nur neue oder eindeutig konfliktfreie Datensaetze |
| Kontakt-Kontexte | ja | nur mit Consent und ohne sensible Freitexte |
| Review-Status | eventuell | nur lokale Statusinformationen, keine externen Aktionen |
| Safety-Status | nein | nur anzeigen, nicht importieren |
| aktive SQLite-Rohdatei | nein | niemals ersetzen |
| `.env`, Secrets, Tokens | nein | immer ausgeschlossen |
| Obsidian Vault | nein | nicht importieren |
| private Roh-Nachrichten | nein | nicht importieren |

## Harte Blockiergruende

Ein spaeterer Write muss blockieren bei:

- fehlendem oder ungueltigem Manifest,
- fehlgeschlagenem Import Dry-Run,
- fehlendem Backup-Schutz,
- Exportordner ausserhalb von `local_data/exports/`,
- Zielpfad ausserhalb lokaler Friday-Daten,
- offenen Konflikten,
- sensiblen Kontakt-Freitexten,
- privaten Roh-Nachrichten,
- Secrets oder `.env`-Dateien,
- Obsidian Vault-Inhalten,
- externer Lookup-Markierung,
- Safety Smoke FAIL,
- fehlendem harten Token `IMPORT ANWENDEN`.

## Konfliktregeln

| Konflikt | Vorgeschlagener Default |
|---|---|
| gleiche Task-ID | blockieren |
| gleicher Task-Titel mit anderem Status | blockieren |
| gleicher Kontaktname mit anderem Kontext | blockieren |
| fehlendes Pflichtfeld | blockieren |
| unbekannter Datenbereich | blockieren |
| doppelte Review-ID | blockieren |
| bereits vorhandener identischer Datensatz | ueberspringen mit Hinweis |

## Transaktionsregel

Ein spaeterer Import-Apply-Write muss atomar sein:

- alle geplanten Datensaetze werden vor dem Commit validiert,
- bei einem Fehler erfolgt Rollback,
- keine Teilimporte,
- nach Commit wird eine lokale Zusammenfassung erzeugt,
- kein externer Versand oder Kalender-Write.

## Token-Regel

Der spaetere harte Token bleibt:

```text
IMPORT ANWENDEN
```

Nicht erlaubt:

- `ja`,
- `JA`,
- `ok`,
- `import`,
- leere Eingabe,
- Token mit abweichender Gross-/Kleinschreibung.

Der Token darf erst nach erfolgreicher Preview angezeigt werden.

## Nicht-Ziele

Dieser Plan implementiert nicht:

- Import-Write,
- CLI-Apply-Token-Abfrage,
- Datenbankmigration,
- Konfliktloesungs-UI,
- In-Place-Restore,
- externe Provider,
- Netzwerkaktionen,
- Obsidian-Import,
- Kontaktimport aus externen Quellen.

## Empfohlene Tests fuer einen spaeteren Implementation-Step

Wenn der Write spaeter gebaut wird, sollten mindestens diese Tests entstehen:

- blockiert ohne `IMPORT ANWENDEN`,
- blockiert bei `ja` und `JA`,
- blockiert bei fehlendem Backup-Schutz,
- blockiert bei Dry-Run-Fehler,
- blockiert bei Konflikten,
- blockiert bei sensiblen Kontakt-Freitexten,
- schreibt nur erlaubte lokale Bereiche,
- ueberspringt identische Datensaetze kontrolliert,
- rollback bei Teilfehler,
- kein In-Place-Restore,
- keine externen Aktionen.

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein Import implementiert.
- Kein Restore implementiert.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Write Guard Plan.

Dieser Schritt sollte weiterhin plan/model-first bleiben und zuerst einen side-effect-free Guard fuer `IMPORT ANWENDEN`, Dry-Run, Backup-Schutz, Konflikte und sensible Daten definieren.
