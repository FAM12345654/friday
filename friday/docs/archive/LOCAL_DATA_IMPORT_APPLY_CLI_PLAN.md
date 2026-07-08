# Local Data Import Apply CLI Plan

## Ziel

Dieses Dokument plant eine spaetere CLI-Anbindung fuer die lokale Import-Apply-Vorschau. Es wird noch keine CLI-Implementierung gebaut und kein Import freigegeben.

Die spaetere CLI soll zuerst nur die Apply-Vorschau anzeigen. Ein echter Apply-Schritt bleibt bis zu separaten Gates gesperrt.

## Ausgangslage

Bereits vorhanden:

- Manifest Reader,
- Import Dry-Run,
- read-only Import-Review im Backup-/Restore-Menue,
- Apply Policy Plan,
- Apply Preview Plan,
- isoliertes Apply-Preview-Modell,
- Apply Preview Readiness Gate.

## Geplanter CLI-Pfad

Spaeterer Menuepfad im Backup-/Restore-Bereich:

```text
Backup / Restore
6. Lokalen Datenimport pruefen
7. Import-Apply-Vorschau anzeigen
8. Zurueck zum Hauptmenue
```

Hinweis: Die konkrete Nummerierung muss im Implementierungsschritt mit dem aktuellen Menue abgeglichen werden.

## Geplanter Ablauf

1. Nutzer waehlt Import-Apply-Vorschau.
2. Friday fragt nach einem lokalen Exportordner.
3. Friday liest `manifest.json` read-only.
4. Friday fuehrt Import Dry-Run read-only aus.
5. Friday baut Apply-Preview.
6. Friday zeigt Status, Sektionen, Warnungen und Blockiergruende.
7. Friday fragt noch keinen Apply-Token ab.
8. Friday schreibt nichts.

## CLI-Ausgabe

Die spaetere Ausgabe sollte klar enthalten:

- Exportordner,
- Manifest-Status,
- Dry-Run-Status,
- Backup-Schutz-Status,
- geplante Sektionen,
- Blockiergruende,
- Warnungen,
- Hinweis: `Es wurde nichts importiert.`,
- Hinweis: `Es wurde nichts geschrieben.`,
- Hinweis: `Import anwenden ist noch nicht freigegeben.`

## Harte Grenzen

Die CLI-Planung erlaubt nicht:

- Import anwenden,
- Restore in aktive Friday-Daten,
- In-Place-Restore,
- aktiven SQLite-Write,
- automatische Konfliktloesung,
- Import von Secrets,
- Import privater Roh-Nachrichten,
- externe Provider,
- Netzwerkaktionen.

## Spaeterer Testplan

Wenn die CLI-Anbindung spaeter umgesetzt wird, sollten Tests pruefen:

- Menue zeigt Import-Apply-Vorschau-Pfad.
- Leere Eingabe und `z` kehren stabil zurueck.
- Gueltiger Exportordner zeigt Preview.
- Blockierter Dry-Run zeigt Blockiergruende.
- Fehlender Backup-Schutz blockiert.
- Kein Token wird abgefragt.
- Kein Import wird ausgefuehrt.
- Keine Datei wird geschrieben.
- Safety-Smoke bleibt PASS.

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein Import implementiert.
- Kein Restore implementiert.
- Keine CLI-Anbindung implementiert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply CLI Preview Implementation.
