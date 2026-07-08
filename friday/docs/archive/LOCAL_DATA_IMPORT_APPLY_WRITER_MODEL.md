# Local Data Import Apply Writer Model

## Ziel

Dieser Schritt ergaenzt einen isolierten lokalen Import-Apply-Writer-Prototyp.

Der Writer wird nur ausgefuehrt, wenn der Import-Apply-Write-Guard bereits `allowed = True` liefert. Er ist nicht an die CLI angebunden und ersetzt keine aktive SQLite-Datenbankdatei.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/local_data_import_apply_writer.py` | Guarded Writer-Prototyp fuer lokale Export-Zusammenfassungen |
| `friday/tests/test_local_data_import_apply_writer.py` | Unit-Tests mit tmp_path-SQLite |

## Writer-Verhalten

Der Writer kann lokale Export-Zusammenfassungen in eine explizit uebergebene SQLite-Datenbank schreiben:

- `tasks/tasks.json` -> `tasks`,
- `contacts/contact_contexts.json` -> `contact_contexts`,
- `review/review_suggestions.json` -> `message_suggestions`.

Er schreibt nur nach Guard-Erlaubnis.

## Schutzregeln

- Kein Write, wenn der Guard blockiert.
- Keine aktive SQLite-Rohdatei wird ersetzt.
- Kein In-Place-Restore.
- Keine CLI-Token-Abfrage.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine privaten Roh-Nachrichten.
- Keine Secrets.
- Sensible Kontakt-Freitexte werden blockiert.

## Transaktion und Rollback

Der Writer nutzt eine SQLite-Transaktion ueber die lokale Verbindung.

Bei Konflikten oder sensiblen Kontakt-Daten wird der Import zurueckgerollt. Dadurch entstehen keine Teilimporte.

## Konfliktverhalten

| Bereich | Verhalten |
|---|---|
| Identischer Task | ueberspringen |
| Task mit gleichem Titel, aber anderen Daten | Rollback und Block `task_conflict` |
| Identischer Kontakt-Kontext | ueberspringen |
| Kontakt mit gleicher ID, aber anderem Kerninhalt | Rollback und Block `contact_conflict` |
| Bereits vorhandene Review-Suggestion-ID | ueberspringen |

## Tests

Abgesichert ist:

- blockiert bei Guard-Block,
- schreibt erlaubte lokale Bereiche bei Guard-Erlaubnis,
- ueberspringt identische Datensaetze bei erneutem Apply,
- rollt bei Task-Konflikt zurueck,
- blockiert sensible Kontakt-Kontexte und rollt zurueck,
- blockiert fehlende Exportdateien,
- blockiert ungueltige Exportdaten,
- sichere Flags bleiben gesetzt.

## Safety-Bewertung

- Kein CLI-Import freigegeben.
- Kein In-Place-Restore.
- Kein aktiver DB-Datei-Ersatz.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Kein Netzwerk.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Writer Readiness Gate.
