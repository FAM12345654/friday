# Local Data Import Apply Write Guard Model

## Ziel

Dieser Schritt ergaenzt ein isoliertes, side-effect-free Guard-Modell fuer einen moeglichen spaeteren lokalen Import-Apply-Write.

Der Guard entscheidet nur, ob ein spaeterer Write theoretisch freigegeben waere. Er schreibt nichts, importiert nichts und veraendert keine aktive Friday-Datei.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/local_data_import_apply_write_guard.py` | Side-effect-free Guard-Modell |
| `friday/tests/test_local_data_import_apply_write_guard.py` | Unit-Tests fuer Token, Preview, Backup, Konflikte, Scope und Safety |

## Guard-Verhalten

Der Guard nutzt:

- Apply-Preview-Ergebnis,
- harten Token `IMPORT ANWENDEN`,
- Safety-Smoke-Status,
- optionalen Write-Scope,
- Konflikt-/Sensitive-/Secret-/Rohdaten-Markierungen.

Er liefert:

- `allowed`,
- `status`,
- `blocked_reasons`,
- `warnings`,
- `required_token`,
- `write_scope`,
- `forbidden_write_scope`,
- sichere Side-Effect-Flags.

## Blockiergruende

Der Guard blockiert unter anderem bei:

- fehlender Preview,
- invalid/blocked Preview,
- nicht tokenfaehiger Preview,
- fehlendem Backup-Schutz,
- Safety Smoke FAIL,
- Konflikten,
- sensiblen Kontakt-Freitexten,
- Secrets,
- privaten Roh-Nachrichten,
- externer Lookup-Markierung,
- verbotenem Write-Scope,
- Datenbankschema-Aenderungsbedarf,
- falschem Token.

## Token-Regel

Nur exakt:

```text
IMPORT ANWENDEN
```

wird akzeptiert.

Explizit blockiert sind:

- `ja`,
- `JA`,
- `ok`,
- `import`,
- `Import anwenden`,
- `IMPORT`,
- leere Eingabe,
- Eingaben mit nachgestelltem Leerzeichen.

## Safety-Bewertung

- Kein Import.
- Kein Restore.
- Kein Datei-Write.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Kein `input()`.
- Kein `print()`.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Tests

Abgesichert ist:

- gueltige Preview + exakt `IMPORT ANWENDEN` erlaubt,
- Warnungs-Preview bleibt erlaubt,
- fehlende Preview blockiert,
- falsche Tokens blockieren,
- Scanner Smoke FAIL blockiert,
- invalid/blocked Preview blockiert,
- fehlender Backup-Schutz blockiert,
- Konflikte blockieren,
- sensible Daten blockieren,
- Secrets und private Roh-Nachrichten blockieren,
- externe Lookup-Markierung blockiert,
- verbotener Write-Scope blockiert,
- Datenbankschema-Aenderung blockiert,
- Guard schreibt keine Dateien.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Write Guard Readiness Gate.
