# Backup / Restore User Guide Integration

## Ziel

Dieses Dokument beschreibt die Integration der lokalen Backup-/Restore-Hinweise in die Nutzer-Dokumentation.

Der Fokus liegt auf einfacher Bedienbarkeit und klaren Safety-Grenzen:

- Backup-Vorschau ansehen,
- Backup lokal erstellen,
- Restore-Dry-Run pruefen,
- Restore-Kopie erstellen,
- keinen echten In-Place-Restore ausfuehren.

## Nutzer-Doku

`README_USER.md` enthaelt jetzt einen kurzen Abschnitt zu Backup / Restore.

Der Abschnitt erklaert:

- wie der Bereich im Hauptmenue geoeffnet wird,
- welche Menuepunkte vorhanden sind,
- welche harten Tokens erforderlich sind,
- dass Restore-Kopie nicht die aktive Datenbank ersetzt,
- dass echte externe Aktionen deaktiviert bleiben.

## Wichtige Tokens

| Aktion | Token |
|---|---|
| Backup lokal erstellen | `BACKUP ERSTELLEN` |
| Restore-Kopie erstellen | `RESTORE AUSFUEHREN` |

## Bewusst unveraendert

- Kein echter In-Place-Restore.
- Kein Restore direkt in `friday.db`.
- Kein Restore aus ZIP.
- Kein Cloud-Backup.
- Kein externer Speicherort.
- Keine Netzwerk- oder Provider-Aktion.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Backup bleibt unter `local_data/backups/`.
- Restore Copy bleibt unter `local_data/restores/`.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Backup / Restore Final Acceptance Gate.
