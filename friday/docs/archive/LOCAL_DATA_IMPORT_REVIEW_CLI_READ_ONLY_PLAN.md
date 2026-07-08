# Local Data Import Review CLI Read-Only Plan

## Ziel

Dieser Plan beschreibt, wie ein spaeterer CLI-Menuepunkt fuer lokalen Datenimport-Review aussehen darf.

Der CLI-Flow soll nur anzeigen und pruefen:

- Exportordner auswaehlen,
- Manifest Reader ausfuehren,
- Import Dry-Run ausfuehren,
- Ergebnis read-only anzeigen,
- zurueck ins Menue.

Dieser Schritt bleibt bewusst Planung:

- keine CLI-Implementierung,
- kein Import,
- kein Restore,
- kein Datei-Write,
- keine Produktlogik,
- keine Tests,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Vorhandene sichere Bausteine:

| Baustein | Status |
|---|---|
| Local Data Export Writer | umgesetzt |
| Local Data Import Manifest Reader | umgesetzt, read-only |
| Local Data Import Dry-Run | umgesetzt, read-only |
| Import Dry-Run Readiness Gate | abgeschlossen |

Import und Restore bleiben weiterhin nicht freigegeben.

## Geplanter CLI-Ort

Der spaetere Review-Flow sollte im Backup-/Restore-/Daten-Menue liegen.

Vorgeschlagene Menue-Erweiterung:

```text
Backup / Restore / Daten
1. Backup-Vorschau anzeigen
2. Backup erstellen
3. Restore Dry-Run anzeigen
4. Restore-Kopie erstellen
5. Lokalen Datenexport pruefen / erstellen
6. Lokalen Datenimport pruefen
7. Zurueck
```

Falls bestehende Nummern anders sind, soll die spaetere Implementierung die vorhandene Menuestruktur respektieren und nur minimal erweitern.

## Geplanter Ablauf

```text
Lokalen Datenimport pruefen

Pfad zum Exportordner eingeben:
> local_data/exports/friday_data_export_YYYYMMDD_HHMMSS

1. Manifest pruefen
2. Dry-Run ausfuehren
3. Ergebnis anzeigen
4. Zurueck
```

Der Flow darf keine harte Import-Freigabe abfragen, weil Import weiterhin nicht freigegeben ist.

## Erwartete Ausgaben

Bei gueltigem Export:

```text
Import-Review wurde read-only geprueft.
Es wurde nichts importiert.
Es wurde nichts wiederhergestellt.
Es wurde nichts geschrieben.
```

Bei blockiertem Manifest:

```text
Import-Review wurde blockiert.
Grund: Manifest ist ungueltig oder nicht freigegeben.
Es wurde nichts importiert.
```

Bei blockiertem Dry-Run:

```text
Import Dry-Run wurde blockiert.
Bitte pruefe die angezeigten Gruende.
Es wurde nichts importiert.
```

## Ruecksprung- und Abbruchregeln

Der spaetere CLI-Flow sollte stabil bleiben bei:

- leerer Eingabe,
- Whitespace,
- nicht vorhandenem Pfad,
- Pfad ausserhalb `local_data/exports`,
- ungueltigem Manifest,
- blockiertem Dry-Run,
- Ruecksprung mit `z`,
- Ruecksprung mit leerer Eingabe, falls im Projektmuster passend.

Jede dieser Situationen darf keine Datei schreiben und keine Datenbank veraendern.

## Nicht-Ziele

Nicht freigegeben sind:

- Import ausfuehren,
- Restore ausfuehren,
- aktiven DB-Write ausfuehren,
- In-Place-Restore,
- Merge aktiver Daten,
- Konflikte automatisch loesen,
- Exportdateien reparieren,
- Secrets importieren,
- Obsidian Vault importieren,
- Roh-Nachrichten importieren,
- externe Provider nutzen.

## Spaetere Teststrategie

Wenn der CLI-Read-Only-Review umgesetzt wird, sollten Tests abdecken:

- Menuepunkt ist sichtbar.
- Ruecksprung funktioniert.
- gueltiger Export zeigt Manifest- und Dry-Run-Ergebnis.
- blockiertes Manifest zeigt klare Fehlermeldung.
- blockierter Dry-Run zeigt klare Fehlermeldung.
- leerer Pfad bleibt stabil.
- Pfad ausserhalb `local_data/exports` blockiert.
- keine Datei wird geschrieben.
- keine aktive SQLite-Datenbank wird geoeffnet oder veraendert.
- Safety Smoke bleibt PASS.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine CLI-Implementierung.
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

Als naechster Schritt sollte `Local Data Import Review CLI Read-Only Implementation` folgen.

Dieser Schritt sollte den CLI-Pfad nur read-only einbauen:

- Exportordner abfragen,
- Manifest Reader ausfuehren,
- Import Dry-Run ausfuehren,
- Ergebnis anzeigen,
- keine Import-/Restore-/Write-Aktion anbieten.
