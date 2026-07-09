# Friday (lokale Version)

## Was ist Friday?
Friday ist ein lokaler Assistent für den PC.

Er nutzt:
- `friday/data/` für die lokalen Demo-JSON-Dateien.
- `local_data/friday.db` als kleine lokale SQLite-Datenbank.

Es werden keine echten Dienste verwendet.

## Wie starte ich Friday?
1. Öffne PowerShell im Projektordner `C:\Users\Phili\Documents\Friday Test Build`.
2. Installiere die Test-Abhängigkeit:
   - `python -m pip install -r requirements-test.txt`
3. Starte Friday:
   - `start_friday_stack.bat` (API + Mobile + Desktop)
4. Oder nur Desktop ohne eingebetteten API-Start:
   - `start_friday_desktop_skip_api.bat`
5. Oder klicke `start_friday.bat` im Projektordner an.
   - Das Fenster bleibt danach mit `pause` offen.
6. Optionalen Systemcheck vor dem Start ausführen:
   - `run_friday_checklist.bat`
   - `run_friday_checklist.bat --repair`
   - `run_friday_checklist.bat --start --repair`
   - `run_friday_checklist.bat --repair --mobile-release`
   - `run_friday_checklist.bat --install --repair --start`
   - `--repair` legt fehlende Shortcuts und `friday-mobile/.env` mit lokaler API-URL an.
   - `verify_friday_services.bat --ci`
   - `verify_friday_services.bat --ci --json` für Maschinen-Parsing
   - `verify_friday_services_ci.bat` als kurzer CI-Einzeiler
   - `verify_friday_shortcuts.bat --ci`
   - `verify_friday_shortcuts.bat --repair --ci`
   - `verify_friday_shortcuts.bat --help`
   - `verify_friday_services.bat --help`
7. Mobile Release / Handy-Download prüfen:
   - `verify_friday_mobile_release.bat`
   - `configure_friday_mobile_eas.bat`
   - `build_friday_mobile_android_preview.bat`
   - `publish_friday_mobile_update_preview.bat`

## Was ist jetzt anders?
- `friday/data/` enthält nur Seed-Dateien (Demo-Daten).
- `local_data/friday.db` ist die Arbeitsdatenbank auf deinem Rechner.
- Friday speichert dort lokale Aufgaben, Nachrichten, Kalender und Kontakte.

## Demo-Modus vs. echter Betrieb

- Standardmäßig läuft Friday im echten lokalen Betrieb mit `DEMO_MODE = False`.
- Dann nutzt Friday `local_data/friday.db` als Arbeitsdatenbank und legt beim frischen Start nur Tabellen an.
- Demo-Daten aus `friday/data/` werden im echten Betrieb nicht automatisch in die Arbeitsdatenbank geschrieben.
- Wenn `DEMO_MODE = True` gesetzt wird, nutzt Friday getrennt `local_data/friday_demo.db` und befüllt nur diese Demo-Datenbank mit den JSON-Seeds.
- Für Demo-Daten ist `USE_REAL_TODAY = False` weiterhin sinnvoll, weil die Demo-Beispiele auf das Demo-Datum passen.
- Bereits vorhandene alte Demo-Einträge in `local_data/friday.db` werden nicht automatisch gelöscht. Entfernen geht nur über vorhandene lokale, gegatete Lösch- und Privacy-Flows.

## Was kann Friday im Moment?
- Lokale Aufgaben anzeigen, erstellen, bearbeiten und mit Priorität verwalten
  - Unterstützte Prioritäten: `low`, `normal`, `high`, `urgent`
  - Optional wiederkehrend: `taeglich`, `woechentlich`, `monatlich`
  - Sortierung: Fälligkeitsdatum aufsteigend (ohne Datum am Ende), dann Priorität
- Lokale Aufgaben suchen und filtern
  - Suche in Titel und Notizen
  - Filter nach Status, Kategorie und Fälligkeitsdatum
- Aufgaben archivieren (`Status: archived`)
- Aufgaben dauerhaft löschen
- Aufgaben schnell erfassen (lokaler Schnellpfad mit Markern und Vorschau)
- Aufgaben als Markdown exportieren (lokaler Export, kein externer Pfad)
- Lokale Tagesplanung als read-only Vorschau anzeigen
- Lokale Nachrichten anzeigen
- Lokale Nachrichten-Vorschläge prüfen und bearbeiten
- Vorschläge lokal freigeben, ablehnen oder bearbeiten
- Vorschläge im Review-Bereich per Batch-Auswahl lokal freigeben, ablehnen oder in Aufgaben umwandeln
- Kalender-Vorschläge anzeigen
- Morgenübersicht mit Platzhalter Wetter/Musik
- Sicherheitsstatus anzeigen
- Vorschläge prüfen / freigeben (ohne reale Ausführung)
- Hilfe / Übersicht im Hauptmenü anzeigen

## Hilfe / Übersicht

- Hauptmenüpunkt: `8. Hilfe / Übersicht`
- Zeigt einen lokalen CLI-Überblick über Aufgaben-, Nachrichten-, Kalender- und Review-Bereiche.
- Stellt klar, dass dieser Bereich nur Informationsausgabe macht:
  - Es werden keine echten Nachrichten gesendet.
  - Es werden keine echten Kalendertermine erstellt.
  - Es werden keine Datenbankänderungen in der Help-Ansicht durchgeführt.
- Hilfreich als schneller Einstieg für lokale Funktionsgrenzen.

## Nachrichten-Vorschläge prüfen

- Friday liest lokale Nachrichten aus der SQLite-Datenbank.
- Für mögliche Termin-Anfragen erzeugt Friday automatisch lokale Antwort-Entwürfe.
- Alle Entwürfe werden als lokale Vorschläge gespeichert.
- In `Vorschläge prüfen / freigeben` kannst du jede Vorlage:
  - lokal freigeben
  - ablehnen
  - Text bearbeiten
  - für später offen lassen
- Eine Freigabe in diesem Schritt sendet noch nichts.
- Abgelehnte oder bearbeitete Vorschläge bleiben lokal gespeichert.

## Kombinierte Vorschlagsprüfung

- Im Menüpunkt `Vorschläge prüfen / freigeben` zeigt Friday jetzt beide Vorschlagsarten zusammen an:
  - Nachrichten-Vorschläge
  - Aufgaben-Vorschläge
- Du kannst jeweils den Bereich wählen und dort bestehende Vorschläge lokal bearbeiten, ablehnen, freigeben oder offen halten.
- Freigaben sind lokale Statuswechsel.
- Eine Freigabe eines Aufgaben-Vorschlags erstellt nur eine lokale Aufgabe in `local_data/friday.db`.
- Kalender-Slot-Auswahl bearbeitet nur den Entwurfstext lokal.
- Es werden keine externen Dienste aufgerufen, keine Nachrichten gesendet und keine echten Termine gebucht.

## Review-Aktivität anzeigen

Im Menüpunkt `Vorschläge prüfen / freigeben` kannst du mit Bereich `6` die lokale Review-Aktivität anzeigen.

Die Anzeige zeigt dir:

- offene, lokal freigegebene und abgelehnte Nachrichten-Vorschläge,
- offene, abgelehnte und in Aufgaben umgewandelte Aufgaben-Vorschläge,
- Aufgaben-Vorschläge, die bereits mit einer lokalen Aufgaben-ID verknüpft sind,
- zuletzt lokal geänderte Vorschläge.

Wichtig:

- Die Anzeige ist nur eine Übersicht.
- Es wird nichts gesendet.
- Es wird kein echter Kalendertermin erstellt.
- Es wird keine neue Aufgabe erstellt.
- Es wird kein Vorschlag freigegeben oder abgelehnt.

Mehr dazu: [Review Activity Summary User Guide](archive/REVIEW_ACTIVITY_SUMMARY_USER_GUIDE.md)

## Review-Aktivität im Detail anzeigen

Im Menüpunkt `Vorschläge prüfen / freigeben` kannst du mit Bereich `7` lokale Review-Einträge im Detail anzeigen.

Die Detailanzeige zeigt dir:

- lokale Nachrichten-Vorschläge mit ID, Status, Absender und kurzem Textauszug,
- lokale Aufgaben-Vorschläge mit ID, Status, Titel und kurzem Auszug,
- bereits umgewandelte Aufgaben-Vorschläge mit lokaler Aufgaben-ID.

Wichtig:

- Die Detailanzeige ist nur eine Übersicht.
- Es wird nichts gesendet.
- Es wird kein echter Kalendertermin erstellt.
- Es wird keine neue Aufgabe erstellt.
- Es wird kein Vorschlag freigegeben oder abgelehnt.

Mehr dazu: [Review Activity Detail View User Guide](archive/REVIEW_ACTIVITY_DETAIL_VIEW_USER_GUIDE.md)

## Review-Aktivität nach Status filtern

Im Menüpunkt `Vorschläge prüfen / freigeben` kannst du mit Bereich `8` lokale Review-Einträge nach Status filtern.

Erlaubte Filter sind:

- `all`
- `open`
- `pending`
- `edited`
- `approved`
- `rejected`
- `converted`

Wichtig:

- Der Filter ist nur eine Anzeige.
- Es wird nichts gesendet.
- Es wird kein echter Kalendertermin erstellt.
- Es wird keine neue Aufgabe erstellt.
- Es wird kein Vorschlag freigegeben oder abgelehnt.

Mehr dazu: [Review Activity Status Filter User Guide](archive/REVIEW_ACTIVITY_STATUS_FILTER_USER_GUIDE.md)

## Batch-Auswahl im Review-Bereich

Im Menüpunkt `Vorschläge prüfen / freigeben` kannst du mit Bereich `5` eine Batch-Auswahl als Vorschau anzeigen.

Beispiele für die Auswahl:

- `1`
- `1,2,3`
- `all`
- `none`
- `z`

Wichtig:

- Friday zeigt zuerst immer eine Vorschau.
- Ohne Vorschau wird keine Batch-Aktion ausgeführt.
- Vor einer lokalen Änderung prüft Friday den Safety Smoke.
- Danach ist ein harter Token nötig.
- Ein falscher Token bricht die Aktion ab.

Mögliche lokale Batch-Aktionen:

| Aktion | Token |
|---|---|
| Nachrichten-Vorschläge lokal freigeben | `BATCH FREIGEBEN` |
| Vorschläge lokal ablehnen | `BATCH ABLEHNEN` |
| Aufgaben lokal erstellen | `BATCH AUFGABEN ERSTELLEN` |

Auch bei Batch-Aktionen gilt:

- Es werden keine echten Nachrichten gesendet.
- Es werden keine echten Kalendertermine erstellt.
- Es werden keine externen Dienste aufgerufen.
- Änderungen bleiben lokal in `local_data/friday.db`.

## Aufgaben-Vorschläge aus Nachrichten

- Friday erkennt lokal Aufgaben-Anfragen in Nachrichten (Intent `task`).
- Daraus entstehen lokale Datensätze in `task_suggestions`.
- Diese werden in `Vorschläge prüfen / freigeben` angezeigt.
- Du kannst Vorschläge:
  - als lokale Aufgabe anlegen,
  - ablehnen,
  - bearbeiten (Titel, Kategorie, Fälligkeit, Notiz, Priorität),
  - oder offen lassen.
- Beim lokalen Anlegen wird `TaskAgent` verwendet.
- Es wird kein externer Kalender, keine Nachricht oder ein externer Dienst verwendet.
- Alle erzeugten Aufgaben bleiben in `local_data/friday.db`.

## Lokale Nachrichtenerkennung

Friday erkennt eingehende Nachrichten nach einfachen Regeln und ordnet sie einer lokalen Kategorie zu:

- Termin/Planung (`scheduling`)
- Aufgabe (`task`)
- Frage (`question`)
- Information (`info`)
- Unklar (`unclear`)

Die Erkennung ist vollständig lokal.
- Kein externer KI-Dienst oder cloud-basiertes Modell wird genutzt.
- Nur Termin-/Planungsnachrichten erzeugen im Moment automatisch lokale Antwortvorschläge.
- Andere Kategorien werden angezeigt, aber erzeugen aktuell keine neuen Vorschläge.

## Kalender-Vorschläge in Nachrichtenprüfung

- Bei der Prüfung von Termin-Nachrichten zeigt Friday jetzt passende freie lokale Kalender-Slots an.
- Du kannst einen Slot per ID auswählen.
- Der Slot wird lokal an den Entwurfstext angehängt, z. B.:
  - `Möglicher Termin: 2026-07-05 von 10:00 bis 11:00.`
- Die Auswahl dient nur als lokaler Vorschau-Text.
- Es wird kein echter Kalendertermin erstellt und kein echtes Nachrichtensenden ausgelöst.
- Alles bleibt lokal in `local_data/friday.db`.

## Archivieren, Suche und Löschen
- Archivieren ist sicherer: Aufgaben bleiben erhalten, werden aber mit `status = archived` markiert.
- Löschen ist dauerhaft: Aufgabe ist danach vollständig aus `local_data/friday.db` entfernt.
- Löschen braucht die exakte Eingabe `JA`.

## Wichtige Einschränkungen
- Keine echten WhatsApp-, E-Mail-, SMS-, Kalender-, Wetter- oder Musik-API-Aufrufe.
- Keine echten Nachrichten werden gesendet.
- Keine echten Kalender-Ereignisse werden erstellt.
- Keine realen externen Aktionen werden ausgeführt.
- Alle Daten bleiben lokal.

## Onboarding beim Start

Beim Start zeigt Friday eine kurze lokale Einstiegseinführung im Dashboard mit:

- Begrüßung und kurzer Funktionsüberblick,
- Hinweis auf die Hauptmenübereiche,
- klarer Sicherheitserklärung (lokale Verarbeitung, kein echter Versand, kein echter Termin).

Weitere Details: [CLI Onboarding Text 12T](archive/cli_onboarding_text_12t.md)

## Lokale Modell-Diagnose

Friday zeigt im Bereich `Sicherheitsstatus`, ob der lokale Modell-Diagnosemodus aktiv ist.

Zusätzlich zeigt der Sicherheitsstatus einen kompakten lokalen Systemstatus:

- `Local Mode`
- `Demo Mode`
- `Use Real Today`
- `SQLite Storage`
- aktive Datenbank-Datei
- lokale Benachrichtigungen
- empfohlene lokale Prüfkommandos

Diese Werte sind nur Anzeige. Die Prüfkommandos werden nur als Text angezeigt. Es wird kein Test gestartet, keine Datenbank geschrieben und kein externer Dienst aufgerufen.

- `Lokaler Modell-Diagnosemodus: Mock/Preview`
- `ENABLE_LOCAL_OLLAMA: False`
- `Ollama Modell gesetzt: False`
- `Ollama URL lokal erlaubt: True`
- `Ollama Live-Health-Check: nicht automatisch ausgeführt`
- `Externe Modellaufrufe: False`
- `Produktfluss angebunden: False`

Das heißt: es werden **keine externen Modellaufrufe** genutzt. Der Sicherheitsstatus zeigt nur lokale Konfiguration an und startet keinen Ollama-Health-Check automatisch.

Ein kurzer Hinweis ist in der Hilfe integriert:

- `Lokale Modell-Diagnose: siehe Sicherheitsstatus. Es werden keine externen Modellaufrufe genutzt.`

Local AI bleibt im MVP ein lokaler Mock- und Preview-Block:

- Mock Provider bleibt Default.
- Ollama bleibt standardmaessig deaktiviert.
- Ollama darf nur nach Opt-in mit `ENABLE_LOCAL_OLLAMA = True`, gesetztem Modell und erfolgreichem lokalen Health Check genutzt werden.
- Erlaubt sind nur `http://127.0.0.1/...` und `http://localhost/...`.
- Bei fehlendem Ollama, leerem Modell oder Health-Fehler fällt Friday automatisch auf Mock zurück.
- Jede Ollama-Antwort muss durch den lokalen Model Output Validator.
- Es gibt keinen Cloud-Fallback.
- Modell-Ausgaben koennen keine Obsidian Writes oder externen Aktionen ausloesen.

Details:
- [Friday Local Ollama User Setup Guide](FRIDAY_LOCAL_OLLAMA_USER_SETUP_GUIDE.md)
- [Local AI Finalization Gate](archive/LOCAL_AI_FINALIZATION_GATE.md)

## Obsidian Brain Preview

Friday kann lokale Aufgaben, Kontakte und Projekte als Obsidian-Notizvorschau anzeigen.

Standardmaessig schreibt Friday nichts in ein Obsidian Vault.

Sicherheitsregeln:

- Preview ist erlaubt und bleibt lokal.
- Write ist deaktiviert, solange `OBSIDIAN_WRITE_ENABLED = False` ist.
- Ein Vault-Write ist nur moeglich, wenn `OBSIDIAN_VAULT_PATH` gesetzt ist.
- Zielpfade muessen im erlaubten Unterordner `Friday` bleiben.
- Bestehende Dateien werden nicht ueberschrieben.
- Sensitive Inhalte werden vor einem Write durch den Guard geprueft.
- Der harte Token fuer einen Write lautet exakt `OBSIDIAN SCHREIBEN`.
- `JA`, `ja` oder leere Eingaben reichen nicht.
- Es gibt keine Netzwerkaktion, keinen Sync, keine externen Provider, keine echten Nachrichten und keine echten Kalenderaktionen.

Details:
- [Obsidian Brain User Guide](archive/OBSIDIAN_BRAIN_USER_GUIDE.md)
- [Obsidian Brain Finalization Gate](archive/OBSIDIAN_BRAIN_FINALIZATION_GATE.md)

## Self-Building Preview

Friday kann lokale Build-Schritte als Vorschau modellieren.

Der Self-Building-Block fuehrt im MVP nichts aus:

- Build Queue bleibt Preview.
- Test Runner nutzt nur eine Allowlist als Vorschau.
- Git Status Viewer ist read-only geplant.
- Commit Drafts sind nur Textvorschlaege.
- Ein spaeterer Commit braucht den harten Token `COMMIT ERSTELLEN`.
- Es gibt keine Git-Mutation, keinen Push und keine Netzwerkaktion.

Details:
- [Self-Building Finalization Gate](archive/SELF_BUILDING_FINALIZATION_GATE.md)

## Aufgabe schnell erfassen

- Im Menü `Aufgaben verwalten` findest du den neuen Punkt `9. Aufgabe schnell erfassen`.
- Du kannst eine Aufgabe in einer Zeile erfassen, z. B.:
  - `zahnarzt anrufen !hoch @morgen`
  - `bericht fertig @2026-07-15 !mittel`
  - `wasser trinken #taeglich`
- Friday erkennt:
  - Priorität: `!hoch`, `!mittel`, `!niedrig`, `!dringend`
  - Fälligkeit: `@YYYY-MM-DD`, `@heute`, `@morgen`
  - Wiederholung: `#taeglich`, `#woechentlich`, `#monatlich`
- Vor dem Speichern zeigt Friday eine Vorschau.
- Erst mit `j` wird die Aufgabe lokal angelegt.
- Mit `n`, Enter oder einer ungültigen Eingabe wird nichts gespeichert.
- Es werden keine externen Aktionen ausgeführt.

Details: [CLI Task Quick Add 12U](archive/cli_task_quick_add_12u.md)

## Aufgaben als Markdown exportieren

- Im Aufgabenmenü gibt es den Punkt `10. Aufgaben als Markdown exportieren`.
- Friday exportiert lokale Aufgaben als Markdown-Datei (`open`, `done`, `archived`) in den lokalen Exportpfad:
  `local_data/exports/`
- Die Datei enthält einen Zeitstempel im Namen, z. B.:
  `friday_tasks_20260706_123045.md`.
- Wiederkehrende Aufgaben enthalten im Export zusätzlich die Zeile `Wiederholung: ...`.
- Es wird **kein freier Pfad** abgefragt, der Export läuft automatisch.
- Es gibt kein Obsidian- oder Cloud-Ziel.
- Es werden keine externen Dienste oder API-Aufrufe verwendet.

Details: [CLI Task Markdown Export Docs 13D](archive/cli_task_markdown_export_docs_13d.md)

## Lokale Tagesplanung anzeigen

- Im Aufgabenmenü gibt es den Punkt `11. Lokale Tagesplanung anzeigen`.
- Friday zeigt eine lokale Tagesplan-Vorschau aus offenen Aufgaben.
- Die Ansicht sortiert Aufgaben nach Fälligkeit, Priorität und Titel.
- Erledigte und archivierte Aufgaben werden nicht empfohlen.
- Aufgaben ohne Fälligkeitsdatum werden verständlich angezeigt.
- Die Tagesplanung ist nur eine Vorschau:
  - Es wird keine Aufgabe erstellt.
  - Es wird keine Aufgabe geändert.
  - Es wird keine Aufgabe erledigt.
  - Es wird keine Aufgabe archiviert.
  - Es wird keine Aufgabe gelöscht.
  - Es wird keine Tagesliste gespeichert.
  - Es werden keine externen Dienste verwendet.
- Zurück kommst du im Aufgabenmenü mit `12. Zurück zum Hauptmenü`.

Details:
- [Local Day Planning CLI Read-Only Implementation](archive/LOCAL_DAY_PLANNING_CLI_READ_ONLY_IMPLEMENTATION.md)
- [Local Day Planning CLI Read-Only Readiness Gate](archive/LOCAL_DAY_PLANNING_CLI_READ_ONLY_READINESS_GATE.md)

## Wiederkehrende Aufgaben

Beim Erstellen oder Bearbeiten kannst du optional eine Wiederholung setzen:

- `taeglich`
- `woechentlich`
- `monatlich`

Wenn eine wiederkehrende Aufgabe als erledigt markiert wird, erstellt Friday lokal genau eine neue offene Folgeaufgabe mit fortgeschriebenem Fälligkeitsdatum.

Wichtig:

- Löschen erzeugt keine Folgeaufgabe.
- Archivieren erzeugt keine Folgeaufgabe.
- Es gibt keine externen Aktionen.

## Lokale Benachrichtigungen

Friday kann beim CLI-Start eine lokale Konsolen-Zusammenfassung für heute fällige oder überfällige Aufgaben anzeigen.

Standard:

- `ENABLE_LOCAL_NOTIFICATIONS = False`

Wenn der Flag aktiv ist, zeigt Friday nur Text in der Konsole. Es wird kein Windows-Toast, kein neues Package, kein Netzwerk und kein externer Dienst verwendet.

## Backup / Restore

Friday hat einen lokalen Bereich **Backup / Restore** im Hauptmenü.

Dort kannst du:

- eine Backup-Vorschau anzeigen,
- ein lokales Backup erstellen,
- einen Restore-Dry-Run prüfen,
- eine Restore-Kopie erstellen,
- einen lokalen Datenexport erstellen,
- einen lokalen Datenimport read-only pruefen,
- eine Import-Apply-Vorschau read-only anzeigen,
- einen Import nach Freigabe lokal anwenden.

Wichtig:

- Ein Backup wird nur lokal unter `local_data/backups/` erstellt.
- Ein Backup wird nur mit dem exakten Token `BACKUP ERSTELLEN` geschrieben.
- Backup-Kopien ueberspringen sensible Pfade in Exporten, z. B. `.env.*`, Secrets, Tokens, API-Keys, Credentials, Private Keys, Passwoerter, `.obsidian` und Obsidian-Vault-Varianten.
- Symlink-/Junction-Kandidaten und Pfade ausserhalb des erwarteten lokalen Roots werden nicht in Backups kopiert.
- Ein Restore-Dry-Run prüft nur und schreibt nichts zurück.
- Ein Restore-Dry-Run blockiert Backups, wenn solche sensiblen Pfade, Symlinks/Junctions oder Root-Escapes im Backup enthalten sind.
- Eine Restore-Kopie wird nur lokal unter `local_data/restores/` erstellt.
- Eine Restore-Kopie wird nur mit dem exakten Token `RESTORE AUSFUEHREN` geschrieben.
- Friday ersetzt dabei nicht die aktive Datenbank.
- Ein echter Restore direkt in aktive Projektdateien ist nicht freigegeben.
- Ein lokaler Datenexport wird nur unter `local_data/exports/` erstellt.
- Ein lokaler Datenexport wird nur mit dem exakten Token `DATEN EXPORTIEREN` geschrieben.
- Vor dem Export prüft Friday den lokalen Safety Smoke.
- Exportiert werden nur lokale Zusammenfassungen, z. B. Aufgaben, Kontakt-Kontexte, Review-Status und Safety-Status.
- Nicht exportiert werden `.env`, Secrets, API-Keys, Obsidian Vault, Cache-Dateien, private Roh-Nachrichten, sensible Kontakt-Freitexte oder die aktive SQLite-Datenbank als Rohdatei.
- Mit `6. Lokalen Datenimport pruefen` kannst du einen Exportordner read-only pruefen.
- Diese Import-Pruefung liest nur `manifest.json` und prueft die Exportdateien.
- Dabei wird nichts importiert, nichts wiederhergestellt und nichts geschrieben.
- Ein echter Import oder Restore in aktive Friday-Daten ist weiterhin nicht freigegeben.
- Mit `7. Import-Apply-Vorschau anzeigen` kannst du sehen, ob ein spaeterer Import theoretisch vorbereitet waere.
- Diese Apply-Vorschau bleibt read-only und zeigt Status, geplante Sektionen, Warnungen und Blockiergruende.
- Auch ueber die Apply-Vorschau wird nichts importiert, nichts wiederhergestellt und nichts geschrieben.
- Mit `8. Import nach Freigabe anwenden` kann ein lokaler Import nur nach Backup-Schutz, Safety-Smoke PASS und exakt `IMPORT ANWENDEN` angewendet werden.
- Wenn die Apply-Pruefung blockiert ist, fragt Friday keinen Token ab.
- Der Import-Apply schreibt nur lokale Zusammenfassungsdaten in die lokale SQLite-Datenbank.
- Externe Dienste werden dabei nicht genutzt.

### Lokaler Datenexport und Import-Pruefung auf einen Blick

Im Bereich **Backup / Restore** sind die lokalen Datenpfade klar getrennt:

| Menuepunkt | Bedeutung | Schreibt Daten? |
|---|---|---|
| `5. Lokaler Datenexport Vorschau anzeigen` | Zeigt und erstellt lokale Export-Zusammenfassungen unter `local_data/exports/`. | Nur mit `DATEN EXPORTIEREN` |
| `6. Lokalen Datenimport pruefen` | Prueft einen Exportordner read-only ueber `manifest.json` und Exportdateien. | Nein |
| `7. Import-Apply-Vorschau anzeigen` | Zeigt, was ein spaeterer Import theoretisch vorbereiten wuerde. | Nein |
| `8. Import nach Freigabe anwenden` | Wendet einen gueltigen lokalen Export nur nach Backup-Schutz, Safety-Smoke PASS und hartem Token an. | Nur mit `IMPORT ANWENDEN` |
| `9. Zurueck zum Hauptmenue` | Verlaesst den Backup-/Restore-Bereich. | Nein |

Wichtig: `7. Import-Apply-Vorschau anzeigen` bleibt read-only. Nur `8. Import nach Freigabe anwenden` kann nach allen lokalen Schutzpruefungen schreiben.

Details:
- [Backup / Restore Runtime Readiness Summary](archive/BACKUP_RESTORE_RUNTIME_READINESS_SUMMARY.md)
- [Backup / Restore Documentation Finalization](archive/BACKUP_RESTORE_DOCUMENTATION_FINALIZATION.md)
- [Local Data Export CLI Approval Readiness Gate](archive/LOCAL_DATA_EXPORT_CLI_APPROVAL_READINESS_GATE.md)
- [Local Data Export User Guide Integration](archive/LOCAL_DATA_EXPORT_USER_GUIDE_INTEGRATION.md)
- [Local Data Import Review Documentation Integration](archive/LOCAL_DATA_IMPORT_REVIEW_DOCUMENTATION_INTEGRATION.md)
- [Local Data Import Apply Documentation Integration](archive/LOCAL_DATA_IMPORT_APPLY_DOCUMENTATION_INTEGRATION.md)
- [Local Data Import Apply CLI Implementation](archive/LOCAL_DATA_IMPORT_APPLY_CLI_IMPLEMENTATION.md)
- [Local Data Import Apply CLI Readiness Gate](archive/LOCAL_DATA_IMPORT_APPLY_CLI_READINESS_GATE.md)
- [Local Data Import Apply User Guide Integration](archive/LOCAL_DATA_IMPORT_APPLY_USER_GUIDE_INTEGRATION.md)
- [Local Data Import Apply Final Acceptance Gate](archive/LOCAL_DATA_IMPORT_APPLY_FINAL_ACCEPTANCE_GATE.md)
- [Local Data Import/Export Runtime Final Acceptance](archive/LOCAL_DATA_IMPORT_EXPORT_RUNTIME_FINAL_ACCEPTANCE.md)
- [Local Data Import/Export Documentation Finalization](archive/LOCAL_DATA_IMPORT_EXPORT_DOCUMENTATION_FINALIZATION.md)
- [Local Data Import/Export User Guide Finalization](archive/LOCAL_DATA_IMPORT_EXPORT_USER_GUIDE_FINALIZATION.md)

## Privacy Dashboard

Friday hat im Hauptmenü den Bereich `12. Privacy Dashboard`.

Die Anzeige- und Count-Bereiche zeigen nur Informationen an.
Separate Cleanup-Ausfuehren-Pfade sind lokale, hart gegatete Funktionen.

Du kannst dort sehen:

- welche lokalen Datenbereiche Friday kennt,
- wie viele lokale Aufgaben, Kontakte, Kontakt-Kontexte und Review-Vorschlaege vorhanden sind,
- wie viele lokale Backup- und Restore-Kopie-Ordner vorhanden sind,
- welche Safety-Flags aktiv oder deaktiviert sind,
- welche externen Aktionen deaktiviert sind,
- welche Aktionen harte Tokens brauchen,
- welche lokalen Safety Scanner vorhanden sind.
- welche lokalen Datenbereiche spaeter gezielt verwaltet werden koennten.
- welche Cleanup-Bereiche spaeter theoretisch moeglich oder blockiert waeren.
- DB-Cleanup-Kandidaten read-only anzeigen.

In separaten Ausfuehren-Pfaden kannst du:

- erlaubte lokale Datei-Cleanup-Bereiche nach Safety Smoke, Guard und hartem Token ausfuehren.
- erlaubte DB-Cleanup-Bereiche nach Backup, Safety Smoke, Guard und hartem Token ausfuehren.

Wichtig:

- Die reinen Anzeige-Bereiche im Privacy Dashboard loeschen nichts.
- Die reinen Anzeige-Bereiche im Privacy Dashboard exportieren nichts.
- Die reinen Anzeige-Bereiche im Privacy Dashboard schreiben nichts.
- Das Privacy Dashboard aktiviert keine externen Dienste.
- Es zeigt keine sensiblen Details aus Kontakten, Nachrichten oder Aufgaben an.
- Lokale Counts werden nur aus einer vorhandenen SQLite-Datenbank im read-only Modus gelesen.
- Wenn keine lokale Datenbank vorhanden ist, legt das Privacy Dashboard keine Datenbank und keine Ordner an.
- Lokale Pfade werden zur Orientierung angezeigt; `.env`, Secrets und Obsidian-Vault-Inhalte werden nicht angezeigt.
- Das Privacy Data Management Inventory ist ebenfalls nur eine read-only Anzeige.
- Die Privacy Cleanup Preview ist ebenfalls nur eine read-only Anzeige und loescht nichts.
- `8. Privacy Cleanup ausfuehren` kann erlaubte lokale Datei-Cleanup-Ziele nur nach Safety Smoke, Guard und hartem Token ausfuehren.
- `9. DB-Cleanup Preview anzeigen` zeigt Datenbank-Cleanup-Kandidaten nur read-only an.
- `10. DB-Cleanup ausführen` kann erlaubte lokale SQLite-Cleanup-Bereiche nur nach Backup, Safety Smoke, Guard und hartem Token ausfuehren.
- Der DB-Cleanup betrifft nur freigegebene Bereiche: Review-History und einzelne Kontakt-Kontexte.
- Pending Vorschlaege, Aufgaben, Nachrichten und Kalenderdaten bleiben geschuetzt.

Details:
- [Privacy Dashboard CLI Read-Only Implementation](archive/PRIVACY_DASHBOARD_CLI_READ_ONLY_IMPLEMENTATION.md)
- [Privacy Dashboard CLI Read-Only Readiness Gate](archive/PRIVACY_DASHBOARD_CLI_READ_ONLY_READINESS_GATE.md)
- [Privacy Data Management Plan](archive/PRIVACY_DATA_MANAGEMENT_PLAN.md)
- [Privacy Data Management CLI Read-Only Plan](archive/PRIVACY_DATA_MANAGEMENT_CLI_READ_ONLY_PLAN.md)
- [Privacy Data Management CLI Read-Only Implementation](archive/PRIVACY_DATA_MANAGEMENT_CLI_READ_ONLY_IMPLEMENTATION.md)
- [Privacy Cleanup CLI Read-Only Preview Implementation](archive/PRIVACY_CLEANUP_CLI_READ_ONLY_PREVIEW_IMPLEMENTATION.md)
- [Privacy Cleanup DB User Guide Update](archive/PRIVACY_CLEANUP_DB_USER_GUIDE_UPDATE.md)

## Tests
Starte die Tests mit:
- `python -m pytest friday/tests`

`run_tests.bat` prüft automatisch, ob `pytest` installiert ist. Falls nicht, wird automatisch `python -m pip install -r requirements-test.txt` ausgeführt und danach getestet.

## CLI Developer Smoke Check

Nach Änderungen an der CLI (Menü, Task-Flow oder Review-Flow) starte bitte den zentralen Guide:

- [CLI Developer Smoke Guide 12J](archive/cli_developer_smoke_guide_12j.md)

Er enthält die empfohlenen lokalen Prüfkommandos für:

- Hauptmenü-/Run-Loop
- Task-Workflows
- Review-/Suggestion-Flows
- vollständige Regression
- `compileall friday`
- `git diff --check`

## CLI-Dokumentationsindex

Für eine schnelle Orientierung über alle CLI-Doku-Dateien aus den Build-Schritten 12C–13Q siehe:

- [CLI Documentation Index 12L](cli_documentation_index_12l.md)
- [Review Activity Summary User Guide](archive/REVIEW_ACTIVITY_SUMMARY_USER_GUIDE.md)
- [Review Activity Detail View User Guide](archive/REVIEW_ACTIVITY_DETAIL_VIEW_USER_GUIDE.md)
- [Review Activity Status Filter User Guide](archive/REVIEW_ACTIVITY_STATUS_FILTER_USER_GUIDE.md)

## Windows-Einrichtung fertigstellen

## Desktop-Verknüpfungen

Nach dem Starten von `setup_friday.bat` (oder `create_friday_shortcut.bat`) stehen auf deinem Desktop automatisch elf Verknüpfungen:

- **Friday**: Startet den lokalen Assistenten (`start_friday.bat`)
- **Friday Stack**: Startet API + Mobile + Desktop (`start_friday_stack.bat`)
- **Friday API**: Startet nur das FastAPI-Backend (`start_friday_api.bat`)
- **Friday Mobile**: Startet die Expo-Mobile-App (`start_friday_mobile.bat`)
- **Friday Desktop**: Startet die Electron-Desktop-App (`start_friday_desktop.bat`)
- **Friday Desktop No API**: Startet nur den Electron-Desktop ohne eingebetteten API-Prozess (`start_friday_desktop_skip_api.bat`)
- **Friday Verify**: Führt den CI-geeigneten API- und Vorab-Check aus (`verify_friday_services_ci.bat`)
- **Friday Checklist**: Führt die Ein-Befehl-Checkliste aus (`run_friday_checklist.bat`)
- **Friday Mobile Release Check**: Prüft, ob die Mobile-App download- und update-ready ist (`verify_friday_mobile_release.bat`)
- **Friday Tests**: Startet die lokalen Tests (`run_tests.bat`)
- **Friday Setup**: Installiert Voraussetzungen und legt die Verknüpfungen neu an (`setup_friday.bat`)

Die Verknüpfungen zeigen direkt auf die Dateien im Projektordner, so dass du nicht in `C:\WINDOWS\system32` starten musst.

1. Öffne den Projektordner:
   - `C:\Users\Phili\Documents\Friday Test Build`
2. Doppelklick auf:
   - `setup_friday.bat`

Das macht:
- Installation von `pytest` (`python -m pip install -r requirements.txt`)
- Erstellung der Desktop-Verknüpfungen `Friday.lnk`, `Friday Stack.lnk`, `Friday API.lnk`, `Friday Mobile.lnk`, `Friday Desktop.lnk`, `Friday Desktop No API.lnk`, `Friday Verify.lnk`, `Friday Checklist.lnk`, `Friday Mobile Release Check.lnk`, `Friday Tests.lnk`, `Friday Setup.lnk`

3. Friday starten:
- Doppelklick auf **`Friday` auf dem Desktop**
   (öffnet `start_friday.bat` im Projektordner)
- Doppelklick auf **`Friday Stack` auf dem Desktop**
- (öffnet `start_friday_stack.bat` im Projektordner)
- Doppelklick auf **`Friday Desktop No API` auf dem Desktop**
- (öffnet `start_friday_desktop_skip_api.bat` im Projektordner)
- Doppelklick auf **`Friday Verify` auf dem Desktop**
- (führt `verify_friday_services_ci.bat` aus)
- Doppelklick auf **`Friday Checklist` auf dem Desktop**
- (führt `run_friday_checklist.bat` aus)
- Doppelklick auf **`Friday Mobile Release Check` auf dem Desktop**
- (führt `verify_friday_mobile_release.bat` aus)
- oder
- Doppelklick auf `start_friday.bat` im Projektordner

4. Tests starten:
   - Doppelklick auf `run_tests.bat`
   - oder auf die Desktop-Verknüpfung **Friday Tests**

5. Falls die Verknüpfung fehlt:
   - Doppelklick auf `create_friday_shortcut.bat`

## Wenn „Friday Tests“ nicht sichtbar ist

Wenn du die Verknüpfung **Friday Tests** nicht auf dem Desktop siehst:

1. Öffne den Projektordner:
   `C:\Users\Phili\Documents\Friday Test Build`

2. Doppelklick auf:
   `create_friday_shortcut.bat`

3. Wenn du sie danach noch nicht siehst:
   Doppelklick auf:
   `verify_friday_shortcuts.bat`

Das öffnet:
- den Projektordner
- den erkannten Desktop-Ordner

Hinweis:
Manche Windows-Systeme verwenden OneDrive für den Desktop.
Darum erstellt Friday die Verknüpfungen im normalen Desktop und, falls vorhanden, auch im OneDrive-Desktop.

Wenn du `run_tests.bat` per PowerShell ausführst, dann bitte aus dem Projektordner heraus:

```powershell
cd "C:\Users\Phili\Documents\Friday Test Build"
.\run_tests.bat
```

Einfacher geht es über die Desktop-Verknüpfung **Friday Tests**.

PowerShell-Alternativen:

```powershell
cd "C:\Users\Phili\Documents\Friday Test Build"
python -m pip install -r requirements.txt
python -m pip install -r requirements-test.txt
python -m pytest friday/tests
start_friday.bat
```

Wichtige Hinweise:
- Die `.bat`-Dateien wechseln automatisch in den Projektordner, damit Tests und Start nicht aus `C:\WINDOWS\system32` laufen.
- `setup_friday.bat` ruft die Shortcut-Erstellung per `create_friday_shortcut.ps1` auf.
- `run_tests.bat` startet zuverlässig `python -m pytest friday/tests`.
- `start_friday.bat` startet den Gesamt-Stack (`start_friday_stack.bat`).
- Es werden keine echten WhatsApp-, E-Mail-, SMS-, Kalender-, Wetter- oder Musik-Integrationen aktiviert.

## Privacy Cleanup Preview

Friday hat im Privacy Dashboard eine read-only Cleanup Preview.

Du findest sie hier:

```text
Hauptmenue -> 12. Privacy Dashboard -> 7. Privacy Cleanup Preview anzeigen
```

Wichtig:
- Diese Ansicht ist nur eine Vorschau.
- Es wird nichts geloescht.
- Es wird nichts exportiert.
- Es wird nichts importiert.
- Es wird nichts wiederhergestellt.
- Es wird kein Token abgefragt.
- Externe Aktionen bleiben deaktiviert.

Zurueck kommst du im Privacy Dashboard mit:

```text
11. Zurueck zum Hauptmenue
```

## Privacy Cleanup ausfuehren

Friday hat im Privacy Dashboard zusaetzlich einen guarded Cleanup-Pfad:

```text
Hauptmenue -> 12. Privacy Dashboard -> 8. Privacy Cleanup ausfuehren
```

Dieser Pfad kann nur lokale Datei-Cleanup-Bereiche ausfuehren:

- Exporte,
- Backups,
- Restore-Kopien.

Vor einer Ausfuehrung prueft Friday:

- konkrete Zielpfad-Eingabe,
- Safety Smoke,
- Privacy Cleanup Guard,
- exakten harten Token.

Diese Tokens sind erforderlich:

| Bereich | Token |
|---|---|
| Exporte | `EXPORT AUFRAEUMEN` |
| Backups | `BACKUP AUFRAEUMEN` |
| Restore-Kopien | `RESTORE AUFRAEUMEN` |

Nicht freigegeben:

- Obsidian-Cleanup,
- externe Aktionen.

## DB-Cleanup Preview

Friday hat im Privacy Dashboard eine read-only DB-Cleanup Preview.

Du findest sie hier:

```text
Hauptmenue -> 12. Privacy Dashboard -> 9. DB-Cleanup Preview anzeigen
```

Wichtig:
- Diese Ansicht ist nur eine Vorschau.
- Es wird nichts aus SQLite geloescht.
- Es wird nichts in SQLite geschrieben.
- Guard und Writer werden nicht ausgefuehrt.
- Angezeigt werden nur sichere Metadaten wie Bereich, Tabelle, Filter, Kandidatenanzahl und erforderlicher Token.

## DB-Cleanup ausfuehren

Friday hat im Privacy Dashboard zusaetzlich einen streng gegateten DB-Cleanup-Pfad:

```text
Hauptmenue -> 12. Privacy Dashboard -> 10. DB-Cleanup ausführen
```

Dieser Pfad kann nur lokale SQLite-Bereiche ausfuehren:

- Review-History,
- einzelner Kontakt-Kontext.

Vor einer Ausfuehrung prueft Friday:

- frische DB-Cleanup Preview,
- lokaler Backup-Nachweis unter `local_data/backups/`,
- Safety Smoke,
- DB-Cleanup Guard,
- exakten harten Token.

Diese Tokens sind erforderlich:

| Bereich | Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

Wichtig:
- `ja` reicht nicht.
- `JA` reicht nicht.
- Ohne lokales Backup wird DB-Cleanup blockiert.
- Bei Safety-Smoke-Fehler wird DB-Cleanup blockiert.
- Pending Vorschlaege, Aufgaben, Nachrichten und Kalenderdaten bleiben geschuetzt.
- Externe Aktionen bleiben deaktiviert.

## Kontakt-Menue: Forget Person

Im Kontakt-Kontext-Menue nutzt `4. Kontakt vergessen` einen eigenen Forget-Person-Flow.

Der Flow ist nur lokal und arbeitet auf `contact_contexts` in SQLite. Vor einem Write zeigt Friday eine Preview, prueft ein vorhandenes lokales Backup, fuehrt den Safety Smoke aus und verlangt den exakten Token:

```text
PERSON VERGESSEN
```

`KONTAKT LÖSCHEN`, `ja`, `JA`, `ok`, Leerwerte und Tokens mit zusaetzlichen Leerzeichen geben Forget Person nicht frei.

Der Flow schreibt keine Obsidian-Dateien, ruft keine Provider auf, aendert kein Schema und loescht keine Aufgaben, Nachrichten, Kalenderdaten oder Vault-Dateien.


## Friday 1.0 Abschluss

Friday ist lokal als Version `1.0.0` abgeschlossen. Der lokale Baseline-Commit ist `e7e9580` mit der Message `Initial baseline: Friday local product v1.0.0`.

Wichtig:
- Friday bleibt lokal.
- E-Mail-Drafts sind nur lokale Vorschauen.
- Es wird nichts echt gesendet.
- Externe Integrationen bleiben deaktiviert.
- Weitere Produktarbeit ist Post-1.0 und braucht ein eigenes Gate.

Siehe auch: `FRIDAY_1_0_COMPLETION_GATE.md`.

## Friday 1.1A CLI-Polish

Die Hilfe im Hauptmenue zeigt jetzt zusaetzlich:
- die Friday-Version,
- den Startbefehl `python -m friday.main`,
- die Local-Only-Grundregel,
- einen Rueckkehrhinweis fuer Untermenues.

Siehe auch: `FRIDAY_1_1A_CLI_POLISH.md`.

## Friday 1.1B Rueckkehrhinweise

Friday zeigt in ersten Untermenues klarere Hinweise:

- Kontakt-Kontext: Aktionen bleiben lokal, Rueckkehr mit `5`.
- E-Mail-Entwurf Preview: Entwuerfe bleiben nur in der Session, Rueckkehr mit `6` oder Enter.

Siehe auch: `FRIDAY_1_1B_CLI_TERMS_AND_RETURN_HINTS.md`.

## Friday 1.1C Backup-/Privacy-Hinweise

Friday zeigt in weiteren Untermenues klarere Hinweise:

- Backup / Restore: bleibt lokal, Rueckkehr mit `9`, Write-Pfade brauchen harte Tokens.
- Privacy Dashboard: Anzeige-Bereiche sind read-only, Rueckkehr mit `11`, Cleanup braucht harte Tokens.

Siehe auch: `FRIDAY_1_1C_BACKUP_PRIVACY_CLI_HINTS.md`.

## Friday 1.1D CLI-Hilfe Safety-Hinweise

Die zentrale Hilfe im Hauptmenue zeigt jetzt einen gemeinsamen Block fuer lokale Safety-Hinweise:

- Kontakt-Kontext bleibt lokal und braucht fuer Speichern/Loeschen harte Tokens.
- E-Mail-Entwuerfe bleiben Session-only und werden nicht gesendet.
- Backup / Restore schreibt nur lokal und nur nach hartem Token.
- Privacy Dashboard zeigt read-only Informationen; Cleanup bleibt hart gegated.

Siehe auch: `FRIDAY_1_1D_CLI_HELP_SAFETY_CONSOLIDATION.md`.

## Friday 1.1E Post-1.0-Doku

Die offenen Post-1.0-Dokumente sind als eigener Doku-Block eingeordnet. Sie bleiben nach dem lokalen 1.0-Baseline-Commit bewusst uncommitted, bis ein separates Commit-Gate dafuer freigegeben wird.

Siehe auch: `FRIDAY_1_1E_POST_1_0_DOC_CLEANUP.md`.
