# Local Data Import Manifest Reader Plan

## Ziel

Dieser Plan beschreibt, wie ein spaeterer Manifest Reader fuer lokale Datenexporte vorbereitet werden soll.

Der Schritt bleibt bewusst Planung:

- kein Manifest Reader,
- kein Import,
- kein Restore,
- kein Datei-Write,
- keine Produktlogik,
- keine Tests,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Der lokale Datenexport ist abgeschlossen und der spaetere Import-/Review-Flow ist als read-only Stufenmodell geplant.

Ein Import darf weiterhin niemals direkt aktive Daten ueberschreiben.

Der erste technische Baustein fuer einen spaeteren Import-Review waere ein Manifest Reader, der nur ein Export-Manifest liest, validiert und als strukturierte Vorschau zurueckgibt.

## Erlaubte Manifest-Felder

Ein spaeterer Manifest Reader darf nur technische Metadaten aus dem Export-Manifest lesen:

| Feld | Zweck | Pflicht |
|---|---|---|
| `export_type` | prueft, ob es ein Friday Local Data Export ist | ja |
| `export_version` | prueft kompatible Export-Struktur | ja |
| `created_at` | zeigt Erstellzeit des Exports | ja |
| `app_name` | prueft Friday-Zugehoerigkeit | ja |
| `storage_scope` | bestaetigt lokalen Export-Scope | ja |
| `sections` | listet enthaltene Exportbereiche | ja |
| `excluded_content` | dokumentiert ausgeschlossene sensible Inhalte | ja |
| `safety_smoke_required` | zeigt Safety-Smoke-Pflicht fuer Export/Import-Review | ja |
| `approval_token_used` | bestaetigt harten Export-Token | ja |

## Nicht erlaubte Manifest-Inhalte

Ein Manifest darf keine geheimen oder sensiblen Inhalte enthalten.

Blockierende Inhalte waeren:

- API Keys,
- Tokens,
- Passwoerter,
- `.env` Inhalte,
- Roh-Nachrichtentexte,
- sensible Kontakt-Freitexte,
- komplette SQLite-Rohdaten,
- Obsidian Vault Inhalte,
- absolute private Systempfade ausserhalb eines harmlosen Export-Hinweises.

## Blockierende Fehler

Ein spaeterer Manifest Reader muss blockieren, wenn:

- `manifest.json` fehlt,
- Manifest kein valides JSON ist,
- Pflichtfelder fehlen,
- `export_type` nicht Friday Local Data Export entspricht,
- `app_name` nicht `Friday` ist,
- `export_version` unbekannt oder inkompatibel ist,
- `storage_scope` nicht lokal ist,
- `excluded_content` fehlt oder ausgeschlossene Inhalte nicht dokumentiert,
- Manifest sensible Inhalte enthaelt,
- Manifest auf externe Provider, Cloud-Sync oder Netzwerkziele verweist.

## Read-only Ergebnis

Ein spaeterer Reader soll nur eine Vorschau erzeugen.

Beispiel:

```text
Manifest erkannt:
- Typ: Friday Local Data Export
- Version: 1
- Erstellt: 2026-07-07T21:30:00
- Bereiche: tasks, contacts, review, safety
- Externe Aktionen: keine
- Import-Write: nicht freigegeben
```

Dieses Ergebnis darf keine Daten importieren, keine Datenbank oeffnen und keine Dateien schreiben.

## Spaetere Teststrategie

Wenn der Manifest Reader umgesetzt wird, sollten Tests abdecken:

- gueltiges Manifest wird gelesen,
- fehlendes Manifest blockiert,
- ungueltiges JSON blockiert,
- fehlende Pflichtfelder blockieren,
- falscher Export-Typ blockiert,
- falscher App-Name blockiert,
- unbekannte Export-Version blockiert,
- nicht-lokaler Scope blockiert,
- sensible Manifest-Inhalte blockieren,
- Reader schreibt keine Datei,
- Reader oeffnet keine aktive SQLite-Datenbank.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Kein Manifest Reader implementiert.
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

Als naechster Schritt sollte `Local Data Import Manifest Reader Model` folgen.

Dieser Schritt sollte isoliert einen read-only Manifest Reader bauen:

- nur `manifest.json` lesen,
- nur erlaubte Felder auswerten,
- blockierende Fehler strukturiert melden,
- keine Import- oder Restore-Aktion,
- keine Datei schreiben,
- keine Datenbank oeffnen.
