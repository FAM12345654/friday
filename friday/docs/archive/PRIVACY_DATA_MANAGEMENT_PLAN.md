# Privacy Data Management Plan

## Ziel

Dieser Plan beschreibt, wie Friday spaeter lokale Datenpflege sichtbar und sicher anbieten soll.

Der Schritt bleibt bewusst Plan-only:

- keine Produktlogik,
- keine neuen CLI-Aktionen,
- keine Loeschfunktion,
- keine neuen Schreibpfade,
- keine externen Aktionen,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Friday hat bereits ein read-only Privacy Dashboard.

Dieses Dashboard zeigt lokal:

- bekannte Datenbereiche,
- Safety-Flags,
- deaktivierte externe Aktionen,
- harte Approval-Tokens,
- vorhandene Safety-Scanner.

Das Dashboard bleibt im aktuellen Stand rein lesend. Es loescht nichts, exportiert nichts, importiert nichts und aktiviert keine externen Dienste.

## Geplante Datenbereiche

| Bereich | Sichtbarkeit | Spaetere Pflege-Idee | Safety-Grenze |
|---|---|---|---|
| Aufgaben | Anzahl, Status und lokaler SQLite-Bezug | Pflege weiter ueber vorhandene Task-Flows | Keine neue Massenloeschung ohne eigenes Gate |
| Kontakt-Kontexte | Anzahl und Typen ohne sensible Details | Anzeigen, Suchen, Bearbeiten oder Vergessen nur mit klarer Freigabe | Sensitive Freitexte nicht ungeprueft anzeigen oder exportieren |
| Review-Vorschlaege | Anzahl und Status | Spaeter optional lokale Bereinigung alter Vorschlaege | Keine echte Nachricht, kein echter Versand |
| Exporte | Lokaler Pfad und Anzahl | Spaeter alte Exportordner auflisten und gezielt bereinigen | Nur unter `local_data/exports/` |
| Backups | Lokaler Pfad und Anzahl | Spaeter alte Backupordner auflisten und gezielt bereinigen | Aktive Datenbank nie direkt ersetzen |
| Restore-Kopien | Lokaler Pfad und Anzahl | Spaeter alte Restore-Kopien auflisten und gezielt bereinigen | Kein In-Place-Restore |
| Import-Reviews | Manifest-/Dry-Run-Status | Spaeter alte Import-Pruefungen nachvollziehbar anzeigen | Kein Import ohne Backup, Guard, Safety Smoke und hartes Token |
| Obsidian-Previews/Writes | Status von Preview, Guard und Write-Freigabe | Spaeter Write-Historie lokal sichtbar machen | Kein Vault-Scan, kein Write ohne Token |
| Safety-Scanner | PASS/FAIL-Status und Scannerliste | Spaeter zentralen Scanner-Smoke einfacher ausfuehren | Keine Provider- oder Netzwerkaktionen |

## Grundregeln fuer spaetere Datenpflege

- Datenpflege muss lokal bleiben.
- Jede Loesch- oder Schreibaktion braucht ein eigenes spaeteres Gate.
- Harte Tokens werden pro Aktion separat festgelegt.
- Bestehende Tokens bleiben unveraendert.
- Es gibt keine Sammelaktion wie "alles loeschen" ohne eigenes Safety-Konzept.
- `.env`, Secrets, API-Keys, Caches und Obsidian Vaults bleiben ausgeschlossen.
- Aktive SQLite-Dateien werden nicht direkt ueberschrieben.
- Externe Integrationen bleiben deaktiviert.

## Nicht-Ziele dieses Plans

- Kein neuer CLI-Menuepunkt.
- Kein Datenexport.
- Kein Datenimport.
- Kein Backup oder Restore.
- Keine Kontaktloeschung.
- Keine Task-Massenaktion.
- Keine Obsidian-Aktion.
- Keine automatische Bereinigung.
- Keine Persistenz sensibler Zusatzdaten.

## Empfohlener naechster technischer Schritt

Der naechste kleine Schritt sollte ein read-only Inventory-Modell sein:

`Privacy Data Management Read-Only Inventory Model`

Dieses Modell sollte nur zusammenfassen:

- welche lokalen Datenbereiche vorhanden sind,
- welche Pfade relevant sind,
- welche Bereiche spaeter pflegbar waeren,
- welche Bereiche blockiert bleiben,
- welche Safety-Grenzen gelten.

Auch dieses Modell darf noch nicht loeschen, schreiben, exportieren oder externe Aktionen ausfuehren.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.
- Privacy Dashboard bleibt read-only.
