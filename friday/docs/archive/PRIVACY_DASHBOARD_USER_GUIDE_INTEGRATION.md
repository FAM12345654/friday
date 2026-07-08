# Privacy Dashboard User Guide Integration

## Ziel

Dieses Dokument beschreibt die Nutzer-Doku-Ergaenzung fuer die read-only Anzeige- und Count-Bereiche im Privacy Dashboard.

Der Nutzer soll verstehen:

- wo das Privacy Dashboard zu finden ist,
- was dort angezeigt wird,
- dass Anzeige- und Count-Bereiche nichts loeschen, exportieren oder schreiben,
- dass externe Aktionen deaktiviert bleiben.

## Nutzer-Doku

`README_USER.md` enthaelt jetzt einen Abschnitt zu:

- `12. Privacy Dashboard`,
- lokale Datenbereiche,
- read-only Counts fuer Aufgaben, Kontakte, Kontakt-Kontexte, Review-Vorschlaege, Backups und Restore-Kopien,
- lokale Pfade ohne Secret- oder Vault-Inhalte,
- Safety-Flags,
- deaktivierte externe Aktionen,
- harte Tokens als Statushinweis,
- Safety Scanner.

## Read-only-Hinweis

Der Abschnitt stellt klar:

- Die Anzeige- und Count-Bereiche sind nur eine Anzeige.
- Sie loeschen nichts.
- Sie exportieren nichts.
- Sie schreiben nichts.
- Sie aktivieren keine externen Dienste.
- Sie lesen lokale SQLite-Counts nur aus einer vorhandenen Datenbank im read-only Modus.
- Sie legen bei fehlender Datenbank keine Datei, keinen Ordner und kein Schema an.
- Sie zeigen keine `.env`-Dateien, Secrets oder Obsidian-Vault-Inhalte an.

## Cleanup-Abgrenzung

Die `ausfuehren`-Pfade im Privacy Dashboard sind separate lokale Cleanup-Funktionen.
Sie sind nicht Teil dieser Count-Finalization und bleiben nur nach Preview, Safety Smoke, Guard, ggf. Backup-Anforderung und hartem Token erlaubt.

## Safety-Bewertung

- Keine Write-Produktlogik geaendert.
- Fokus-Tests fuer read-only Count-Ermittlung und CLI-Anzeige ergaenzt.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Privacy Dashboard Final Acceptance Gate.
