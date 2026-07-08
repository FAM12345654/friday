# Local Data Import Apply Policy Plan

## Ziel

Dieses Dokument plant die Policy fuer einen moeglichen spaeteren lokalen Import-Apply-Schritt. Es wird noch kein Import implementiert und kein Restore freigegeben.

Der aktuelle Stand bleibt:

- Manifest Reader ist read-only.
- Import Dry-Run ist read-only.
- CLI Import-Review ist read-only.
- Aktive Friday-Daten werden nicht veraendert.

## Grundregel

Ein spaeterer Import-Apply darf nur nach mehreren Gates geplant werden:

1. Exportordner wurde per Manifest Reader geprueft.
2. Import Dry-Run ist erfolgreich.
3. Keine Blockiergruende sind offen.
4. Nutzer sieht eine klare Import-Vorschau.
5. Nutzer bestaetigt mit hartem Token.
6. Import schreibt nie direkt ohne Backup-Schutz.

## Harte Nicht-Ziele

Dieser Plan erlaubt nicht:

- In-Place-Restore,
- direktes Ersetzen der aktiven SQLite-Datenbank,
- automatisches Zusammenfuehren ohne Preview,
- Import von Secrets,
- Import von `.env`,
- Import von API-Keys oder Tokens,
- Import von Obsidian Vaults,
- Import privater Roh-Nachrichten,
- externe Provider-Aufrufe,
- Netzwerkaktionen.

## Erlaubter spaeterer Zielumfang

Ein spaeterer Import-Apply duerfte nur lokale, explizit freigegebene Datenbereiche betreffen:

| Datenbereich | Spaeter denkbar? | Bedingung |
|---|---|---|
| Aufgaben-Zusammenfassungen | ja | nur nach Dry-Run, Preview und hartem Token |
| Kontakt-Kontexte | ja | nur consent-geprueft und ohne sensible Freitexte |
| Review-Status | eventuell | nur status-schonend und ohne externe Aktion |
| Safety-Status | nein | nur anzeigen, nicht importieren |
| aktive SQLite-Rohdatei | nein | niemals direkt ersetzen |
| Secrets / `.env` / Tokens | nein | immer ausgeschlossen |
| Obsidian Vault | nein | nicht Teil des Imports |

## Vorgeschlagener harter Token

Ein spaeterer Import-Apply sollte nicht `JA` oder `ja` verwenden.

Vorgeschlagener Token:

```text
IMPORT ANWENDEN
```

Regeln:

- Nur exakt `IMPORT ANWENDEN` darf einen spaeteren Import-Apply freigeben.
- Leere Eingabe bricht ab.
- `ja`, `JA`, `ok`, `import` und aehnliche weiche Antworten duerfen nicht anwenden.
- Vor dem Token muss eine klare Vorschau angezeigt werden.

## Backup-Pflicht vor Import

Vor einem spaeteren Import-Apply muss ein lokaler Schutzmechanismus definiert werden:

- vorhandene aktive Daten vorher sichern,
- Backup-Ziel nur unter `local_data/backups/`,
- keine Secrets sichern,
- keine Obsidian Vaults sichern,
- Backup-Ergebnis in der Import-Vorschau anzeigen.

Ohne erfolgreichen Backup-Schutz darf kein Import-Apply laufen.

## Konflikt-Policy

Konflikte duerfen nicht automatisch still geloest werden.

Spaetere Konfliktarten:

| Konflikt | Default |
|---|---|
| gleiche Task-ID | blockieren |
| gleicher Kontaktname | blockieren oder Vorschau |
| unterschiedlicher Status | blockieren |
| fehlendes Pflichtfeld | blockieren |
| sensible Kontaktdaten | blockieren |

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein Import implementiert.
- Kein Restore implementiert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Preview Plan.
