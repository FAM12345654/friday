# Local Data Import Apply User Guide Integration

## Ziel

Dieses Dokument haelt fest, dass die Nutzer-Dokumentation fuer den lokalen Import-Apply-Schreibpfad synchronisiert wurde.

Der wichtige Unterschied fuer Nutzer:

- `7. Import-Apply-Vorschau anzeigen` bleibt read-only.
- `8. Import nach Freigabe anwenden` kann lokal schreiben, aber nur nach Backup-Schutz, Safety Smoke PASS und exakt `IMPORT ANWENDEN`.

## README-Integration

`README_USER.md` beschreibt jetzt den Backup-/Restore-Bereich mit getrennten Import-Apply-Pfaden:

| Menuepunkt | Bedeutung | Schreibverhalten |
|---|---|---|
| `7. Import-Apply-Vorschau anzeigen` | Zeigt Status, Sektionen, Warnungen und Blockiergruende. | Schreibt nie. |
| `8. Import nach Freigabe anwenden` | Wendet einen gueltigen lokalen Export auf die lokale SQLite-DB an. | Nur mit Backup-Schutz, Safety Smoke PASS und `IMPORT ANWENDEN`. |
| `9. Zurueck zum Hauptmenue` | Verlaesst den Backup-/Restore-Bereich. | Schreibt nie. |

## Nutzer-Safety

Friday fragt den Token nur ab, wenn die Apply-Pruefung tokenfaehig ist.

Wenn Manifest, Dry-Run oder Backup-Schutz blockieren:

- wird kein Token abgefragt,
- wird nichts importiert,
- wird nichts wiederhergestellt,
- wird nichts geschrieben.

Wenn der Token falsch ist:

- wird der Writer nicht freigegeben,
- bleibt die lokale SQLite-DB unveraendert,
- zeigt Friday den Blockiergrund `invalid_token`.

## Bewusst unveraendert

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Restore in aktive Projektdateien.
- Keine Datenbankschema-Aenderung.
- `7. Import-Apply-Vorschau anzeigen` bleibt read-only.
- Delete-Policy bleibt unveraendert.

## Verweise

- `LOCAL_DATA_IMPORT_APPLY_CLI_IMPLEMENTATION.md`
- `LOCAL_DATA_IMPORT_APPLY_CLI_READINESS_GATE.md`
- `LOCAL_DATA_IMPORT_APPLY_WRITER_MODEL.md`
- `LOCAL_DATA_IMPORT_APPLY_WRITE_GUARD_MODEL.md`
- `README_USER.md`

## Empfehlung fuer naechsten Build Step

Local Data Import Apply Final Acceptance Gate: den gesamten Apply-Block von Policy, Preview, Guard, Writer, CLI und User Guide final zusammenfassen und mit Full Regression abschliessen.
