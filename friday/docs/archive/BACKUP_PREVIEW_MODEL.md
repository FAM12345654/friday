# Backup Preview Model

## Ziel

Lokales Preview-Modell fuer spaetere Friday-Backups.

## Umfang

- berechnet geplante Backup-Sektionen
- erzeugt Manifest-Preview
- schreibt keine Dateien
- kopiert keine Dateien
- erzeugt keine ZIP-Datei
- fuehrt keinen Restore aus
- nutzt keine externen Dienste

## Geplante Sektionen

| Sektion | Status |
|---|---|
| database | included oder missing |
| exports | included oder missing |
| safety_docs | included oder missing |
| obsidian_vault | excluded |
| secrets | excluded |
| venv_cache | excluded |

## Implementierte Bausteine

- BackupPreviewSection
- BackupPreview
- build_backup_preview

## Safety

- preview_only=True
- persisted=False
- external_lookup_used=False
- keine Dateioperationen ausser lokaler Existenz-/Zaehlpruefung
- keine DB-Kopie
- keine Obsidian-Vault-Kopie
- keine Secrets

## Tests

- test_backup_preview_model.py

## Empfehlung

Naechster sinnvoller Schritt:

Backup Preview Readiness Gate oder Backup Write Plan.
