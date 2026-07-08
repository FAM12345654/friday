# Privacy Cleanup CLI Write Implementation Plan

## Ziel

Dieses Dokument plant die konkrete CLI-Implementierung fuer guarded Privacy Cleanup Writes.

## Geplanter Umfang

- Privacy Dashboard erhaelt `8. Privacy Cleanup ausfuehren`.
- Rueckkehr verschiebt sich auf `9. Zurueck zum Hauptmenue`.
- Nutzer waehlt nur Datei-Scopes:
  - Exporte,
  - Backups,
  - Restore-Kopien.
- Nutzer gibt einen konkreten lokalen Zielpfad ein.
- Friday zeigt eine Preview.
- Safety Smoke muss `PASS` sein.
- Nutzer muss den exakten harten Token eingeben.
- Guard muss erlauben.
- Writer fuehrt nur danach lokalen Datei-Cleanup aus.

## Nicht umgesetzt

- Kein Kontakt-Cleanup.
- Kein Review-History-Cleanup.
- Kein Obsidian-Cleanup.
- Kein externer Zugriff.
- Keine Datenbankschema-Aenderung.

## Empfehlung

Naechster Build Step: Privacy Cleanup CLI Write Implementation.
