# Local Data Export Implementation Plan

## Ziel

Dieses Dokument plant die spaetere Implementierung eines echten lokalen Datenexports.

Der Schritt selbst bleibt reine Planung. Es wird noch kein Export erzeugt, kein ZIP gebaut, keine Datei geschrieben, keine Datenbank gelesen und keine CLI-Aktion geaendert.

## Ausgangslage

Vorhanden und abgeschlossen:

- `LOCAL_DATA_EXPORT_READINESS_PLAN.md`
- `LOCAL_DATA_EXPORT_PREVIEW_MODEL.md`
- `LOCAL_DATA_EXPORT_GUARD_PLAN.md`
- `LOCAL_DATA_EXPORT_GUARD_MODEL.md`
- `LOCAL_DATA_EXPORT_GUARD_READINESS_GATE.md`

Der naechste technische Export-Schritt darf erst beginnen, wenn klar ist, welche Datenquellen exportiert werden duerfen und welche Inhalte weiterhin ausgeschlossen bleiben.

## Geplante Export-Architektur

| Baustein | Aufgabe |
|---|---|
| Preview | zeigt geplante Exportbereiche und Ausschluesse |
| Guard | blockiert unsichere Exportversuche |
| Export Builder | sammelt erlaubte lokale Daten und erzeugt Exportdateien |
| Manifest | dokumentiert Inhalt, Zeitpunkt, Safety-Status und Ausschluesse |
| CLI Approval | spaeterer Nutzerpfad mit hartem Token `DATEN EXPORTIEREN` |

## Erlaubte Datenquellen fuer spaetere Implementierung

| Bereich | Quelle | Format | Einschränkung |
|---|---|---|---|
| Aufgaben | lokale Task-Repositories | JSON und Markdown | keine Secrets, keine externen Daten |
| Kontakt-Kontexte | lokale Contact-Context-Repositories | JSON Summary | nur freigegebene, nicht sensible Felder |
| Review-Vorschlaege | lokale Suggestion-Repositories | JSON Summary | keine rohen privaten Nachrichtentexte |
| Safety Status | Konfiguration und Scanner-Ergebnis | JSON Summary | nur Flag-/Statuswerte |
| Dokumentationsindex | vorhandene lokale Doku | Markdown | keine Runtime-Secrets |

## Bewusst nicht erlaubte Inhalte

- `.env`
- API Keys
- Tokens
- Cache-Dateien
- Obsidian Vault
- rohe aktive Datenbankkopie
- vollstaendige private Nachrichtentexte
- sensible Kontakt-Freitexte
- private Gesundheitsdaten
- private Finanzdetails
- externe Providerdaten
- Cloud-Daten

## Geplante Exportstruktur

Ein spaeterer Export sollte unter folgendem Muster entstehen:

| Pfad | Zweck |
|---|---|
| `local_data/exports/friday_data_export_<timestamp>/manifest.json` | Export-Metadaten und Safety-Status |
| `local_data/exports/friday_data_export_<timestamp>/tasks/tasks.json` | lokale Aufgaben als strukturierte Daten |
| `local_data/exports/friday_data_export_<timestamp>/tasks/tasks.md` | lokale Aufgaben als lesbare Markdown-Uebersicht |
| `local_data/exports/friday_data_export_<timestamp>/contacts/contact_contexts.json` | freigegebene Kontakt-Kontext-Zusammenfassung |
| `local_data/exports/friday_data_export_<timestamp>/review/review_suggestions.json` | lokale Review-Zusammenfassung ohne rohe Nachrichtentexte |
| `local_data/exports/friday_data_export_<timestamp>/safety/safety_status.json` | lokale Safety-Flags und Scannerstatus |
| `local_data/exports/friday_data_export_<timestamp>/docs/export_notes.md` | kurze Exportnotizen |

## Guard-Pflicht vor jedem echten Export

Ein spaeterer Export darf nur starten, wenn:

- ein Preview vorhanden ist,
- der Guard `allowed=True` liefert,
- der Token exakt `DATEN EXPORTIEREN` ist,
- Safety Smoke PASS ist,
- Zielpfad unter `local_data/exports` liegt,
- alle Pflicht-Ausschluesse aktiv sind,
- sensible Details ausgeschlossen bleiben.

## Empfohlene technische Reihenfolge

| Schritt | Beschreibung |
|---|---|
| 1 | Export Writer Plan abschliessen |
| 2 | isolierten Export Builder ohne CLI bauen |
| 3 | Export Builder nur mit tmp_path testen |
| 4 | Guard vor jedem Export erzwingen |
| 5 | Manifest erzeugen |
| 6 | keine ZIP-Erstellung im ersten Writer-Schritt |
| 7 | Readiness Gate fuer Export Builder |
| 8 | danach erst CLI-Approval planen |

## Teststrategie fuer spaetere Implementierung

Geplante Tests:

- Export blockiert ohne Guard-Freigabe.
- Export blockiert bei falschem Token.
- Export blockiert bei Safety Smoke FAIL.
- Export schreibt nur unter `local_data/exports`.
- Export erstellt Manifest.
- Export enthaelt keine `.env`, Tokens, Cache-Dateien oder Obsidian Vault.
- Export enthaelt keine rohe aktive Datenbankkopie.
- Export enthaelt keine rohen privaten Nachrichtentexte.
- Export nutzt nur tmp_path in Tests.
- Export nutzt keine externen Aktionen.

## Nicht-Ziele fuer den ersten Implementierungsschritt

- Kein ZIP.
- Keine Cloud.
- Keine Provider.
- Kein Obsidian Write.
- Kein echter Nachrichtenversand.
- Keine echten Kalenderaktionen.
- Kein Restore.
- Keine automatische Exportplanung.
- Keine Standing Approval.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Dateioperation eingebaut.
- Keine Datenbankabfrage.
- Keine externe Aktion.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export Writer Model` folgen.

Dieser Writer sollte:

- isoliert bleiben,
- nur mit explizit uebergebenen Daten arbeiten,
- nur unter einem tmp_path-Ziel getestet werden,
- den Guard zwingend voraussetzen,
- Manifest und einfache JSON-/Markdown-Dateien erzeugen,
- keine ZIP-Datei erzeugen,
- keine Datenbank selbst lesen,
- keine CLI-Anbindung enthalten.
