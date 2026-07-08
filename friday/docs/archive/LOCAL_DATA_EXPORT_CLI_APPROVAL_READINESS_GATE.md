# Local Data Export CLI Approval Readiness Gate

## Ziel

Dieses Gate prueft den lokalen CLI-Datenexport nach der Approval-Implementation.

Der Datenexport ist fuer lokale Nutzung freigegeben, bleibt aber strikt gegated.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/interface.py` | CLI ruft Preview, Safety Smoke, Token-Abfrage, Guard und Writer kontrolliert auf |
| `friday/app/local_data_export_guard.py` | Guard prueft Token, Zielpfad, Safety Smoke und Excludes |
| `friday/app/local_data_export_writer.py` | Writer schreibt nur explizite Payload unter `local_data/exports` |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Abbruch, falscher Token und erfolgreicher Export getestet |
| `friday/tests/test_local_data_export_guard.py` | Guard-Regeln getestet |
| `friday/tests/test_local_data_export_writer.py` | Writer-Regeln getestet |

## Readiness-Ergebnis

- CLI-Export bleibt lokal.
- Preview wird vor dem Token angezeigt.
- Safety Smoke wird vor dem Token geprueft.
- Safety Smoke FAIL blockiert den Export.
- Enter/leere Eingabe bricht ohne Export ab.
- Falscher Token wie `JA` schreibt nichts.
- Exakter Token `DATEN EXPORTIEREN` kann nur bei Guard-Freigabe exportieren.
- Exportziel bleibt unter `local_data/exports`.
- Writer erstellt Manifest, Aufgaben, Kontakte, Review-Summary, Safety-Summary und Export-Notiz.
- Kontakt- und Review-Daten werden gefiltert.
- Rohe aktive Datenbank wird nicht exportiert.
- Obsidian Vault wird nicht exportiert.
- Secrets und `.env` bleiben ausgeschlossen.

## Nicht freigegeben

Weiterhin nicht freigegeben sind:

- Cloud-Export,
- externe Provider,
- echter Nachrichtenversand,
- echte Kalenderaktionen,
- Export der aktiven SQLite-Datenbank als Rohdatei,
- Export von `.env`,
- Export von API-Keys oder Tokens,
- Export des Obsidian Vault,
- Export sensibler Kontakt-Freitexte.

## Tests

Fokus-Tests:

- `python -m pytest friday/tests/test_interface_main_menu_e2e.py friday/tests/test_local_data_export_guard.py friday/tests/test_local_data_export_writer.py`

Vollvalidierung:

- `python -m pytest friday/tests`
- `python -m compileall friday`
- `python scripts/friday_safety_smoke.py`
- `git diff --check`

## Safety-Bewertung

- Keine externen Aktionen.
- Keine Netzwerkaktionen.
- Keine Cloud.
- Keine echten Nachrichten.
- Keine echten Kalenderaktionen.
- Keine Datenbankschema-Aenderung.
- Lokaler Export nur unter `local_data/exports`.
- Harter Token `DATEN EXPORTIEREN` erforderlich.
- Safety Smoke PASS erforderlich.
- Guard-Freigabe erforderlich.
- Delete-Policy unveraendert.
- Safety-Flags unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte `Local Data Export User Guide Integration` folgen.

Dieser Schritt sollte die Nutzer-Doku aktualisieren:

- wo der lokale Datenexport im Menue liegt,
- dass der Token `DATEN EXPORTIEREN` erforderlich ist,
- was exportiert wird,
- was bewusst ausgeschlossen bleibt,
- dass alles lokal bleibt.
