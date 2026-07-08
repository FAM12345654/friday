# Privacy Data Cleanup Policy Plan

## Ziel

Dieser Plan definiert, welche lokalen Datenbereiche spaeter ueber Privacy Data Management bereinigt werden duerften.

Der Schritt bleibt bewusst Plan-only:

- keine Produktlogik,
- keine CLI-Aenderung,
- keine Loeschfunktion,
- keine Exportfunktion,
- keine Importfunktion,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Grundprinzip

Privacy Cleanup darf spaeter nur gezielt, lokal und hart gegatet erfolgen.

Es gibt keine globale Aktion wie "alles loeschen".

Jede echte Bereinigung braucht:

- eigenes Implementierungs-Gate,
- eigenes Readiness-Gate,
- klare Vorschau,
- harten Approval-Token,
- Safety Smoke PASS, falls ein Write/Delete ausgefuehrt wird,
- Tests mit `tmp_path`, falls Dateien oder SQLite betroffen sind.

## Policy-Matrix

| Datenbereich | Spaeter bereinigbar? | Erlaubte Idee | Nicht erlaubt | Erforderliches spaeteres Gate |
|---|---|---|---|---|
| Aufgaben | Nein im Privacy Cleanup | Pflege bleibt im bestehenden Task-Menue | Massenloeschung ueber Privacy Dashboard | Task Cleanup Gate separat |
| Kontakt-Kontexte | Nur gezielt | Einzelnen Kontakt-Kontext vergessen | Alle Kontakte auf einmal loeschen | Contact Cleanup Approval Gate |
| Review-Vorschlaege | Nur lokal und statusbasiert | alte abgelehnte/converted Vorschlaege bereinigen | pending Vorschlaege automatisch loeschen | Review Cleanup Approval Gate |
| Exporte | Ja, lokal und ordnerbasiert | alte Exportordner unter `local_data/exports/` entfernen | Dateien ausserhalb `local_data/exports/` entfernen | Export Cleanup Approval Gate |
| Backups | Ja, lokal und ordnerbasiert | alte Backupordner unter `local_data/backups/` entfernen | neuestes Backup automatisch loeschen | Backup Cleanup Approval Gate |
| Restore-Kopien | Ja, lokal und ordnerbasiert | alte Restore-Kopien unter `local_data/restores/` entfernen | aktive Datenbank ersetzen oder loeschen | Restore Copy Cleanup Approval Gate |
| Import-Reviews | Nur read-only oder ordnerbasiert | alte Export-/Reviewordner markieren oder entfernen | Import-Apply Rueckgaengig machen | Import Review Cleanup Gate |
| Obsidian-Previews/Writes | Nein im Privacy Cleanup | nur Status anzeigen | Vault scannen oder Notizen loeschen | Eigenes Obsidian Cleanup Gate |
| Safety-Scanner | Nein | Scannerstatus anzeigen | Scannerdateien entfernen | nicht vorgesehen |
| `.env` / Secrets | Nein | dauerhaft ausgeschlossen | anzeigen, exportieren oder loeschen | nicht vorgesehen |
| aktive SQLite-DB | Nein | nur Status anzeigen | direkt loeschen, ersetzen oder ueberschreiben | nicht vorgesehen |

## Harter Token-Plan

Tokens werden erst in spaeteren Implementierungs-Gates final festgelegt.

Vorlaeufige Policy:

| Aktion | Vorgeschlagener spaeterer Token | Status |
|---|---|---|
| Exportordner bereinigen | `EXPORT AUFRAEUMEN` | nur geplant |
| Backupordner bereinigen | `BACKUP AUFRAEUMEN` | nur geplant |
| Restore-Kopien bereinigen | `RESTORE AUFRAEUMEN` | nur geplant |
| Review-Vorschlaege bereinigen | `REVIEW AUFRAEUMEN` | nur geplant |
| Kontakt-Kontext gezielt vergessen | bestehend: `KONTAKT LÖSCHEN` | bereits im Kontakt-Menue gegatet |

Wichtig:

- `JA` darf fuer neue Privacy-Cleanup-Aktionen nicht verwendet werden.
- `ja` darf fuer neue Privacy-Cleanup-Aktionen nicht verwendet werden.
- Bestehende Delete-Policy fuer Aufgaben bleibt unveraendert.

## Mindestanforderungen fuer spaetere Umsetzung

Jede spaetere Cleanup-Implementierung muss:

- vor dem Token eine read-only Vorschau anzeigen,
- nur erlaubte lokale Pfade verwenden,
- Pfade normalisieren und auf erlaubte Wurzeln pruefen,
- keine freien Zielpfade akzeptieren,
- keine aktiven Datenbankdateien loeschen,
- keine `.env`, Secrets, API-Keys oder Caches anfassen,
- keine externen Dienste aufrufen,
- keine Netzwerkaktionen ausfuehren,
- nach Abbruch nichts veraendern,
- bei falschem Token nichts veraendern.

## Nicht-Ziele

- Keine Implementierung in diesem Schritt.
- Keine CLI-Anbindung in diesem Schritt.
- Kein neuer Menuepunkt.
- Kein neues Repository.
- Keine Datenmigration.
- Kein In-Place-Restore.
- Kein Obsidian Vault Cleanup.
- Keine automatische Bereinigung.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Loeschpfade.
- Keine neuen Exportpfade.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Data Cleanup Policy Readiness Gate`

Ziel: Pruefen und dokumentieren, dass die Cleanup-Policy keine Implementierung freischaltet und alle riskanten Bereiche weiterhin blockiert.
