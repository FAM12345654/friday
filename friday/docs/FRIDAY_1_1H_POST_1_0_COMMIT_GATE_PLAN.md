# Friday 1.1H Post-1.0 Commit Gate Plan

## Ziel

Build Step 1.1H plant einen moeglichen spaeteren Commit fuer die offenen Post-1.0-Doku- und UX-Aenderungen. Dieser Schritt fuehrt keinen Commit aus.

## Ausgangslage

| Bereich | Stand |
|---|---|
| Lokale 1.0 Baseline | 7e9580 |
| Letzter Full Run | 1084 passed, 4 skipped |
| Compilecheck | erfolgreich |
| Safety Smoke | Overall: PASS |
| Diff-Check | sauber |
| Commit in diesem Schritt | keiner |

## Offene Aenderungen laut Working Tree

`	ext
 M friday/app/interface.py  M friday/app/menu.py  M friday/docs/BUILD_HISTORY.md  M friday/docs/DATA_MODELS.md  M friday/docs/FRIDAY_1_0_RELEASE_NOTES.md  M friday/docs/README_USER.md  M friday/docs/SAFETY_MATRIX.md  M friday/docs/TEST_MATRIX.md  M friday/docs/cli_documentation_index_12l.md  M friday/tests/test_interface_main_menu_e2e.py ?? friday/docs/FRIDAY_1_0_COMPLETION_GATE.md ?? friday/docs/FRIDAY_1_1A_CLI_POLISH.md ?? friday/docs/FRIDAY_1_1B_CLI_TERMS_AND_RETURN_HINTS.md ?? friday/docs/FRIDAY_1_1C_BACKUP_PRIVACY_CLI_HINTS.md ?? friday/docs/FRIDAY_1_1D_CLI_HELP_SAFETY_CONSOLIDATION.md ?? friday/docs/FRIDAY_1_1E_POST_1_0_DOC_CLEANUP.md ?? friday/docs/FRIDAY_1_1F_POST_1_0_UX_VALIDATION.md ?? friday/docs/FRIDAY_1_1G_FULL_REGRESSION_VALIDATION.md ?? friday/docs/FRIDAY_1_1_PLANNING_GATE.md
`

## Vorgeschlagener spaeterer Commit-Scope

Ein spaeterer Post-1.0-Commit darf nur folgende Kategorien enthalten:

- 1.0 Completion-Dokumentation,
- 1.1 Planning Gate,
- CLI-UX-Hinweise aus 1.1A bis 1.1D,
- Post-1.0-Doku-Bereinigung aus 1.1E,
- Validierungsdokumente aus 1.1F und 1.1G,
- passende Tests fuer die neuen CLI-Hinweise,
- keine externen Integrationen.

## Nicht in diesen Commit aufnehmen

- local_data/,
- Logs,
- .env Dateien,
- Secrets oder Credentials,
- Provider-Konfiguration,
- echte E-Mail-/WhatsApp-/SMS-/Kalender-Integration,
- Mobile-Publish-/Cloudflare-Aenderungen ausser bereits bewusst vorhandener Baseline,
- Datenbankschema-Aenderungen.

## Pflicht-Checks vor einem spaeteren Commit

- python -m pytest friday/tests
- python -m compileall friday
- python scripts\friday_safety_smoke.py
- git diff --check
- git status --short
- Staged-Dateien auf local_data/, .env, logs/, Secrets und Credentials pruefen.

## Empfohlene Commit Message fuer spaeter

`	ext
Post-1.0: document and polish local CLI UX
`

## Safety-Bewertung

- Dieser Schritt fuehrt keinen Commit aus.
- Keine Produktlogik wird geaendert.
- Keine externen Aktionen werden aktiviert.
- Safety-Flags bleiben unveraendert.
- Harte Tokens bleiben unveraendert.

## Empfehlung fuer naechsten Build Step

Build Step 1.1I: Staged-Commit-Readiness Check vorbereiten oder, falls ausdruecklich freigegeben, den Post-1.0-Commit nach erneuter Full Regression ausfuehren.
