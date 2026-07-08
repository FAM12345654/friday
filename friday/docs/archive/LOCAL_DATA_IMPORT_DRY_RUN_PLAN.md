# Local Data Import Dry-Run Plan

## Ziel

Dieser Plan beschreibt den naechsten sicheren Baustein fuer einen spaeteren lokalen Import-Review.

Der Dry-Run soll spaeter Exportinhalte nur pruefen und zusammenfassen.

Dieser Schritt bleibt bewusst Planung:

- kein Dry-Run-Modell,
- kein Import,
- kein Restore,
- kein Datei-Write,
- keine Produktlogik,
- keine Tests,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Der lokale Datenexport ist umgesetzt und freigegeben.

Der Manifest Reader ist umgesetzt und per Readiness Gate freigegeben:

- `manifest.json` wird read-only gelesen,
- gueltige Manifestdateien aus dem Export Writer werden akzeptiert,
- sensible oder externe Manifestinhalte werden blockiert,
- Import und Restore bleiben nicht freigegeben.

## Dry-Run-Grundregel

Ein spaeterer Import-Dry-Run darf nur feststellen:

- welche Exportdateien vorhanden sind,
- welche Sektionen laut Manifest erwartet werden,
- welche Dateien fehlen,
- welche Dateien ungueltig aussehen,
- welche Konflikte spaeter relevant waeren,
- welche Inhalte nicht importiert werden duerfen.

Er darf niemals:

- Daten importieren,
- aktive SQLite-Datenbanken oeffnen,
- aktive Daten ueberschreiben,
- Dateien in `local_data` veraendern,
- Exportdateien reparieren,
- Obsidian Vaults schreiben,
- externe Anbieter aufrufen.

## Geplante Eingaben

Ein spaeterer Dry-Run sollte nur diese Eingaben bekommen:

| Eingabe | Zweck |
|---|---|
| `export_root` | lokaler Exportordner unter `local_data/exports` |
| `manifest_result` | Ergebnis des Manifest Readers |
| `project_root` | Projektwurzel zur Pfadpruefung |

Wenn `manifest_result.allowed` nicht `True` ist, muss der Dry-Run blockieren.

## Geplante pruefbare Exportdateien

Der Dry-Run darf spaeter nur Dateien pruefen, die vom Export Writer erzeugt wurden:

| Datei | Pruefung |
|---|---|
| `manifest.json` | bereits durch Manifest Reader geprueft |
| `tasks/tasks.json` | JSON-Struktur und Anzahl |
| `tasks/tasks.md` | Existenz und Groesse |
| `contacts/contact_contexts.json` | JSON-Struktur, erlaubte Felder |
| `review/review_suggestions.json` | JSON-Struktur, erlaubte Felder |
| `safety/safety_status.json` | lokale Safety-Flags |
| `docs/export_notes.md` | Existenz und harmloser Hinweistext |

Nicht pruefen oder lesen:

- aktive SQLite-Rohdatenbank,
- `.env`,
- Secrets,
- API Keys,
- Tokens,
- Obsidian Vault,
- Cache-Dateien,
- private Roh-Nachrichtentexte.

## Geplante Ergebnisstruktur

Ein spaeteres Dry-Run-Ergebnis sollte enthalten:

```text
allowed
export_root
manifest_valid
sections_checked
missing_files
invalid_files
blocked_reasons
warnings
message
preview_only=True
persisted=False
external_lookup_used=False
```

## Blockierende Fehler

Der Dry-Run muss spaeter blockieren, wenn:

- Manifest Reader blockiert,
- Exportordner ausserhalb `local_data/exports` liegt,
- erwartete Dateien ausserhalb des Exportordners zeigen,
- JSON-Dateien ungueltig sind,
- sensible Felder in Kontakt- oder Review-Dateien auftauchen,
- Safety-Flags echte externe Aktionen aktivieren,
- Exportdateien verbotene Pfadbestandteile enthalten,
- `external_lookup_used` irgendwo `True` ist.

## Konfliktpruefung nur als Vorschau

Ein spaeterer Dry-Run darf Konflikte nur melden.

Beispiele:

- Aufgabe mit gleicher ID wuerde existieren,
- Kontakt mit gleicher ID wuerde existieren,
- Review-Vorschlag mit gleicher ID wuerde existieren,
- Export ist aelter als aktive Daten.

Diese Konflikte duerfen nicht automatisch geloest werden.

## Spaetere Teststrategie

Wenn das Dry-Run-Modell umgesetzt wird, sollten Tests abdecken:

- gueltiger Export wird read-only geprueft,
- blockiertes Manifest blockiert Dry-Run,
- fehlende Datei erzeugt Warning oder Block je nach Sektion,
- ungueltiges JSON blockiert,
- sensible Kontaktfelder blockieren,
- rohe private Nachrichtentexte blockieren,
- Safety-Flags mit echten externen Aktionen blockieren,
- Pfad ausserhalb Exportordner blockiert,
- Dry-Run schreibt keine Datei,
- Dry-Run oeffnet keine aktive SQLite-Datenbank.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Kein Dry-Run implementiert.
- Kein Import implementiert.
- Kein Restore implementiert.
- Keine Datei geschrieben.
- Keine Datenbank gelesen oder geschrieben.
- Keine Datenbankschema-Aenderung.
- Keine externe Aktion.
- Keine Netzwerkaktion.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Import Dry-Run Model` folgen.

Dieser Schritt sollte isoliert und read-only bleiben:

- Manifest Reader Ergebnis nutzen,
- Exportdateien pruefen,
- strukturierte Sections und Blockiergruende liefern,
- keine Import- oder Restore-Aktion,
- keine Datei schreiben,
- keine aktive Datenbank oeffnen.
