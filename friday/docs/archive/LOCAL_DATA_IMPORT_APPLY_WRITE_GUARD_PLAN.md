# Local Data Import Apply Write Guard Plan

## Ziel

Dieses Dokument plant einen spaeteren side-effect-free Guard fuer einen moeglichen lokalen Import-Apply-Write.

Der Schritt ist bewusst plan-only:

- keine Produktlogik,
- keine Tests,
- kein Guard-Code,
- kein Import,
- kein aktiver SQLite-Write,
- keine Datenbankschema-Aenderung,
- keine Abfrage von `IMPORT ANWENDEN`.

## Ausgangsstand

Bereits dokumentiert und abgeschlossen sind:

- Local Data Import Apply Policy Plan,
- Local Data Import Apply Preview Model,
- Local Data Import/Export Final Acceptance Gate,
- Local Data Import Apply Write Plan.

Der echte Import bleibt weiterhin nicht freigegeben.

## Guard-Aufgabe

Ein spaeterer Import-Apply-Write-Guard soll vor jedem echten Import entscheiden:

- Ist die Import-Grundlage gueltig?
- Ist der Dry-Run erfolgreich?
- Ist ein Schutz-Backup vorhanden?
- Sind keine Konflikte offen?
- Sind keine sensiblen oder verbotenen Daten enthalten?
- Wurde der harte Token exakt eingegeben?
- Bleibt der Write lokal und begrenzt?

Der Guard darf selbst nichts schreiben.

## Vorgeschlagene Guard-Eingaben

| Eingabe | Zweck |
|---|---|
| Manifest-Status | pruefen, ob `manifest.json` valide ist |
| Dry-Run-Status | pruefen, ob Exportdateien read-only akzeptiert wurden |
| Apply-Preview-Status | pruefen, ob die Vorschau tokenfaehig ist |
| Backup-Schutz-Status | pruefen, ob lokaler Schutz vor Write vorhanden ist |
| Konfliktliste | offene Konflikte blockieren |
| Sensitive-Data-Ergebnis | sensible Kontakt-Freitexte blockieren |
| Safety-Smoke-Ergebnis | Import bei Scanner-Fehler blockieren |
| Zielbereich | nur erlaubte lokale Datenbereiche zulassen |
| Nutzer-Token | nur exaktes `IMPORT ANWENDEN` erlauben |

## Vorgeschlagene Guard-Ausgabe

Ein spaeteres Guard-Modell sollte nur ein Ergebnisobjekt liefern:

| Feld | Bedeutung |
|---|---|
| `allowed` | `True` nur, wenn alle Bedingungen erfuellt sind |
| `status` | z. B. `allowed`, `blocked`, `invalid`, `warnings` |
| `blocked_reasons` | Liste harter Blockiergruende |
| `warnings` | Hinweise ohne direkte Freigabe |
| `required_token` | immer `IMPORT ANWENDEN` |
| `write_scope` | erlaubte lokale Zielbereiche |
| `external_action_used` | muss immer `False` sein |
| `database_schema_change_required` | muss fuer diesen Block `False` bleiben |

## Harte Blockierregeln

Der Guard muss `allowed = False` liefern bei:

- fehlendem Manifest,
- ungueltigem Manifest,
- fehlgeschlagenem Import Dry-Run,
- Apply-Preview-Status `blocked` oder `invalid`,
- fehlendem Backup-Schutz,
- Safety Smoke FAIL,
- offenen Konflikten,
- sensiblen Kontakt-Freitexten,
- privaten Roh-Nachrichten,
- Secrets, `.env`, Tokens oder API-Keys,
- Obsidian Vault-Inhalten,
- Zielbereich ausserhalb lokaler Friday-Daten,
- unbekanntem Datenbereich,
- externer Lookup-Markierung,
- fehlendem Token,
- Token ungleich `IMPORT ANWENDEN`.

## Token-Regel

Nur exakt:

```text
IMPORT ANWENDEN
```

darf spaeter erlaubt sein.

Explizit blockiert bleiben:

- `ja`,
- `JA`,
- `ok`,
- `import`,
- `Import anwenden`,
- `IMPORT`,
- leere Eingabe,
- Eingaben mit fuehrenden oder nachgestellten Zeichen.

## Erlaubter Write-Scope

Ein spaeterer Guard darf nur lokale, explizit geplante Bereiche als denkbar markieren:

| Bereich | Guard-Status |
|---|---|
| Aufgaben | spaeter denkbar, wenn konfliktfrei |
| Kontakt-Kontexte | spaeter denkbar, nur mit Consent und ohne sensible Freitexte |
| Review-Status | spaeter optional, nur lokal |
| Safety-Status | blockiert fuer Write |
| aktive SQLite-Rohdatei | blockiert |
| Secrets / `.env` | blockiert |
| Obsidian Vault | blockiert |
| private Roh-Nachrichten | blockiert |

## Side-Effect-Free-Regel

Der spaetere Guard darf:

- keine Dateien schreiben,
- keine SQLite-Daten veraendern,
- keine Ordner erstellen,
- keine externen Aktionen ausfuehren,
- keine Netzwerkaufrufe machen,
- keine Secrets lesen,
- kein `input()` verwenden,
- kein `print()` verwenden.

## Empfohlene Tests fuer einen spaeteren Guard-Model-Step

Wenn das Guard-Modell spaeter implementiert wird, sollten Tests pruefen:

- erlaubt nur bei komplett gueltigem Status und exakt `IMPORT ANWENDEN`,
- blockiert ohne Token,
- blockiert bei `ja`,
- blockiert bei `JA`,
- blockiert bei `Import anwenden`,
- blockiert bei fehlendem Backup-Schutz,
- blockiert bei Dry-Run-Fehler,
- blockiert bei Preview `blocked`,
- blockiert bei Konflikten,
- blockiert bei sensiblen Kontakt-Freitexten,
- blockiert bei Secrets,
- blockiert bei externer Lookup-Markierung,
- schreibt keine Dateien,
- veraendert keine SQLite-Daten.

## Nicht-Ziele

Dieser Plan baut nicht:

- Guard-Code,
- Import-Write,
- CLI-Token-Abfrage,
- Datenbankmigration,
- Konfliktloesungs-UI,
- echten Restore,
- externe Provider,
- Netzwerkaktionen.

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein Import implementiert.
- Kein Guard-Code implementiert.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Write Guard Model.

Dieser Schritt sollte ein isoliertes, side-effect-free Guard-Modell mit Tests bauen, aber weiterhin keinen echten Import-Write ausfuehren.
