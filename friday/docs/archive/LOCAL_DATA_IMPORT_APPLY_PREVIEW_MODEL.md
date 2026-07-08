# Local Data Import Apply Preview Model

## Ziel

Dieser Schritt ergaenzt ein isoliertes, side-effect-free Modell fuer eine spaetere lokale Import-Apply-Vorschau.

Das Modell zeigt nur, ob eine spaetere Import-Anwendung grundsaetzlich angefragt werden duerfte. Es importiert nichts, schreibt nichts und veraendert keine aktive Friday-Datei.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/local_data_import_apply_preview.py` | Read-only Apply-Preview-Modell |
| `friday/tests/test_local_data_import_apply_preview.py` | Unit-Tests fuer Preview-Status, Backup-Pflicht und Blockiergruende |

## Modell-Verhalten

Das Modell nutzt bereits gepruefte Eingaben:

- Manifest Reader Ergebnis,
- Import Dry-Run Ergebnis,
- Backup-Schutz-Status,
- optionale Konfliktwarnungen.

Es erzeugt:

- Vorschau-Status,
- geplante lokale Sektionen,
- Blockiergruende,
- Warnungen,
- erforderlichen harten Token `IMPORT ANWENDEN`.

## Statuswerte

| Status | Bedeutung |
|---|---|
| `preview_ready` | Vorschau ist bereit und spaeterer Token duerfte angefragt werden |
| `warnings` | Vorschau hat Warnungen, bleibt aber tokenfaehig |
| `blocked` | Vorschau blockiert, Token darf nicht angefragt werden |
| `invalid` | Manifest-/Exportgrundlage ist ungueltig |

## Harte Blockiergruende

Das Modell blockiert bei:

- blockiertem Manifest,
- blockiertem Dry-Run,
- fehlendem Backup-Schutz,
- Konflikten,
- externer Lookup-Markierung.

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

- valide Exportdaten mit Backup erzeugen `preview_ready`,
- fehlender Backup-Schutz blockiert,
- blockierter Dry-Run blockiert,
- blockiertes Manifest erzeugt `invalid`,
- Konflikte blockieren,
- externe Lookup-Markierung bleibt blockiert,
- Modell schreibt keine Dateien.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Preview Readiness Gate.
