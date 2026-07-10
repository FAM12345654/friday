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
| WhatsApp Read-Bridge | vorbereitet/gated | separater Node-Read-Bridge-Pfad, API-Ingest, lokaler Speicher, Review-Suggestions und Mobile/CLI-Preview; `ENABLE_REAL_WHATSAPP` bleibt `False` |

## Letzter validierter Stand

| Kommando | Ergebnis |
|---|---|
| `python -m pytest friday/tests` | `1177 passed, 4 skipped` |
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

## Friday Setup, Calendar Extraction and Contact Categories

| Bereich | Ergebnis |
|---|---|
| Ziel | Setup-Screen, Termin-Erkennung, Kalender-Link-Vorschau und Kontakt-Kategorien |
| Setup | API-Status und Mobile Setup-Tab lokal umgesetzt |
| Termine | KI nur Rohsignal; Python loest Datum/Uhrzeit deterministisch |
| Kalender | nur Review-Vorschlag und Link-Vorschau; kein echter Write |
| Kontakte | Kategorien `familie`, `arbeit`, `freund`, `kunde`, `dienstleister`, `sonstiges`, `unbekannt` normalisiert |
| Safety | `ENABLE_REAL_CALENDAR=False`, keine externen Aktionen |
| Doku | `FRIDAY_SETUP_CALENDAR_CONTACT_GATE.md` |

## Friday Account-Policy + Google Calendar Foundation

| Bereich | Ergebnis |
|---|---|
| Ziel | Account-Policy-Engine und Google-Kalender-Fundament |
| Policies | lokale Tabelle `account_policies`, Token `POLICY SPEICHERN` |
| Filter | deterministisch in Python, z. B. `title_contains: PH` |
| KI-Kontext | Policy-Notizen werden als Kontextblock gebaut |
| Google | Provider-Modul und OAuth-URL-Preview vorbereitet |
| Kalender-Write | weiterhin blockiert, solange `ENABLE_REAL_CALENDAR=False`; Token `TERMIN SPEICHERN` erforderlich |
| Safety | Google-Imports nur in `calendar_provider_google.py`; Tests mocken Provider |
| Doku | `FRIDAY_CALENDAR_ACCOUNTS_GATE.md` |

## Friday Calendar Write Activation

| Bereich | Ergebnis |
|---|---|
| Ziel | Echtes Google-Kalender-Schreiben als bewusste Safety-Ausnahme aktivieren |
| Config | `ENABLE_REAL_CALENDAR=True`; E-Mail, WhatsApp, SMS, Wetter und Musik bleiben `False` |
| Invariante | Local-AI-/Scanner-Sendesperre prueft die fuenf Sende-Flags, Kalender ist entkoppelt |
| Kalender-Write | pro Event weiter hart gegatet: `TERMIN SPEICHERN`, Haupt-Policy, Verbindung OK |
| API | `/api/calendar/events/write-guard` erstellt bei erlaubtem Guard genau einen Google-Event und speichert lokale Referenz |
| Tests | Provider/API-Write gemockt; keine echten Google-Calls in pytest |
| Rollback | `ENABLE_REAL_CALENDAR=False` setzen und Scanner-Baseline fuer Kalender zurueck auf `False` stellen |

## Friday Outlook-ICS, Termin-Flow und Guarded Delete

| Bereich | Ergebnis |
|---|---|
| Ziel | Outlook-ICS read-only Quelle, Termin-aus-Nachricht-Write-Flow und guarded Google-Delete |
| ICS | `calendar_provider_ics.py` liest ICS mit stdlib Fetch und `icalendar`/`recurring-ical-events`; keine Write-/Delete-Operation |
| Account-Policy | `outlook_ics` speichert ICS-URL verschluesselt und URL-frei in API-Antworten |
| Kalender-Merge | `/api/calendar` fuehrt lokale Items und gefilterte Source-Events zusammen; Quellenfehler bleiben isoliert |
| Termin-Flow | `/api/calendar/events/from-message` schreibt erst nach Review und `TERMIN SPEICHERN` |
| Delete | `/api/calendar/events/delete-guard` loescht erst nach `TERMIN LOESCHEN` und entfernt danach lokale Referenz |
| Mobile | Kalenderquellen, Termin-Uebernahme, ICS-URL-Feld und Delete-Token-Feld ergaenzt |
| Safety | E-Mail, WhatsApp, SMS, Wetter und Musik bleiben `False`; Kalender bleibt pro Event hart gegatet |
| Doku | `FRIDAY_CALENDAR_SOURCES_AND_FLOW_GATE.md` |

## Friday PH-Zeitfenster und Agent-Notizen

| Bereich | Ergebnis |
|---|---|
| Ziel | PH-Zeitfenster fuer Outlook-ICS/team-hampejs und lokale Agent-Notizen fuer KI-Entwuerfe |
| PH-Zeitfenster | Policy-Transform `fixed_daily_window` setzt Outlook-ICS-Quellen lokal auf `08:00` bis `18:00` |
| Agent-Notizen | E-Mail-, WhatsApp-, Kontakt- und Policy-Notizen koennen lokal gespeichert und in lokale KI-Drafts eingebunden werden |
| Mobile | Kontakte-, Setup- und Kontenbereiche zeigen Eingabefelder fuer Agent-Notizen und PH-Zeitfenster |
| Safety | Keine neuen externen Aktionen, kein automatischer Versand, keine Cloud-KI, keine Safety-Flag-Aenderung |
| Tests | Fokus-Tests fuer Policy-Transform, Agent-Kontext, Stores, API und Forward-Draft |
| Doku | `FRIDAY_PH_TIME_WINDOW_AGENT_NOTES_GATE.md` |

## Friday Kalenderansicht und Filter-Fixes

| Bereich | Ergebnis |
|---|---|
| Ziel | Kalenderanzeige, Merge-Logik, PH-Filter und Datums-/Zeitfenster stabilisieren |
| Mobile | Kalenderansicht nutzt `merged_items` statt nur lokaler `items` |
| API | `/api/calendar` unterstuetzt `range_start`, `range_end`, `day_start`, `day_end` |
| Merge | aktivierte `main`- und `source`-Kalender-Policies werden zusammengefuehrt |
| Filter | `title_contains: PH` ist tokenbasiert und matcht nicht mehr `Philip`/`GRAPH` |
| View-Prefs | lokale Tabelle `calendar_view_prefs` speichert nur Anzeigeeinstellungen |
| Safety | keine neuen externen Aktionen; Write/Delete bleiben hart gegatet |
| Doku | `FRIDAY_CALENDAR_VIEW_FILTER_FIXES_GATE.md` |

## Friday Kontakt-Betreuer und To-do-Zustaendigkeit

| Bereich | Ergebnis |
|---|---|
| Ziel | Kunden-Betreuer an lokalen Kontakten und deterministische To-do-Zustaendigkeitsregel |
| Kontakte | `contacts` speichert optional `betreuer` fuer `contact_type = kunde` |
| Betreuer | erlaubt: `flo`, `philip`, `alex`; Nicht-Kunden leeren/ignorieren Betreuer |
| To-do-Regel | Task-Suggestions nur bei ganzwoertigem Philip/Phips/PH/Zeitler oder Kunde mit Betreuer Philip |
| Mobile | Kontakte-Tab und unbekannte Nachrichten-Absender koennen Kontaktart/Betreuer lokal speichern |
| CLI | Kontakt-Menue erhaelt Option `6. Einfachen Kontakt speichern`, Rueckweg `5` bleibt unveraendert |
| Agent-Kontext | Kunden-Betreuer werden in lokalen KI-Draft-Kontext aufgenommen |
| Safety | kein echter Versand, keine Cloud-KI, keine neue externe Aktion |
| Doku | `FRIDAY_CONTACT_BETREUER_TODO_RULE_GATE.md` |

## Familienhelden Microsoft Mail Read-only

- Neuer Microsoft Graph Mail.Read Provider: `friday/app/ms_mail_provider.py`.
- Neuer verschluesselter Account Store: `friday/app/ms_mail_account_store.py`.
- Neues Aktivierungs-Gate: `friday/app/ms_mail_read_activation_gate.py`.
- Neue lokale Tabelle: `ms_mail_messages` fuer Absender, Betreff, Empfangszeit und Vorschau.
- Neue API-Endpunkte unter `/api/accounts/ms-mail` und `/api/messages/ms-mail`.
- Mobile App zeigt Familienhelden-Postfach read-only mit Connect/Status/Sync/Preview.
- Kein Mail-Senden; `ENABLE_REAL_EMAIL` bleibt `False`.

## Familienhelden Microsoft Mail Multi-Account Read-only

- Microsoft Graph Mail.Read unterstuetzt jetzt mehrere lokale Postfaecher parallel.
- Legacy-Datei `local_data/accounts/ms_mail_account.json` wird idempotent in `local_data/accounts/ms_mail_accounts/<account_id>.json` migriert und bleibt erhalten.
- API-Status listet alle Konten tokenfrei; Sync kann alle Konten oder ein einzelnes Konto synchronisieren.
- `ms_mail_messages` speichert `account_id`, `account_username` und `provider_message_id` additiv.
- Mobile App zeigt verbundene Postfaecher, Sync pro Konto und Trennen per `KONTO LOESCHEN`.
- `ENABLE_MS_MAIL_READ` ist ein nutzer-aktivierbarer Read-Flag und nicht mehr Teil der harten Safety-Flag-Baseline.
- Kein Mail-Senden; `ENABLE_REAL_EMAIL` bleibt `False`.

## Lokaler Spam-/Absender-Block fuer Nachrichten

- Nachrichten koennen lokal als Spam markiert werden.
- Der Absender wird lokal in `blocked_senders` blockiert.
- `messages`, `whatsapp_messages` und `ms_mail_messages` erhalten additiv `is_spam`.
- Standardlisten blenden Spam aus; Spam-Ansichten nutzen `include_spam=true`.
- Neue MS-Mail-/WhatsApp-Nachrichten blockierter Absender werden lokal als Spam gespeichert und erzeugen keine Suggestions.
- Mobile App enthaelt `Spam / Absender blockieren` und einen eigenen `Spam`-Tab mit Entblocken.
- CLI enthaelt `Spam / Blockiert`.
- Kein echtes Postfach wird verschoben, geloescht oder serverseitig markiert; `Mail.Read` bleibt read-only.

## MS-Mail Absender-Fix und Office-Relevanzfilter

- Neue Doku: `FRIDAY_MS_MAIL_SENDER_RELEVANCE_GATE.md`
- Microsoft-Mail-Absender werden lokal lesbar normalisiert, inklusive interner X.500-Absender.
- `office@familienhelden.at` wird in der Standardansicht lokal nach Philip-/Team-/Betreuer-Relevanz gefiltert.
- `include_all=true`, Mobile `Alle anzeigen` und CLI `Alle Microsoft-Mails anzeigen` zeigen die lokal gespeicherten Ausnahmen.
- Safety bleibt read-only: `Mail.Read`, kein `Mail.Send`, keine Provider-Schreibaktion.

## Volle Mail-Inhalte + KI-Relevanz

- Microsoft-Mail-Sync speichert `body_full`, Empfaenger-JSON, `body_fetched_at` und `relevance_method` lokal in SQLite.
- Office-Relevanz nutzt deterministische Regeln plus lokale KI auf vollem Body. Fallback bei KI-Fehler: sichtbar markieren.
- Mobile Detailansicht zeigt den kompletten lokal gespeicherten Mail-Text erst nach Antippen.
- Safety: weiterhin `Mail.Read`, kein `Mail.Send`, kein `Mail.ReadWrite`, keine Cloud-KI fuer Body-Inhalte.

## Lernen-Reiter und lokale Regeln

- Neuer lokaler Routine-Detector fuer haeufige unbekannte Absender, Kunden ohne Betreuer, wiederkehrende Mail-Themen und wiederkehrende Kalendertermine ohne Kategorie.
- Neue lokale SQLite-Tabellen `learning_questions` und `learned_rules`.
- Neue API-Endpunkte unter `/api/learning`.
- CLI erhaelt Hauptmenuepunkt `17. Lernen`.
- Mobile App erhaelt Tab `Lernen` mit Fragekarten, Antwortoptionen, `Später` und Regelverlauf.
- Aktive Lernregeln wirken in `is_relevant_for_user` und `build_agent_context`.
- Safety: kein Modell-Nachtraining, keine externen Aktionen, keine neuen Scopes oder Pakete.
- Doku: `FRIDAY_LEARNING_TAB_GATE.md`.

## Mail-Fix: Token-Refresh, Relevanz, Tempo

- Microsoft-Mail-Sync erneuert gespeicherte OAuth-Token ueber das lokale Refresh-Token und speichert das aktualisierte Bundle wieder verschluesselt.
- Ungueltige Refresh-Tokens fuehren zu `reconnect_required`, ohne weitere Graph-Abfrage fuer dieses Konto.
- Office-Relevanz ist deterministischer: Empfaenger-/Name-/Team-/Betreuer-Regeln zuerst, Social-/Newsletter-Rauschen immer lokal irrelevant.
- Unsichere Office-Mails bleiben sichtbar mit Grund `unsicher`.
- Der normale Sync blockiert nicht mehr pro Mail auf lokale KI; KI-Relevanz bleibt nur fuer explizit injizierte zweite Meinung aktiv.
- Safety: `Mail.Read` bleibt read-only, kein `Mail.Send`, keine Cloud-KI, keine neuen Scopes.

## Mobile-Redesign: 5-Tab-IA, Home-Screen und Designsystem

- Mobile-App nutzt jetzt fuenf Haupttabs: Home, Kalender, Aufgaben, Posteingang, Mehr.
- `Mehr` enthaelt Kontakte, Lernen, Einrichten, Datenschutz und Spam/Blockiert mit eigener Zurueck-Navigation.
- Home-Screen zeigt lokale Tageskarten fuer Kalender, relevante Mails, faellige Aufgaben und Lernfragen.
- Designsystem wurde auf die verbindliche Creme/Moos-Palette zurueckgefuehrt und fuer Light/Dark vorbereitet.
- `ConfirmTokenModal` zentralisiert harte Token-Freigaben; Tokens bleiben exakt und unveraendert.
- Keine neuen nativen Pakete, keine Safety-Flag-Aenderungen, keine Backend-Sende-Logik.
- Mobile Android Export ist OTA-faehig.
