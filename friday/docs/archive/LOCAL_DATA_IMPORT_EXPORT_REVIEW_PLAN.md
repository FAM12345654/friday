# Local Data Import / Export Review Plan

## Ziel

Dieser Plan beschreibt, ob und wie ein spaeterer sicherer Import- oder Review-Flow fuer lokale Daten aussehen darf.

Der Schritt ist bewusst nur Planung:

- kein Import,
- kein Restore,
- kein Datei-Write,
- keine Produktlogik,
- keine Tests,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Der lokale Datenexport ist abgeschlossen und freigegeben:

- Export-Preview ist stabil.
- Export-Guard ist stabil.
- Export-Writer ist stabil.
- CLI-Export ist lokal nutzbar.
- Token `DATEN EXPORTIEREN` ist Pflicht.
- Safety Smoke PASS ist Pflicht.
- Exportziel bleibt `local_data/exports`.

Ein Import ist noch nicht freigegeben.

## Grundsatzentscheidung

Ein spaeterer Import darf niemals direkt aktive Daten ueberschreiben.

Stattdessen muss ein Import in Stufen geplant werden:

1. Exportordner auswaehlen.
2. Manifest lesen.
3. Import-Dry-Run erzeugen.
4. Inhalte nur als Review anzeigen.
5. Konflikte sichtbar machen.
6. Import-Vorschau dokumentieren.
7. Harte Freigabe fuer einzelne sichere Aktionen separat planen.

## Nicht-Ziele

Nicht gebaut oder nicht freigegeben werden:

- automatischer Import,
- direkter Write in `local_data/friday.db`,
- Ersetzen aktiver Daten,
- Merge ohne Review,
- Import von Secrets,
- Import von `.env`,
- Import von Obsidian Vault,
- Import von Roh-Nachrichten,
- Import sensibler Kontakt-Freitexte,
- Cloud-Sync,
- externe Provider.

## Geplanter Review-Flow

Ein spaeterer Review-Flow koennte so aussehen:

```text
1. Exportordner pruefen
2. Manifest anzeigen
3. Import-Dry-Run anzeigen
4. Unterschiede anzeigen
5. Konflikte anzeigen
6. Keine Daten schreiben
7. Zurueck
```

Dieser Flow waere zunaechst read-only.

## Erforderliche Guards vor einem spaeteren Import

Ein spaeterer Import braucht eigene Schutzbausteine:

| Guard | Zweck |
|---|---|
| Manifest Guard | prueft Export-Typ, Version, Struktur und Pflichtdateien |
| Path Guard | erlaubt nur lokale Exportordner unter `local_data/exports` oder explizit erlaubte lokale Importpfade |
| Safety Smoke Guard | blockiert bei Safety Smoke FAIL |
| Sensitive Data Guard | blockiert sensible Freitexte und ausgeschlossene Rohdaten |
| Conflict Guard | erkennt doppelte IDs, aeltere Daten und Statuskonflikte |
| Write Guard | verhindert aktive Writes ohne spaeteres eigenes hartes Token |

## Moeglicher harter Token fuer spaetere Writes

Falls spaeter ein Import-Write geplant wird, sollte er einen eigenen Token bekommen.

Vorschlag:

```text
DATEN IMPORTIEREN
```

Dieser Token darf nicht in diesem Plan aktiviert werden.

## Datenbereiche

Ein spaeterer Import-Review duerfte nur folgende Bereiche pruefen:

- Aufgaben-Zusammenfassungen,
- Kontakt-Kontext-Zusammenfassungen,
- Review-/Vorschlags-Status,
- Safety-Status,
- Manifest.

Nicht geprueft oder importiert werden sollen:

- aktive SQLite-Datenbank als Rohdatei,
- `.env`,
- Secrets,
- API-Keys,
- Tokens,
- Obsidian Vault,
- volle private Roh-Nachrichtentexte,
- sensible Kontakt-Freitexte.

## Teststrategie fuer spaetere Schritte

Wenn der Import-/Review-Block gebaut wird, sollten Schritte getrennt bleiben:

1. Import Review Plan.
2. Import Manifest Reader Model.
3. Import Dry-Run Model.
4. Import Review CLI Read-Only Preview.
5. Import Review Readiness Gate.
6. Erst danach eine separate Write-Planung.

Moegliche Tests:

- gueltiger Exportordner wird erkannt,
- fehlendes Manifest blockiert,
- falscher Export-Typ blockiert,
- Export ausserhalb erlaubter Pfade blockiert,
- ausgeschlossene Inhalte blockieren,
- Review zeigt Konflikte,
- Dry-Run schreibt nichts,
- falscher Token schreibt nichts,
- aktiver DB-Write bleibt nicht moeglich.

## Safety-Bewertung

- Keine Produktlogik geaendert.
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

Als naechster Schritt sollte `Local Data Import Manifest Reader Plan` folgen.

Dieser Schritt sollte nur planen:

- welche Manifest-Felder gelesen werden duerfen,
- welche Pflichtfelder erforderlich sind,
- welche Fehler blockieren,
- dass weiterhin nichts geschrieben wird.
