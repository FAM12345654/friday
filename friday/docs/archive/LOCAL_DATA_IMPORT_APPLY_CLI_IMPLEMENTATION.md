# Local Data Import Apply CLI Implementation

## Ziel

Dieser Schritt bindet den lokalen Import-Apply-Writer getrennt in das Backup-/Restore-Menue ein.

Der bestehende Menuepunkt `7. Import-Apply-Vorschau anzeigen` bleibt read-only. Der neue Menuepunkt `8. Import nach Freigabe anwenden` ist der einzige CLI-Pfad, der den Import-Apply-Writer erreichen kann.

## Umgesetzter CLI-Pfad

| Schritt | Verhalten |
|---|---|
| Exportordner eingeben | Friday liest `manifest.json` und prueft Exportdateien lokal. |
| Apply-Preview bauen | Friday prueft Manifest, Dry-Run und Backup-Schutz. |
| Backup-Schutz pruefen | Es muss ein lokaler Backup-Eintrag unter `local_data/backups/` vorhanden sein. |
| Safety Smoke pruefen | Vor dem Token muss der lokale Safety Smoke PASS melden. |
| Token abfragen | Nur exakt `IMPORT ANWENDEN` gibt den Writer frei. |
| Writer ausfuehren | Der Writer schreibt nur erlaubte lokale Scopes in die lokale SQLite-DB. |

## Bewusst unveraendert

- `7. Import-Apply-Vorschau anzeigen` bleibt read-only.
- Falsche Tokens wie `JA` oder `ja` wenden keinen Import an.
- Ohne Backup-Schutz wird kein Token abgefragt.
- Ohne Safety-Smoke PASS wird kein Import angewendet.
- Es gibt keinen Restore in aktive Projektdateien.
- Es gibt keine externen Aktionen.

## Tests

Ergaenzte Abdeckung:

- Backup-/Restore-Menue zeigt den separaten Apply-Schreibpunkt.
- Apply-Schreibpfad blockiert ohne Backup-Schutz vor Tokenabfrage.
- Falscher Token blockiert den Writer.
- Exakter Token `IMPORT ANWENDEN` wendet einen gueltigen lokalen Export auf tmp_path SQLite an.
- Bestehende read-only Apply-Vorschau bleibt unveraendert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerk- oder Provider-Aufrufe.
- Lokale SQLite-Datenhaltung.
- Keine Datenbankschema-Aenderung.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer naechsten Build Step

Local Data Import Apply CLI Readiness Gate: den neuen Schreibpfad final pruefen, dokumentieren und gegen Full Regression, Compilecheck, Safety Smoke und `git diff --check` absichern.
