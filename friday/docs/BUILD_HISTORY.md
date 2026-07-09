# Friday Build History

## Ziel

Kurze lokale Build-Historie fuer den aktuellen Friday-1.0-Abschlussstand.

## Stand 2026-07-08

| Bereich | Status | Ergebnis |
|---|---|---|
| Lokale CLI | abgeschlossen | Hauptmenue, Aufgaben, Review, Kontakt, Backup/Restore, Privacy, Safety und E-Mail-Draft-Preview lokal verfuegbar |
| SQLite Storage | abgeschlossen | Arbeitsdatenbank und Demo-Datenbank getrennt; `recurrence` additiv und idempotent migriert |
| Aufgaben | abgeschlossen | Create/Edit/Search/Done/Archive/Delete, Quick Add, Recurrence, Markdown Export und Tagesplanung lokal abgesichert |
| Review/Suggestions | abgeschlossen | Nachrichten- und Aufgaben-Vorschlaege, Batch-Flows und Activity-Ansichten bleiben lokal/gated |
| Kontakt-Kontext | abgeschlossen | Preview, Prompt, lokale Persistenz mit Consent, Forget Person und Sensitive Guard |
| Obsidian | abgeschlossen lokal/gated | Preview, Dry Run und Write nur mit Guard und `OBSIDIAN SCHREIBEN` |
| Backup/Restore/Import/Export | abgeschlossen lokal/gated | Backup, Restore Copy, Datenexport/-import und Cleanup mit harten Tokens |
| Local AI | abgeschlossen mock/opt-in | Mock Default; Ollama nur localhost, Opt-in, Health/Validator-Guard |
| Safety Scanner | abgeschlossen | Forbidden Imports, No Network, No Input/Print, Safety Flags und Approval Tokens im Smoke |
| E-Mail Draft-only | in Abschlusslauf | Lokales Draft-Modell und CLI-Preview ohne Provider, Login, Netzwerk oder Versand |
| Live Roadmap | abgeschlossen | E-Mail Draft-only als erster Live-Vorbereitungsblock gewaehlt; echte Live-Aktionen bleiben deferred |

## Stand 2026-07-09

| Bereich | Status | Ergebnis |
|---|---|---|
| Mobile Cleartext-Fix | abgeschlossen | `expo-build-properties` mit `usesCleartextTraffic: true`; Release-APK darf lokale HTTP-API erreichen |
| Finaler Mobile-Build | abgeschlossen | EAS Build `ad7d6749` (versionCode 5) ersetzt `1ef0090b`; APK-Link im Final Gate und Mobile/Desktop Guide aktualisiert |
| Lokale KI-Aktivierung | abgeschlossen | `ENABLE_LOCAL_OLLAMA=True`, Modell `qwen3:8b`, Timeout `30`, localhost-only, kein Cloud-Fallback |
| Messaging Agents | abgeschlossen | E-Mail-/WhatsApp-Deep-Links werden nur als Vorschau/App-Link erzeugt; Friday sendet keine echte Nachricht |
| Mobile Weiterleiten | abgeschlossen | Weiterleiten-Flow zeigt lokalen KI-Draft und oeffnet nach hartem Token nur externe App zur manuellen Nutzerfreigabe |
| E-Mail Konto-Anbindung | vorbereitet/gated | Konto-Store, SMTP/IMAP-Test, read-only Inbox-Preview, API/CLI/Mobile-Kontoansicht und Send-Guard vorbereitet; `ENABLE_REAL_EMAIL` bleibt `False` |

## Letzter validierter Stand

| Kommando | Ergebnis |
|---|---|
| `python -m pytest friday/tests` | `1171 passed, 4 skipped` |
| `python -m compileall friday friday-api` | erfolgreich |
| `python scripts/friday_safety_smoke.py` | `Overall: PASS` |
| `git diff --check` | sauber |

## Bekannte Skips

Die vier Skips betreffen Windows-Symlink-Rechte in Backup-/Restore-Symlink-Schutztests.
Sie sind keine Release-Blocker fuer Friday 1.0 lokal.

## Bewusst verschoben

- echter E-Mail-/WhatsApp-/SMS-Versand,
- echte Kalendertermine,
- Cloud-AI,
- Provider-Login/OAuth/Secrets,
- In-Place-Restore in aktive Daten,
- Self-Building Runner-Ausfuehrung,
- Git-Push/Remote/Tagging,
- Mobile/Publish/Cloudflare-Live-Flows.

## Safety

Alle aktuellen Produktfunktionen bleiben lokal oder hart gegatet.
Externe Aktionen, Cloud-Provider und echte Modellaufrufe sind fuer Friday 1.0 lokal nicht freigegeben.


## Friday 1.0 Baseline Commit

| Feld | Wert |
|---|---|
| Commit | 7e9580 |
| Message | Initial baseline: Friday local product v1.0.0 |
| Status | lokale 1.0 Baseline committed |
| Naechster Schritt | Post-1.0 Planning Gate |

## Friday 1.1E

| Bereich | Ergebnis |
|---|---|
| Ziel | Post-1.0-Dokumentationsbereinigung |
| Produktlogik | unveraendert |
| Tests | nicht ausgefuehrt; nur Doku-Schritt |
| Commit | keiner |
| Naechster Schritt | 1.1F Validierung nach Freigabe |

## Friday 1.1G

| Bereich | Ergebnis |
|---|---|
| Ziel | Full Regression fuer offene Post-1.0-Aenderungen |
| Tests | `1084 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff-Check | sauber |
| Commit | keiner |

## Friday Mobile/Desktop Creme-Moos Redesign

| Bereich | Ergebnis |
|---|---|
| Ziel | Mobile- und Desktop-Oberflaeche im hellen Creme/Moos-Design finalisieren |
| Mobile | Expo/React-Native-App mit hellem Theme, Icon-Set und LAN-API `http://192.168.178.42:8000` |
| Desktop | Electron-Fenster mit Friday-Titel, Icon und Creme/Moos-Design |
| Android Preview APK | `https://expo.dev/artifacts/eas/EKmkRcLTi_ZmjHcgInjy_L9QkfPUK9Cg1C7b0qZvUrs.apk` |
| Safety | Keine echten externen Aktionen; Friday bleibt lokal-first |

## Friday AI Draft Quality Check

| Bereich | Ergebnis |
|---|---|
| Ziel | Lokaler Qualitaetsvergleich `qwen3:8b` gegen `qwen3:14b` fuer Aufgaben-Weiterleiten-Drafts |
| Report | `FRIDAY_AI_DRAFT_QUALITY_REPORT.md` |
| Szenarien | 10 feste deutsche Weiterleiten-Szenarien, jeweils mit beiden Modellen |
| `qwen3:8b` | Durchschnitt `10.60/12`, Minimum `9/12`, Durchschnittszeit `21.90s` |
| `qwen3:14b` | Durchschnitt `11.10/12`, Minimum `10/12`, Durchschnittszeit `38.87s` |
| Entscheidung | `qwen3:8b` bleibt aktiv, weil 8b die feste Regel erfuellt und 14b nicht mindestens 2 Punkte besser ist |
| Config | keine Aenderung; `OLLAMA_MODEL = "qwen3:8b"` bleibt aktiv |
| Tests | `1151 passed, 4 skipped`; Compilecheck erfolgreich; Safety Smoke PASS; Diff-Check sauber |
| Safety | Keine Cloud-KI, kein Versand, keine Credentials, nur lokales Ollama |
