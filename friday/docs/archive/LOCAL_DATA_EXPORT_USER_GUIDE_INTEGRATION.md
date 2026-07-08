# Local Data Export User Guide Integration

## Ziel

Dieses Dokument beschreibt die Nutzer-Doku-Ergaenzung fuer den lokalen Datenexport.

Der Datenexport ist im Backup-/Restore-Menue sichtbar und bleibt lokal, guard-basiert und hart gegatet.

## Nutzerpfad

Der lokale Datenexport liegt im Hauptmenue unter:

```text
11. Backup / Restore
5. Lokaler Datenexport Vorschau anzeigen
```

Beim Auswaehlen zeigt Friday zuerst eine Vorschau an.

Danach prueft Friday den lokalen Safety Smoke.

Ein Export wird nur erstellt, wenn der Nutzer exakt diesen Token eingibt:

```text
DATEN EXPORTIEREN
```

## Was exportiert wird

Friday exportiert nur lokale Zusammenfassungen:

- lokale Aufgaben,
- lokale Kontakt-Kontexte,
- lokale Review-/Vorschlags-Zusammenfassungen,
- lokaler Safety-Status,
- Export-Manifest,
- Export-Hinweise.

## Was nicht exportiert wird

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

## Safety-Regeln

- Export nur lokal unter `local_data/exports/`.
- Export nur nach Safety Smoke PASS.
- Export nur nach Guard-Freigabe.
- Export nur mit hartem Token `DATEN EXPORTIEREN`.
- Falsche Tokens wie `JA`, `ja`, `ok` oder leere Eingabe erstellen keinen Export.
- Es werden keine externen Aktionen ausgefuehrt.

## Geaenderte Nutzer-Doku

Ergaenzt wurde:

- `friday/docs/README_USER.md`

Der Abschnitt `Backup / Restore` erklaert jetzt:

- lokalen Datenexport im Menue,
- Token `DATEN EXPORTIEREN`,
- Safety Smoke vor Export,
- exportierte lokale Zusammenfassungen,
- ausgeschlossene sensible Inhalte.

## Tests

Dieser Schritt aendert keine Tests.

Die bestehende Absicherung liegt in:

- `friday/tests/test_interface_main_menu_e2e.py`,
- `friday/tests/test_local_data_export_guard.py`,
- `friday/tests/test_local_data_export_writer.py`.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externe Aktion.
- Keine Netzwerkaktion.
- Keine Datenbankschema-Aenderung.
- Delete-Policy unveraendert.
- Safety-Flags unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export Final Acceptance Gate` folgen.

Dieses Gate sollte dokumentieren:

- CLI-Export ist lokal freigegeben,
- Safety Smoke und Guard sind Pflicht,
- Doku ist aktualisiert,
- Tests bleiben gruen,
- keine externen Aktionen sind aktiv.
