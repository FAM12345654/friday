# Local Data Export Runtime Readiness Summary

## Ziel

Diese Uebersicht beschreibt den aktuellen lokalen Runtime-Stand des Datenexports.

Der Block ist nach dem Final Acceptance Gate abgeschlossen und lokal nutzbar.

## Runtime-Status

| Bereich | Status | Absicherung |
|---|---|---|
| Export-Preview | stabil | `test_local_data_export_preview.py` |
| Export-Guard | stabil | `test_local_data_export_guard.py` |
| Export-Writer | stabil | `test_local_data_export_writer.py` |
| CLI-Anbindung | stabil | `test_interface_main_menu_e2e.py` |
| Nutzer-Doku | aktualisiert | `README_USER.md` und `LOCAL_DATA_EXPORT_USER_GUIDE_INTEGRATION.md` |
| Final Gate | abgeschlossen | `LOCAL_DATA_EXPORT_FINAL_ACCEPTANCE_GATE.md` |

## Lokaler Nutzerpfad

Der lokale Datenexport ist erreichbar ueber:

```text
11. Backup / Restore
5. Lokaler Datenexport Vorschau anzeigen
```

Der Ablauf:

1. Preview anzeigen.
2. Safety Smoke ausfuehren.
3. Token abfragen.
4. Nur bei `DATEN EXPORTIEREN` fortfahren.
5. Guard pruefen.
6. Export unter `local_data/exports` schreiben.

## Exportierte Inhalte

Friday kann lokale Zusammenfassungen exportieren:

- Aufgaben,
- Kontakt-Kontexte,
- Review-/Vorschlags-Status,
- Safety-Status,
- Manifest,
- Export-Hinweise.

## Nicht exportierte Inhalte

Ausgeschlossen bleiben:

- `.env`,
- Secrets,
- API-Keys,
- Tokens,
- Obsidian Vault,
- Cache-Dateien,
- volle private Roh-Nachrichtentexte,
- sensible Kontakt-Freitexte,
- aktive SQLite-Datenbank als Rohdatei,
- externe Providerdaten.

## Teststatus

Aktueller dokumentierter Stand:

- Fokus-Tests: `103 passed`
- Full Regression: `611 passed`
- Compilecheck: erfolgreich
- Safety Smoke: `PASS`
- `git diff --check`: sauber

## Safety-Bewertung

- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Keine Cloud.
- Keine echten Nachrichten.
- Keine echten Kalenderaktionen.
- Keine Datenbankschema-Aenderung.
- Export nur lokal unter `local_data/exports`.
- Harter Token `DATEN EXPORTIEREN` erforderlich.
- Safety Smoke PASS erforderlich.
- Guard-Freigabe erforderlich.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Operativer Hinweis

Wenn ein Export blockiert wird, ist das erwartet bei:

- leerer Eingabe,
- falschem Token,
- Safety Smoke FAIL,
- Guard-Blockierung,
- Zielpfad ausserhalb `local_data/exports`,
- fehlenden Exclude-Regeln,
- bereits vorhandenem Zielordner.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt kann ein neuer Produktblock geplant werden.

Empfohlen:

- `Local Data Import / Export Review Plan`

Dieser Schritt sollte nur planen, ob und wie ein spaeterer sicherer Import- oder Review-Flow aussehen darf. Kein Import sollte ohne eigenes Guard-, Dry-Run- und Approval-Gate gebaut werden.
