# Local Data Export Final Acceptance Gate

## Ziel

Dieses Gate schliesst den lokalen Datenexport-Block ab.

Der lokale Datenexport ist als CLI-Funktion freigegeben, bleibt aber strikt lokal, guard-basiert und hart gegatet.

## Gepruefte Dokumente

| Dokument | Status |
|---|---|
| `LOCAL_DATA_EXPORT_READINESS_PLAN.md` | vorhanden |
| `LOCAL_DATA_EXPORT_PREVIEW_MODEL.md` | vorhanden |
| `LOCAL_DATA_EXPORT_GUARD_PLAN.md` | vorhanden |
| `LOCAL_DATA_EXPORT_GUARD_MODEL.md` | vorhanden |
| `LOCAL_DATA_EXPORT_GUARD_READINESS_GATE.md` | vorhanden |
| `LOCAL_DATA_EXPORT_IMPLEMENTATION_PLAN.md` | vorhanden |
| `LOCAL_DATA_EXPORT_WRITER_MODEL.md` | vorhanden |
| `LOCAL_DATA_EXPORT_WRITER_READINESS_GATE.md` | vorhanden |
| `LOCAL_DATA_EXPORT_CLI_PLAN.md` | vorhanden |
| `LOCAL_DATA_EXPORT_CLI_READ_ONLY_PREVIEW.md` | vorhanden |
| `LOCAL_DATA_EXPORT_CLI_READ_ONLY_READINESS_GATE.md` | vorhanden |
| `LOCAL_DATA_EXPORT_CLI_APPROVAL_PLAN.md` | vorhanden |
| `LOCAL_DATA_EXPORT_CLI_APPROVAL_IMPLEMENTATION.md` | vorhanden |
| `LOCAL_DATA_EXPORT_CLI_APPROVAL_READINESS_GATE.md` | vorhanden |
| `LOCAL_DATA_EXPORT_USER_GUIDE_INTEGRATION.md` | vorhanden |
| `README_USER.md` | aktualisiert |

## Final Acceptance Ergebnis

- Lokaler Datenexport ist im Backup-/Restore-Menue erreichbar.
- Preview wird vor dem Export angezeigt.
- Safety Smoke wird vor der Token-Abfrage ausgefuehrt.
- Export erfordert exakt `DATEN EXPORTIEREN`.
- Guard prueft Token, Zielpfad, Safety Smoke und Excludes.
- Writer schreibt nur unter `local_data/exports`.
- Falsche Tokens schreiben nichts.
- Leere Eingabe schreibt nichts.
- Exportierte Daten sind explizit zusammengestellt.
- Kontakt- und Review-Daten werden gefiltert.
- Nutzer-Doku ist aktualisiert.
- Testmatrix, Safety-Matrix und Doku-Index sind aktualisiert.

## Exportierte Bereiche

Der Export kann lokale Zusammenfassungen enthalten:

- Aufgaben,
- Kontakt-Kontexte,
- Review-/Vorschlags-Status,
- Safety-Status,
- Manifest,
- Export-Hinweise.

## Bewusst ausgeschlossene Bereiche

Nicht exportiert werden:

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

## Testabdeckung

Abgesichert durch:

- `friday/tests/test_local_data_export_preview.py`,
- `friday/tests/test_local_data_export_guard.py`,
- `friday/tests/test_local_data_export_writer.py`,
- `friday/tests/test_interface_main_menu_e2e.py`.

Gepruefte Kernfaelle:

- Preview ohne Dateioperation,
- Guard blockiert falsche Tokens,
- Guard blockiert falsche Zielpfade,
- Guard blockiert fehlende Excludes,
- Writer schreibt nur bei Guard-Freigabe,
- CLI bricht bei Enter ab,
- CLI blockiert falschen Token,
- CLI schreibt bei `DATEN EXPORTIEREN`,
- Manifest und Dateien werden erstellt,
- rohe aktive Datenbank wird nicht exportiert.

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

## Finaler Status

Der lokale Datenexport-Block ist abgeschlossen und angenommen.

Friday kann lokale Daten exportieren, aber nur innerhalb der definierten Safety-Grenzen.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Export Runtime Readiness Summary` oder ein neuer Produktblock folgen.

Empfohlener naechster Produktblock:

- `Local Data Export Runtime Readiness Summary`, falls eine kurze Abschlussuebersicht gewuenscht ist.
- Danach: `Local Data Import / Export Review Plan`, falls spaeter ein sicherer Import-/Restore-aehnlicher Datenfluss geplant werden soll.
