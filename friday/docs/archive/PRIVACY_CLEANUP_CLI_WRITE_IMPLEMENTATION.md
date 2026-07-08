# Privacy Cleanup CLI Write Implementation

## Ziel

Dieses Dokument beschreibt die umgesetzte CLI-Anbindung fuer guarded Privacy Cleanup Writes.

## Umgesetzter Nutzerpfad

```text
Hauptmenue -> 12. Privacy Dashboard -> 8. Privacy Cleanup ausfuehren
```

Rueckkehr:

```text
9. Zurueck zum Hauptmenue
```

## Umgesetzte Safety-Reihenfolge

1. Warnung anzeigen.
2. Datei-Cleanup-Bereich auswaehlen.
3. Konkreten lokalen Zielpfad eingeben.
4. Preview anzeigen.
5. Safety Smoke pruefen.
6. Exakten harten Token abfragen.
7. Guard pruefen.
8. Writer ausfuehren.
9. Ergebnis anzeigen.

## Unterstützte Bereiche

- Exporte mit `EXPORT AUFRAEUMEN`
- Backups mit `BACKUP AUFRAEUMEN`
- Restore-Kopien mit `RESTORE AUFRAEUMEN`

## Weiterhin blockiert

- Kontakt-Kontext-Cleanup.
- Review-History-Cleanup.
- Obsidian-Cleanup.
- Externe Aktionen.
- SQLite-Schema-Aenderungen.

## Tests

- Falscher Token loescht nicht.
- Exakter Token loescht erlaubten Exportordner unter `tmp_path`.
- Nicht freigegebener Bereich bleibt ungueltig.

## Empfehlung

Naechster Build Step: Privacy Cleanup CLI Write Readiness Gate.
