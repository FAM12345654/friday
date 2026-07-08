# CLI Documentation Index 12L

## Ziel

Zentrale Orientierung ueber die aktiven Friday-Dokumente fuer den 1.0-Abschlussstand.
Historische Build-Gates und Detailplaene liegen im Archiv unter `archive/`.

## Aktive Dokumente

| Dokument | Zweck | Status |
|---|---|---|
| `README_USER.md` | Nutzer- und Setup-Doku fuer lokale Bedienung | aktiv |
| `FRIDAY_ARCHITECTURE.md` | Architekturuebersicht | aktiv |
| `ARCHITECTURE.md` | kurze Projektstruktur | aktiv |
| `DATA_MODELS.md` | zentrale lokale Datenmodelle | aktiv |
| `SAFETY_MATRIX.md` | Safety-Flags, Tokens, erlaubte/gated/verbotene Aktionen | aktiv |
| `TEST_MATRIX.md` | Testbereiche und Validierungsstand | aktiv |
| `BUILD_HISTORY.md` | aktueller Verlauf und letzter validierter Stand | aktiv |
| `DOCS_POLICY.md` | Regel fuer aktive Doku und Archiv | aktiv |
| `FRIDAY_LOCAL_PRODUCT_COMPLETION_GATE.md` | lokales Produktabschluss-Gate vor 1.0 | aktiv |
| `FRIDAY_LIVE_READINESS_MATRIX.md` | offene Punkte bis zu echten Live-Funktionen | aktiv |
| `FRIDAY_LIVE_ROADMAP_GATE.md` | sichere Reihenfolge fuer spaetere Live-Vorbereitung | aktiv |
| `EMAIL_DRAFT_ONLY_PLAN.md` | Plan fuer lokale E-Mail-Entwuerfe ohne Versand | aktiv |
| `FRIDAY_1_0_RELEASE_NOTES.md` | finale 1.0 Release Notes | aktiv |
| FRIDAY_1_0_COMPLETION_GATE.md | finales 1.0 Abschlussgate | abgeschlossen |
| FRIDAY_1_1_PLANNING_GATE.md | Post-1.0 Planung fuer Friday 1.1 | aktiv |

## Archiv-Regel

- Historische Detaildokumente bleiben erhalten, aber unter `archive/`.
- Neue Build-Steps sollen nur neue aktive Dokumente erzeugen, wenn sie fuer den aktuellen Produktstand steuernd sind.
- Veraltete Gates werden verschoben, nicht geloescht.

## Empfohlene Nutzung

- Nutzerstart und Bedienung: `README_USER.md`.
- Safety-Fragen: `SAFETY_MATRIX.md`.
- Test-/Coverage-Fragen: `TEST_MATRIX.md`.
- Architektur: `FRIDAY_ARCHITECTURE.md` und `DATA_MODELS.md`.
- Live-Fragen: `FRIDAY_LIVE_READINESS_MATRIX.md` und `FRIDAY_LIVE_ROADMAP_GATE.md`.

## Safety- und Local-Only-Hinweis

- Keine echten Nachrichten, WhatsApp, SMS, Kalender-Events, Wetter- oder Musikaktionen.
- Lokale SQLite-DB fuer lokale CLI-DB-Flows.
- Safety-Flags bleiben lokal-only.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Build Step: Build Step 1.1J - Post-1.0 Commit Gate nur nach ausdruecklicher Freigabe ausfuehren.


| FRIDAY_1_1B_CLI_TERMS_AND_RETURN_HINTS.md | CLI-Begriffe und Rueckkehrhinweise nach 1.0 | aktiv |


| FRIDAY_1_1C_BACKUP_PRIVACY_CLI_HINTS.md | Backup-/Privacy-CLI-Hinweise nach 1.0 | aktiv |

| FRIDAY_1_1D_CLI_HELP_SAFETY_CONSOLIDATION.md | konsolidierte lokale Safety-Hinweise in der CLI-Hilfe | aktiv |

| FRIDAY_1_1E_POST_1_0_DOC_CLEANUP.md | Post-1.0-Dokumentationsbereinigung | aktiv |

| FRIDAY_1_1F_POST_1_0_UX_VALIDATION.md | fokussierte Post-1.0-UX-Validierung | aktiv |

| FRIDAY_1_1G_FULL_REGRESSION_VALIDATION.md | Full Regression fuer offene Post-1.0-Aenderungen | aktiv |

| FRIDAY_1_1H_POST_1_0_COMMIT_GATE_PLAN.md | Plan fuer spaeteren Post-1.0-Commit | aktiv |

| FRIDAY_1_1I_STAGED_COMMIT_READINESS_CHECK.md | Readiness Check fuer spaeteren Post-1.0-Commit | aktiv |
