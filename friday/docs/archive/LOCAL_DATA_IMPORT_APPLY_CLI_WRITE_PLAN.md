# Local Data Import Apply CLI Write Plan

## Ziel

Dieses Dokument plant eine moegliche spaetere CLI-Anbindung fuer einen lokalen Import-Apply-Write.

Der Schritt ist bewusst plan-only:

- keine Produktlogik,
- keine Tests,
- kein neuer Menuepunkt,
- keine CLI-Token-Abfrage,
- kein Import,
- kein aktiver SQLite-Write,
- keine Datenbankschema-Aenderung.

## Ausgangsstand

Bereits vorhanden sind:

- read-only Manifest Reader,
- read-only Import Dry-Run,
- read-only Import Review CLI,
- read-only Import Apply Preview CLI,
- Import Apply Write Guard Model,
- Import Apply Writer Model,
- Writer Readiness Gate.

Ein echter Nutzer-Import in der CLI bleibt weiterhin nicht freigegeben.

## CLI-Grundregel

Eine spaetere CLI-Anbindung darf den Writer nur starten, wenn alle Vorbedingungen erfuellt sind:

1. Exportordner liegt unter `local_data/exports/`.
2. Manifest Reader ist erlaubt.
3. Import Dry-Run ist erlaubt.
4. Apply-Vorschau ist tokenfaehig.
5. Schutz-Backup ist vorhanden.
6. Safety Smoke ist erfolgreich.
7. Guard liefert `allowed = True`.
8. Nutzer bestaetigt exakt mit `IMPORT ANWENDEN`.
9. Writer schreibt nur erlaubte lokale Bereiche.
10. Fehler fuehren zu Rollback.

## Vorgeschlagener CLI-Ablauf

| Schritt | Anzeige / Aktion | Write? |
|---|---|---|
| 1. Exportordner abfragen | Pfad unter `local_data/exports/` | Nein |
| 2. Manifest anzeigen | Zusammenfassung und Counts | Nein |
| 3. Dry-Run anzeigen | Dateien, Warnungen, Blockiergruende | Nein |
| 4. Apply-Vorschau anzeigen | geplante Sektionen und Risiken | Nein |
| 5. Backup-Schutz pruefen | Backup vorhanden oder blockieren | Nein |
| 6. Safety Smoke ausfuehren | PASS erforderlich | Nein |
| 7. Guard-Ergebnis anzeigen | allowed/blocked und Gruende | Nein |
| 8. Token abfragen | nur bei Guard allowed | Nein |
| 9. Writer starten | nur bei exakt `IMPORT ANWENDEN` | Ja |
| 10. Ergebnis anzeigen | created/skipped/blocked/rollback | Nein |

## Vorgeschlagene Menue-Policy

Im Backup-/Restore-Menue sollte ein spaeterer echter Apply-Write nicht still den bestehenden Preview-Punkt ersetzen.

Empfehlung:

| Option | Zweck |
|---|---|
| `7. Import-Apply-Vorschau anzeigen` | bleibt read-only |
| neuer spaeterer Punkt | `Import nach Freigabe anwenden` |

Der neue Punkt darf erst nach eigenem Readiness Gate sichtbar werden.

## Token-Regel

Ein spaeterer CLI-Apply darf nur exakt diesen Token akzeptieren:

```text
IMPORT ANWENDEN
```

Blockiert bleiben:

- `ja`,
- `JA`,
- `ok`,
- `import`,
- `Import anwenden`,
- `IMPORT`,
- leere Eingabe,
- Eingaben mit fuehrenden oder nachgestellten Zeichen.

Der Token darf erst angezeigt werden, wenn der Guard `allowed = True` liefert.

## Nutzertexte

Spaetere CLI-Texte sollten klar machen:

- Import ist lokal.
- Es werden keine externen Dienste genutzt.
- Es wird kein In-Place-Restore ausgefuehrt.
- Aktive SQLite-Rohdatei wird nicht ersetzt.
- Sensible oder verbotene Daten blockieren.
- Bei Fehlern wird zurueckgerollt.

Beispiel:

```text
Import-Apply ist vorbereitet.
Es werden nur erlaubte lokale Zusammenfassungen importiert.
Zum Anwenden tippe exakt: IMPORT ANWENDEN
Enter oder jede andere Eingabe bricht ab.
```

## Blockierfaelle in der CLI

Die CLI muss abbrechen bei:

- Manifest-Fehler,
- Dry-Run-Fehler,
- fehlendem Backup-Schutz,
- Safety Smoke FAIL,
- Guard blockiert,
- falschem Token,
- Konflikten,
- sensiblen Kontakt-Freitexten,
- Secrets oder privaten Roh-Nachrichten,
- verbotenem Write-Scope,
- Writer-Rollback.

## Nicht-Ziele

Dieser Plan baut nicht:

- CLI-Anbindung,
- echten Import-Menuepunkt,
- Token-Abfrage im Produktfluss,
- Writer-Ausfuehrung aus dem Menue,
- Datenbankmigration,
- Konfliktloesungs-UI,
- In-Place-Restore,
- externe Provider,
- Netzwerkaktionen.

## Empfohlene Tests fuer einen spaeteren CLI-Implementation-Step

Wenn die CLI-Anbindung spaeter gebaut wird, sollten Tests mindestens pruefen:

- Preview-Punkt bleibt read-only,
- echter Apply-Punkt ist getrennt,
- falscher Token bricht ab,
- `ja` und `JA` wenden nicht an,
- exakt `IMPORT ANWENDEN` startet Writer nur bei Guard allowed,
- Guard blocked verhindert Token-Abfrage oder Write,
- Writer-Rollback wird verstaendlich angezeigt,
- keine externen Aktionen,
- keine Datenbankschema-Aenderung,
- keine In-Place-Restore-Aktion.

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein CLI-Import implementiert.
- Kein Import ausgefuehrt.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply CLI Write Preview Gate.

Dieser Schritt sollte vor einer Implementierung nochmals pruefen, ob die CLI-Sicherheitsgrenzen, Nutzertexte und getrennten Menuepfade eindeutig genug sind.
