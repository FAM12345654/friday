# Local Data Import Apply CLI Write Preview Gate

## Ziel

Dieses Gate prueft den geplanten CLI-Pfad fuer einen spaeteren Local Data Import Apply Write, bevor eine Implementierung in Frage kommt.

Der Schritt bleibt bewusst Doku-only:

- keine Produktlogik,
- keine Tests,
- kein neuer Menuepunkt,
- keine CLI-Token-Abfrage,
- kein Import,
- kein aktiver SQLite-Write.

## Gepruefte Plan-Dokumente

| Dokument | Ergebnis |
|---|---|
| `LOCAL_DATA_IMPORT_APPLY_CLI_WRITE_PLAN.md` | CLI-Write-Pfad geplant |
| `LOCAL_DATA_IMPORT_APPLY_WRITER_READINESS_GATE.md` | isolierter Writer angenommen |
| `LOCAL_DATA_IMPORT_APPLY_WRITE_GUARD_READINESS_GATE.md` | Guard angenommen |
| `LOCAL_DATA_IMPORT_EXPORT_FINAL_ACCEPTANCE_GATE.md` | Export/Review/Preview-Block angenommen |

## Gepruefte CLI-Sicherheitsgrenzen

| Bereich | Ergebnis |
|---|---|
| Preview-Punkt bleibt read-only | bestaetigt |
| Echte Apply-Aktion braucht getrennten spaeteren Menuepunkt | bestaetigt |
| Token erst nach Guard `allowed = True` | bestaetigt |
| Exakter Token `IMPORT ANWENDEN` | bestaetigt |
| `ja` und `JA` bleiben ungueltig fuer Import Apply | bestaetigt |
| Backup-Schutz vor Writer | bestaetigt |
| Safety Smoke vor Writer | bestaetigt |
| Writer-Rollback muss angezeigt werden | bestaetigt |
| Kein In-Place-Restore | bestaetigt |
| Kein aktiver DB-Datei-Ersatz | bestaetigt |
| Keine externen Aktionen | bestaetigt |

## Preview-Gate Ergebnis

Der geplante CLI-Pfad ist ausreichend klar fuer eine spaetere Implementierungsplanung.

Freigegeben ist:

- weitere Planung eines getrennten CLI-Apply-Punkts,
- Nutzung von Preview, Dry-Run, Backup-Schutz, Guard und Writer als Pflichtkette,
- harte Token-Regel `IMPORT ANWENDEN`,
- Abbruch bei jedem Blockiergrund.

Nicht freigegeben ist:

- aktueller CLI-Import,
- neuer Menuepunkt im Produkt,
- Token-Abfrage im Produktfluss,
- aktiver SQLite-Write aus der CLI,
- Datenbankschema-Aenderung,
- In-Place-Restore,
- Konfliktloesungs-UI,
- externe Aktionen.

## Empfohlene Implementierungsgrenzen fuer spaeter

Wenn spaeter eine CLI-Implementierung gebaut wird, sollte sie klein bleiben:

- bestehende `7. Import-Apply-Vorschau anzeigen` unveraendert read-only lassen,
- neuen getrennten Punkt nur nach eigenem Implementierungsstep einfuehren,
- bei Guard `blocked` keinen Token abfragen,
- bei falschem Token nichts schreiben,
- Writer-Ergebnis immer anzeigen,
- Rollback-Faelle verstaendlich ausgeben.

## Teststatus

Aktueller Abschlussstand:

- `python -m pytest friday/tests` -> `674 passed`
- `python -m compileall friday` -> erfolgreich
- `python scripts/friday_safety_smoke.py` -> `Overall: PASS`
- `git diff --check` -> sauber

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein CLI-Import implementiert.
- Kein neuer Menuepunkt.
- Kein Import ausgefuehrt.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Gate Entscheidung

Local Data Import Apply CLI Write Preview Gate ist angenommen.

Der naechste Schritt darf die CLI-Implementierung planen oder vorbereiten. Ein echter CLI-Import bleibt bis zu einem eigenen Implementation- und Readiness-Gate gesperrt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply CLI Implementation Plan.

Dieser Schritt sollte weiterhin plan-only bleiben und exakt festlegen, welche Dateien spaeter fuer eine sichere CLI-Anbindung geaendert werden duerften.
