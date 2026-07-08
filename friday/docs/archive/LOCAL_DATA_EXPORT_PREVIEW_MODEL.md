# Local Data Export Preview Model

## Ziel

Dieses Dokument beschreibt das neue isolierte Preview-Modell fuer einen spaeteren lokalen Datenexport.

Der Schritt erzeugt noch keinen echten Export. Er beschreibt nur, welche Bereiche spaeter exportiert werden koennten, wohin der Export lokal geplant waere und welche Daten bewusst ausgeschlossen bleiben.

## Implementierte Datei

| Datei | Zweck |
|---|---|
| `friday/app/local_data_export_preview.py` | Side-effect-free Preview-Modell fuer lokalen Datenexport |
| `friday/tests/test_local_data_export_preview.py` | Tests fuer Zielpfad, Preview-Flags, Ausschluesse und harten Token |

## Modellumfang

Das Modell liefert:

- geplanten Zielordner unter `local_data/exports/friday_data_export_<timestamp>`,
- geplante Exportbereiche,
- bewusst ausgeschlossene Inhalte,
- harten Freigabe-Token `DATEN EXPORTIEREN`,
- Safety-Flags fuer Preview-only, keine Persistenz und keine externen Lookups.

## Geplante Bereiche

| Bereich | Format | Safety-Hinweis |
|---|---|---|
| Aufgaben | `markdown_json` | nur lokale Task-Felder, keine rohe aktive Datenbank |
| Kontakt-Kontexte | `summary_json` | nur freigegebene Zusammenfassung, keine sensiblen Freitexte |
| Review-Vorschlaege | `summary_json` | Status und IDs, keine rohen privaten Nachrichtentexte |
| Backup-Restore-Status | `summary_json` | Pfade und Status, kein verschachtelter Backup-Inhalt |
| Privacy Dashboard Summary | `summary_json` | lokale Flag-/Statusuebersicht |
| Safety Matrix | `markdown_summary` | Dokumentationssnapshot ohne Runtime-Secrets |

## Bewusst ausgeschlossene Inhalte

- `.env`
- API Keys
- Tokens
- Cache-Dateien
- Obsidian Vault
- vollstaendige private Nachrichtentexte
- sensible Kontakt-Freitexte
- private Gesundheitsdaten
- private Finanzdetails
- rohe aktive Datenbankkopie

## Tests

Abgedeckt durch `friday/tests/test_local_data_export_preview.py`:

- Preview bleibt `preview_only=True`.
- Es wird nichts persistiert.
- Es werden keine externen Lookups genutzt.
- Zielpfad liegt unter `local_data/exports`.
- Der Builder erstellt keine Ordner.
- Secrets und sensible Payloads sind ausgeschlossen.
- Der harte Token lautet `DATEN EXPORTIEREN`.
- Alle Sections markieren sensible Details als ausgeschlossen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine CLI-Anbindung.
- Keine Dateioperation im Modell.
- Keine Datenbankabfrage.
- Keine Netzwerkaktion.
- Keine externen Provider.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export Guard Plan` folgen. Dieser sollte festlegen, welche Bedingungen spaeter erfuellt sein muessen, bevor ein echter lokaler Export erlaubt wird, zum Beispiel Zielpfad unter `local_data/exports`, harter Token `DATEN EXPORTIEREN`, Safety Smoke PASS und Ausschluss sensibler Inhalte.
