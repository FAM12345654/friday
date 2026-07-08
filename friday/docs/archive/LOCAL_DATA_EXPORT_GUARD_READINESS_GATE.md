# Local Data Export Guard Readiness Gate

## Ziel

Dieses Gate prueft und dokumentiert den aktuellen Stand des lokalen Datenexport-Preview- und Guard-Blocks.

Der Block ist bereit fuer die naechste Planungsstufe, aber noch nicht fuer einen echten Export freigegeben.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/local_data_export_preview.py` | Preview-only Modell vorhanden |
| `friday/app/local_data_export_guard.py` | Guard-Modell vorhanden |
| `friday/tests/test_local_data_export_preview.py` | Preview-Tests vorhanden |
| `friday/tests/test_local_data_export_guard.py` | Guard-Tests vorhanden |
| `friday/docs/LOCAL_DATA_EXPORT_READINESS_PLAN.md` | Plan vorhanden |
| `friday/docs/LOCAL_DATA_EXPORT_PREVIEW_MODEL.md` | Preview-Doku vorhanden |
| `friday/docs/LOCAL_DATA_EXPORT_GUARD_PLAN.md` | Guard-Plan vorhanden |
| `friday/docs/LOCAL_DATA_EXPORT_GUARD_MODEL.md` | Guard-Modell-Doku vorhanden |

## Readiness-Ergebnis

- Preview und Guard sind klar getrennt.
- Preview beschreibt nur geplante Exportbereiche.
- Guard prueft nur Freigabebedingungen.
- Kein Modul erzeugt Exportdateien.
- Kein Modul erstellt Ordner.
- Kein Modul liest die Datenbank.
- Kein Modul nutzt Netzwerk oder externe Provider.
- Kein Modul ist an die CLI angebunden.
- Der harte Token fuer spaetere Freigabe lautet `DATEN EXPORTIEREN`.
- Zielpfade ausserhalb `local_data/exports` werden im Guard blockiert.
- Safety Smoke PASS ist als Bedingung abgebildet.
- Pflicht-Ausschluesse fuer Secrets, Tokens, Cache, Obsidian Vault, private Nachrichten und rohe aktive DB sind abgebildet.

## Abgesicherte Tests

| Testdatei | Ergebnis |
|---|---|
| `friday/tests/test_local_data_export_preview.py` | Preview-Verhalten, Zielpfad, Ausschluesse und Token |
| `friday/tests/test_local_data_export_guard.py` | Guard-Verhalten, Blockiergruende, Zielpfad, Token, Safety Smoke und Excludes |

## Nicht freigegeben

Noch nicht freigegeben sind:

- echter Export,
- ZIP-Erstellung,
- CLI-Export-Aktion,
- Datenbankabfrage fuer Exportinhalt,
- Kontakt-/Nachrichten-/Task-Datenextraktion,
- Obsidian-Export,
- Cloud- oder Provider-Export,
- automatische Speicherung sensibler Daten.

## Safety-Bewertung

- Keine externe Aktion.
- Keine Netzwerkaktion.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine Safety-Flag-Aenderung.
- Delete-Policy unveraendert.
- Preview und Guard bleiben side-effect-free.
- Safety Smoke PASS.

## Validierung

Empfohlene Validierung fuer dieses Gate:

- `python -m pytest friday/tests/test_local_data_export_preview.py friday/tests/test_local_data_export_guard.py`
- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export Implementation Plan` folgen.

Dieser Plan sollte festlegen:

- welche Datenquellen exportiert werden duerfen,
- welches Format verwendet wird,
- wie sensible Inhalte ausgeschlossen bleiben,
- ob Export zuerst als Dry-Run geplant wird,
- wie der Guard vor jedem echten Export zwingend genutzt wird,
- dass ein echter Export weiterhin nur lokal unter `local_data/exports` erfolgen darf.
