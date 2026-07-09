# Friday Safety Matrix

## Ziel

Zentrale Uebersicht ueber erlaubte, gated und verbotene Aktionen.

## Globale Safety-Flags

| Flag | Status |
|---|---|
| `LOCAL_MODE` | `True` |
| `ENABLE_REAL_EMAIL` | `False` |
| `ENABLE_REAL_WHATSAPP` | `False` |
| `ENABLE_REAL_SMS` | `False` |
| `ENABLE_REAL_CALENDAR` | `False` |
| `ENABLE_REAL_WEATHER` | `False` |
| `ENABLE_REAL_MUSIC` | `False` |
| `REQUIRE_USER_APPROVAL` | `True` |
| `USE_REAL_TODAY` | `True` |
| `USE_SQLITE_STORAGE` | `True` |
| `DEMO_MODE` | `False` |
| `ENABLE_LOCAL_NOTIFICATIONS` | `False` |
| `OBSIDIAN_WRITE_ENABLED` | `False` |
| `ENABLE_LOCAL_OLLAMA` | `False` |

## Aktionen

| Aktion | Status | Bedingung |
|---|---|---|
| Kontakt anzeigen | erlaubt | lokal |
| Kontakt suchen | erlaubt | lokal |
| Kontakt speichern | gated | Token `SPEICHERN` |
| Kontakt-Freitext speichern | gated | Token `SPEICHERN` + Sensitive Guard erlaubt |
| Kontakt-Freitext mit sensibler Kategorie | verboten | Guard blockiert, auch mit `SPEICHERN` |
| Kontakt-Kontext löschen (DB-Cleanup) | gated | Token `KONTAKT LÖSCHEN` im bestehenden DB-Cleanup-Pfad |
| Forget Person (Kontakt-Menue) | gated | Preview + Backup + Smoke PASS + Token `PERSON VERGESSEN` |
| Review-Kontakt-Draft | erlaubt | lokal |
| Task Contact Snapshot | erlaubt | lokal |
| Obsidian Preview | erlaubt | lokal |
| Obsidian Dry-Run | erlaubt | lokal |
| Obsidian Write | gated | Vault + Flag + Token |
| Obsidian Guard Integration | umgesetzt | Sensitive Guard greift vor Obsidian Write |
| Obsidian Write mit sensiblen Freitexten | verboten | Guard blockiert auch mit `OBSIDIAN SCHREIBEN` |
| Obsidian Brain Finalization Gate | abgeschlossen | Preview-ready, Write bleibt standardmaessig deaktiviert und hart gegatet |
| Backup / Restore Plan | geplant | lokale Backups ohne Cloud/Secrets |
| Backup Preview Model | umgesetzt | zeigt geplante Backup-Inhalte ohne Dateioperation |
| Backup Preview Readiness Gate | abgeschlossen | Backup Preview ist side-effect-free geprueft |
| Backup Write Plan | geplant | lokaler Backup Write mit Token `BACKUP ERSTELLEN` |
| Backup Write Token | geplant | `BACKUP ERSTELLEN`, keine weichen Tokens |
| Backup Write mit Secrets | verboten | `.env.*`, Secrets, Tokens, API-Keys, Credentials, Private Keys, Passwoerter, `.obsidian` und Obsidian-Vault-Varianten ausgeschlossen |
| Backup Write Guard / Model | umgesetzt | prueft Token, Zielpfad, Smoke PASS und Excludes |
| Backup Write ohne `BACKUP ERSTELLEN` | verboten | Guard blockiert |
| Backup Write bei Scanner Smoke FAIL | verboten | Guard blockiert |
| Backup Write Guard Readiness Gate | abgeschlossen | Backup Write Guard ist side-effect-free geprueft |
| Backup Write Implementation Plan | geplant | spaeterer lokaler Backup Write unter Guard und hartem Token |
| Backup Write Implementation | umgesetzt | lokaler Backup Write nur unter Guard und Token |
| Backup Write Readiness Gate | abgeschlossen | lokaler Backup Write ist guard-basiert geprueft |
| Backup Write | gated | nur lokal unter `local_data/backups` mit `BACKUP ERSTELLEN` |
| Backup/Restore Forbidden-Path Hardening | umgesetzt | Backup skippt sensible Exportpfade, Symlinks/Junctions und Root-Escapes; Restore Dry-Run blockiert solche Backup-Inhalte |
| Restore Dry-Run Plan | geplant | Backup pruefen ohne Zurueckschreiben oder Ueberschreiben |
| Restore Dry-Run Model | umgesetzt | prueft lokalen Backup-Ordner ohne Restore-Write |
| Restore Dry-Run Readiness Gate | abgeschlossen | Restore Dry-Run ist side-effect-free geprueft |
| Backup / Restore CLI Integration Plan | geplant | spaeteres Menue trennt Preview, gated Backup Write und Restore Dry-Run |
| Backup / Restore CLI Read-Only Preview | umgesetzt | Menue zeigt Backup Preview und Restore Dry-Run ohne Write |
| Backup Write CLI Approval Plan | geplant | Backup Write spaeter nur mit Scanner Smoke PASS und `BACKUP ERSTELLEN` im CLI |
| Backup Write CLI Approval Implementation | umgesetzt | Backup Write im CLI nur mit Safety Smoke PASS und `BACKUP ERSTELLEN` |
| Backup Rotation | umgesetzt | alte lokale Backups nur nach Preview, Safety Smoke PASS und Token `BACKUP AUFRAEUMEN`; neuester Backup-Ordner bleibt geschuetzt |
| Backup / Restore CLI Readiness Gate | abgeschlossen | CLI-Block fuer Preview, Backup Write und Dry-Run geprueft |
| Restore Write Plan | geplant | echter Restore braucht Dry-Run PASS, Konfliktpruefung und `RESTORE AUSFUEHREN` |
| Restore Write Guard Model | umgesetzt | prueft Restore Write theoretisch ohne Dateiaenderung |
| Restore Write Guard Readiness Gate | abgeschlossen | Restore Write Guard ist side-effect-free geprueft |
| Restore Write Implementation Plan | geplant | spaeterer Restore Write nur in separaten Restore-Zielordner, keine aktive DB ersetzen |
| Restore Write Implementation | umgesetzt | Restore Copy nur in separaten Zielordner, aktive DB bleibt unangetastet |
| Restore Write Readiness Gate | abgeschlossen | Restore Writer ist als separater Copy-Baustein geprueft |
| Restore Write CLI Approval Plan | geplant | Restore Copy spaeter nur mit `RESTORE AUSFUEHREN` im CLI |
| Restore Write CLI Approval Implementation | umgesetzt | Restore Copy im CLI nur mit `RESTORE AUSFUEHREN` und separatem Zielordner |
| Restore Write CLI Readiness Gate | abgeschlossen | CLI-Restore-Write als lokale Kopie geprueft und weiterhin hart gegatet |
| Backup / Restore Documentation Finalization | abgeschlossen | Backup/Restore-Status, Grenzen und nicht freigegebener In-Place-Restore dokumentiert |
| Backup / Restore Runtime Readiness Summary | abgeschlossen | lokaler Runtime-Stand fuer Backup Preview, Backup Write, Restore Dry-Run und Restore Copy dokumentiert |
| Backup / Restore User Guide Integration | abgeschlossen | Nutzer-Doku erklaert Backup/Restore-Menue, harte Tokens und blockierten In-Place-Restore |
| Backup / Restore Final Acceptance Gate | abgeschlossen | lokaler Backup-/Restore-Block fuer Preview, Write, Dry-Run und Copy angenommen |
| Privacy Dashboard Readiness Plan | geplant | spaeteres read-only Privacy Dashboard fuer lokale Daten, Safety-Flags und gated Aktionen |
| Privacy Dashboard Read-Only Model | umgesetzt | isoliertes Modell zeigt lokale Safety-/Datenbereiche ohne Writes oder externe Aktion; optionale Counts nur read-only |
| Privacy Dashboard Read-Only Readiness Gate | abgeschlossen | isoliertes Privacy-Modell ist read-only, scanner-clean und bereit fuer spaetere CLI-Planung |
| Privacy Dashboard CLI Read-Only Plan | geplant | spaetere CLI-Anbindung bleibt read-only und ohne Loesch-/Export-/Write-Aktionen |
| Privacy Dashboard CLI Read-Only Implementation | umgesetzt | Anzeige-Bereiche im Privacy Dashboard bleiben read-only ohne Write, Export oder Loeschung |
| Privacy Dashboard CLI Read-Only Readiness Gate | abgeschlossen | Privacy-Dashboard-Anzeige ist read-only, scanner-clean und lokal freigegeben |
| Privacy Dashboard User Guide Integration | abgeschlossen | Nutzer-Doku trennt read-only Anzeige-/Count-Bereiche von separaten hart gegateten Cleanup-Pfaden |
| Privacy Dashboard Final Acceptance Gate | abgeschlossen | Privacy Dashboard Anzeige-/Count-Block als read-only CLI-Uebersicht final angenommen |
| Privacy Dashboard Local Count Finalization | umgesetzt | vorhandene SQLite-Daten und lokale Backup/Restore-Ordner werden read-only gezaehlt; fehlende DBs werden nicht erzeugt |
| Privacy Data Cleanup Policy Plan | geplant | spaetere lokale Bereinigung nur gezielt, hart gegatet und ohne globale Loeschaktion |
| Privacy Data Cleanup Policy Readiness Gate | abgeschlossen | Cleanup-Policy bleibt nicht-ausfuehrend; keine Loeschfunktion freigegeben |
| Local Data Export Readiness Plan | geplant | spaeterer lokaler Export nur unter `local_data/exports` und eigenem harten Token |
| Local Data Export Preview Model | umgesetzt | isoliertes Preview-Modell plant lokalen Export ohne Dateioperation, DB-Abfrage oder externe Aktion |
| Local Data Export Guard Plan | geplant | spaeterer Export nur mit Zielpfad unter `local_data/exports`, Safety Smoke PASS und `DATEN EXPORTIEREN` |
| Local Data Export Guard Model | umgesetzt | isolierter Guard prueft Token, Zielpfad, Safety Smoke und Excludes ohne Export |
| Local Data Export Guard Readiness Gate | abgeschlossen | Preview und Guard sind side-effect-free geprueft, echter Export bleibt nicht freigegeben |
| Local Data Export Implementation Plan | geplant | spaeterer Writer nur unter Guard, `local_data/exports`, Safety Smoke PASS und Exclude-Regeln |
| Local Data Export Writer Model | umgesetzt | isolierter Writer schreibt nur explizit uebergebene Daten unter Guard und `local_data/exports` |
| Local Data Export Writer Readiness Gate | abgeschlossen | Writer ist guard-basiert geprueft, CLI-Anbindung bleibt nicht freigegeben |
| Local Data Export CLI Plan | geplant | spaetere CLI-Anbindung trennt Preview, Safety, Guard, Token und Writer |
| Local Data Export CLI Read-Only Preview | umgesetzt | Backup-/Restore-Menue zeigt Export-Preview ohne Token, Writer oder Dateioperation |
| Local Data Export CLI Read-Only Readiness Gate | abgeschlossen | CLI-Preview ist read-only geprueft, echter Export bleibt nicht freigegeben |
| Local Data Export CLI Approval Plan | geplant | spaeterer CLI-Export nur mit Safety Smoke PASS, Guard und `DATEN EXPORTIEREN` |
| Local Data Export CLI Approval Implementation | umgesetzt | CLI-Export nur mit Safety Smoke PASS, Guard und `DATEN EXPORTIEREN` |
| Local Data Export CLI Approval Readiness Gate | abgeschlossen | lokaler CLI-Export ist guard-basiert geprueft und bleibt hart gegatet |
| Local Data Export User Guide Integration | abgeschlossen | Nutzer-Doku erklaert lokalen Export, Token und ausgeschlossene Inhalte |
| Local Data Export Final Acceptance Gate | abgeschlossen | lokaler Datenexport-Block final angenommen |
| Local Data Export Runtime Readiness Summary | abgeschlossen | aktueller lokaler Runtime-Stand fuer Datenexport dokumentiert |
| Local Data Import / Export Review Plan | geplant | spaeterer Import-/Review-Flow nur read-only, kein aktiver Write |
| Local Data Import Manifest Reader Plan | geplant | spaeterer Manifest Reader nur read-only, kein Import oder Restore |
| Local Data Import Manifest Reader Model | umgesetzt | liest nur `manifest.json` unter `local_data/exports`, kein Import oder Restore |
| Local Data Import Manifest Reader Readiness Gate | abgeschlossen | Manifest Reader ist read-only, scanner-clean und Export-Writer-kompatibel |
| Local Data Import Dry-Run Plan | geplant | spaeterer Import-Dry-Run prueft Exportdateien nur read-only, kein Import |
| Local Data Import Dry-Run Model | umgesetzt | prueft lokale Exportdateien read-only, kein Import oder Restore |
| Local Data Import Dry-Run Readiness Gate | abgeschlossen | Import-Dry-Run ist read-only, scanner-clean und Export-Writer-kompatibel |
| Local Data Import Review CLI Read-Only Plan | geplant | spaeterer CLI-Review zeigt Manifest und Dry-Run nur read-only |
| Local Data Import Review CLI Read-Only Implementation | umgesetzt | CLI zeigt Manifest Reader und Import Dry-Run read-only, kein Import |
| Local Data Import Review CLI Read-Only Readiness Gate | abgeschlossen | CLI-Import-Review ist read-only, scanner-clean und stabil |
| Local Data Import Review Documentation Integration | abgeschlossen | Nutzer-Doku erklaert read-only Import-Review ohne Import oder Restore |
| Local Data Import Review Final Acceptance Gate | abgeschlossen | read-only Import-Review-Block final angenommen, echter Import bleibt nicht freigegeben |
| Local Data Import Runtime Readiness Summary | abgeschlossen | aktueller Runtime-Stand fuer read-only Import-Review dokumentiert |
| Local Data Import Block Documentation Finalization | abgeschlossen | Import-Review-Dokumentation finalisiert, echter Import bleibt nicht freigegeben |
| Local Data Import Apply Policy Plan | geplant | Policy fuer spaeteren Import-Apply, noch kein Import oder Restore |
| Local Data Import Apply Preview Plan | geplant | Planung fuer spaetere Import-Apply-Vorschau ohne Import oder Write |
| Local Data Import Apply Preview Model | umgesetzt | isoliertes Apply-Preview-Modell ohne Import, Restore oder Write |
| Local Data Import Apply Preview Readiness Gate | abgeschlossen | Apply-Preview-Modell geprueft, echter Import bleibt nicht freigegeben |
| Local Data Import Apply CLI Plan | geplant | Planung fuer spaetere CLI-Anbindung der Apply-Vorschau ohne Import |
| Local Data Import Apply CLI Preview Implementation | umgesetzt | CLI zeigt Apply-Vorschau read-only, kein Import oder Token-Apply |
| Local Data Import Apply CLI Preview Readiness Gate | abgeschlossen | CLI-Apply-Vorschau ist read-only geprueft, echter Import bleibt nicht freigegeben |
| Local Data Import Apply Runtime Readiness Summary | abgeschlossen | aktueller Runtime-Stand fuer Apply-Vorschau dokumentiert, kein Import freigegeben |
| Local Data Import Apply Documentation Integration | abgeschlossen | Nutzer-Doku erklaert Apply-Vorschau ohne Import, Restore oder Token-Apply |
| Local Data Import Apply Final Acceptance Gate | abgeschlossen | Apply-Preview-Block final angenommen, echter Import bleibt nicht freigegeben |
| Local Data Import Apply Block Documentation Finalization | abgeschlossen | Apply-Preview-Dokumentation finalisiert, echter Import bleibt nicht freigegeben |
| Local Data Import/Export Runtime Finalization Gate | abgeschlossen | Export, Import-Review und Apply-Vorschau als lokaler Runtime-Block finalisiert |
| Local Data Import/Export User Guide Finalization | abgeschlossen | Nutzer-Doku fuer Export, Import-Review und Apply-Vorschau finalisiert |
| Local Data Import/Export Final Acceptance Gate | abgeschlossen | lokaler Export, Import-Review und Apply-Vorschau final angenommen; echter Import bleibt nicht freigegeben |
| Local Data Import Apply Write Plan | geplant | spaeterer Import-Write nur mit Guard, Backup-Schutz, konfliktfreiem Dry-Run und hartem Token `IMPORT ANWENDEN` |
| Local Data Import Apply Write Guard Plan | geplant | spaeterer side-effect-free Guard fuer Import-Apply-Freigabe ohne Write |
| Local Data Import Apply Write Guard Model | umgesetzt | isolierter Guard prueft Token, Preview, Scope, Safety Smoke und Blockiergruende ohne Write |
| Local Data Import Apply Write Guard Readiness Gate | abgeschlossen | Guard-Modell angenommen; echter Import bleibt nicht freigegeben |
| Local Data Import Apply Writer Plan | geplant | spaeterer Writer nur nach Guard-Erlaubnis, Transaktion und Rollback-Regeln |
| Local Data Import Apply Writer Model | umgesetzt | isolierter Writer-Prototyp schreibt nur mit Guard-Erlaubnis in explizite SQLite-DB |
| Local Data Import Apply Writer Readiness Gate | abgeschlossen | Writer-Prototyp angenommen; CLI-Import bleibt nicht freigegeben |
| Local Data Import Apply CLI Write Plan | geplant | spaetere CLI-Anbindung nur nach Preview, Backup-Schutz, Guard und exakt `IMPORT ANWENDEN` |
| Local Data Import Apply CLI Write Preview Gate | abgeschlossen | CLI-Sicherheitsgrenzen fuer spaeteren Import-Apply-Write geprueft; kein CLI-Import freigegeben |
| Local Data Import Apply CLI Implementation Plan | geplant | spaetere getrennte CLI-Anbindung mit Preview, Guard, Token und Writer geplant |
| Restore | nicht umgesetzt | spaeter nur nach Dry-Run und hartem Token |
| Secrets im Backup | verboten | `.env` und API Keys ausschliessen |
| Kompakter Systemstatus | erlaubt read-only | zeigt lokale Flags und aktive Datenbank-Datei; startet keine Tests, schreibt keine Daten und ruft keine externen Dienste auf |
| Teststatus-Hilfe im Sicherheitsstatus | erlaubt read-only | zeigt empfohlene lokale Pruefkommandos nur als Text; fuehrt keine Shell-Befehle aus |
| Local Model Mock | erlaubt | lokal |
| Local AI Diagnose im Sicherheitsstatus | erlaubt read-only | zeigt nur Flags, Modellstatus und lokale URL-Regel; startet keinen Ollama Live-Health-Check |
| Ollama Runtime Opt-in | gated lokal | nur `127.0.0.1`/`localhost`, nur mit `ENABLE_LOCAL_OLLAMA=True`, Modell gesetzt, Health PASS und Validator |
| Local AI Finalization Gate | abgeschlossen | Mock Default, Ollama disabled, keine Produktflow-Live-Calls |
| AI Task Forwarding Draft | umgesetzt | Produktflow nutzt lokale KI-Provider-Schicht fuer sichtbare Drafts; Mock Default, kein echter Versand, kein Cloud-Modell |
| Local Ollama Activation Gate | umgesetzt | read-only Status-Gate; Ollama nur lokal, opt-in, Modell gesetzt und Health PASS; sonst Mock-Fallback |
| Local Ollama Config Preview | umgesetzt | prueft Modellname und lokale Base-URL ohne Config-Write, Health-Check oder Modellaufruf |
| Local Ollama Manual Config Apply Gate | umgesetzt | prueft Token `OLLAMA AKTIVIEREN`, Safety Smoke und Health PASS; schreibt config.py nicht automatisch |
| Local Ollama Config Apply Implementation Plan | geplant | beschreibt spaeteren kontrollierten Apply und Rollback; aktuell kein Config-Write |
| Local Ollama Config Apply Writer | umgesetzt isoliert | schreibt nur explizite `config.py`-Pfade, Tests nur `tmp_path`; echte Projekt-`config.py` bleibt standardmaessig blockiert |
| Local Model Settings / Health Preview / Validation Pipeline | umgesetzt | Mock bleibt Default; Ollama Health Check ist localhost-only; Validator+Logic Check blockiert riskante Ausgaben |
| Lokale Notifications | erlaubt opt-in | Default `False`; nur Konsolen-Zusammenfassung, kein Toast, kein Netzwerk |
| Demo-Modus | getrennt | echte Arbeits-DB bleibt `friday.db`; Demo-Seeds nur in `friday_demo.db` |
| Wiederkehrende Aufgaben | erlaubt lokal | nur additive nullable Spalte `recurrence`; Folgeaufgabe nur beim Erledigen |
| Friday Local Product Completion Gate | abgeschlossen | Finaler lokaler Produktstand bleibt ohne externe Aktionen, ohne Cloud-AI und mit unveraenderten Safety-Flags |
| Self-Building Preview | erlaubt | Build Queue, Test Runner Allowlist, Git Viewer und Commit Draft ohne Ausfuehrung |
| Self-Building Finalization Gate | abgeschlossen | Runner, Git und Commit bleiben preview-only und nicht ausgefuehrt |
| Self-Building Commit | nicht freigegeben | spaeter nur mit eigenem Gate und `COMMIT ERSTELLEN` |
| Friday Local MVP Release Gate | abgeschlossen | Obsidian, Local AI, Self-Building und Safety Evidence zusammengefuehrt |
| Friday Local MVP Release Closure | abgeschlossen | Chat-3-Handoff, Deferred Items und Abbruchregeln dokumentiert |
| Friday Local MVP Release Consolidation Gate | abgeschlossen | Drei parallele Chat-Stränge konsolidiert; lokales MVP bleibt ohne externe Aktionen |
| Friday Local MVP Release Candidate Checklist | abgeschlossen | Go/No-Go-Kriterien, harte Tokens und deferred externe Features dokumentiert |
| Friday Local MVP Final Go/No-Go Gate | GO lokal / NO-GO extern | Lokaler MVP freigegeben; externe Aktionen und Cloud-Provider bleiben deferred |
| Friday Local MVP Post-Release Roadmap | geplant | Post-MVP-Arbeit bleibt phasenweise, lokal-first und gate-basiert |
| Friday Local MVP User Acceptance Script | abgeschlossen | Manueller Abnahmelauf prueft lokale Nutzung ohne externe Aktionen |
| Friday Local MVP Release Notes | abgeschlossen | Release Notes dokumentieren lokalen MVP-GO, deferred externe Features und Safety-Grenzen |
| Friday Local MVP Release Notes Readiness Gate | abgeschlossen | Release Notes gegen Tests, Safety Smoke, deferred externe Features und harte Tokens geprueft |
| Friday Local MVP Runtime Handoff Summary | abgeschlossen | Runtime-Handoff dokumentiert lokale stabile Bereiche, Tests und deferred externe Funktionen |
| Friday Local MVP Phase 1 Stabilization Gate | abgeschlossen | Doku-Link-Check, README-Pruefung und CLI-Text-Review ohne Produktlogik- oder Safety-Aenderung |
| Review Export mit Guard | umgesetzt | lokaler Export nur unter `local_data/exports` mit Safety Smoke PASS und Token `REVIEW EXPORTIEREN` |
| Review Export ohne `REVIEW EXPORTIEREN` | verboten | Guard blockiert |
| Review Export bei Scanner Smoke FAIL | verboten | Guard blockiert |
| Friday Local Product Phase 2 Improvements Gate | abgeschlossen | Review Export umgesetzt; Privacy, Tagesplanung und Kontakt-CLI bleiben safety-konform read-only/gated |
| Safety Scanner | geplant | Scanner-Hardening vorbereitet |
| Scanner Readiness Gate | abgeschlossen | Scanner-Block ist dokumentiert und freigegeben |
| Scanner Smoke Script | releasefaehig | fuehrt lokale Python-Safety-Scanner gesammelt aus |
| Safety Scanner Finalization Gate | abgeschlossen | Standard-Smoke, Token-Coverage und Link-Checker-Plan dokumentiert |
| Approval Token Scanner | umgesetzt | prueft harte Tokens inkl. Forget Person, Backup, Restore, Export und Import; erkennt weiche Approval-Tokens |
| Safety Flag Regression Scanner | umgesetzt | prueft zentrale Safety-Flags auf sichere Werte |
| Forbidden Import Scanner | umgesetzt | erkennt blockierte Provider-/Netzwerkimports |
| No Network Scanner | umgesetzt | erkennt direkte Netzwerk-Nutzungsmuster lokal |
| Script Network Scanner Preview | umgesetzt | erkennt JS-/PowerShell-/Package-Script-Netzwerkmuster ohne Ausfuehrung; bewusst nicht im Standard-Smoke |
| Script Network Scanner Readiness Gate | umgesetzt | bounded Preview mit Projekt-Root und Size-Limit; Standard-Smoke-Integration bleibt deferred |
| No Input/Print Scanner | umgesetzt | erkennt direkte `input()`-/`print()`-Nutzung in isolierten Modulen |
| Markdown Link Checker | geplant | optionaler lokaler Doku-Check ohne Netzwerk |
| E-Mail senden | verboten | Flag false |
| WhatsApp senden | verboten | Flag false |
| SMS senden | verboten | Flag false |
| Kalendertermin erstellen | verboten | Flag false |
| externe Modellaufrufe | verboten | nicht freigegeben |

## Harte Tokens

| Token | Aktion |
|---|---|
| `SPEICHERN` | Kontakt-Kontext speichern |
| `KONTAKT LÖSCHEN` | Kontakt-Kontext im bestehenden DB-Cleanup-Pfad löschen |
| `PERSON VERGESSEN` | Forget Person im Kontakt-Menue ausfuehren |
| `OBSIDIAN SCHREIBEN` | Obsidian Write ausfuehren |
| `COMMIT ERSTELLEN` | spaeteren lokalen Commit ausfuehren; aktuell nicht freigegeben |
| `BACKUP ERSTELLEN` | lokales Backup erstellen |
| `RESTORE AUSFUEHREN` | spaeterer echter Restore Write |
| `DATEN EXPORTIEREN` | spaeteren lokalen Datenexport ausfuehren |
| `REVIEW EXPORTIEREN` | lokalen Review-Export ausfuehren |
| `IMPORT ANWENDEN` | spaeteren lokalen Import-Apply ausfuehren; aktuell nicht freigegeben |
| `EXPORT AUFRAEUMEN` | lokale Exporte aufraeumen |
| `BACKUP AUFRAEUMEN` | lokale Backups aufraeumen |
| `RESTORE AUFRAEUMEN` | lokale Restore-Kopien aufraeumen |
| `REVIEW AUFRAEUMEN` | lokale Review-History aufraeumen |
| `OLLAMA AKTIVIEREN` | lokale Ollama-Konfiguration fuer isolierten Writer freigeben; echte Projekt-Config bleibt ohne separates Apply-Gate blockiert |

## Delete-Policy

- `"ja"` loescht nicht.
- `"JA"` loescht nur im bestehenden Delete-Flow.
- `" JA "` bleibt durch `strip()` im bestehenden Delete-Flow erlaubt.
- `"JA"` ist im Contact-Context-Prompt invalid.


## Friday 1.0 Completion Gate

| Bereich | Status | Hinweis |
|---|---|---|
| Friday 1.0 lokal | abgeschlossen | Baseline Commit 7e9580; externe Aktionen bleiben deaktiviert |
| E-Mail-Draft | lokal erlaubt | kein Provider, kein Login, kein Versand |
| Post-1.0 Arbeit | gated | neue Produktlogik, externe Dienste oder weitere Commits brauchen eigenes Gate |
