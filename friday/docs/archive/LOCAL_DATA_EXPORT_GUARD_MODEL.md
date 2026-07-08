# Local Data Export Guard Model

## Ziel

Dieses Dokument beschreibt das isolierte Guard-Modell fuer einen spaeteren lokalen Datenexport.

Der Guard entscheidet nur, ob ein Export erlaubt waere. Er erzeugt keinen Export, erstellt keine Ordner, liest keine Datenbank und ist nicht an die CLI angebunden.

## Implementierte Datei

| Datei | Zweck |
|---|---|
| `friday/app/local_data_export_guard.py` | Isoliertes Guard-Modell fuer lokalen Datenexport |
| `friday/tests/test_local_data_export_guard.py` | Tests fuer Token, Zielpfad, Safety Smoke, Excludes und Safe-Flags |

## Guard-Regeln

| Regel | Verhalten |
|---|---|
| Preview erforderlich | Ohne Preview wird blockiert |
| Exakter Token erforderlich | Nur `DATEN EXPORTIEREN` erlaubt den Guard-Pfad |
| Ziel unter `local_data/exports` | Andere Zielpfade werden blockiert |
| Safety Smoke PASS erforderlich | Fehlender Smoke-Pass blockiert |
| Pflicht-Ausschluesse erforderlich | `.env`, Tokens, Cache, Obsidian Vault, private Nachrichten und rohe aktive DB muessen ausgeschlossen sein |
| Sensible Details ausgeschlossen | Jede Section muss sensible Details ausschliessen |

## Blockiergruende

| Grund | Bedeutung |
|---|---|
| `missing_preview` | Kein Preview-Modell vorhanden |
| `invalid_token` | Token ist nicht exakt `DATEN EXPORTIEREN` |
| `target_outside_exports` | Zielpfad liegt nicht unter `local_data/exports` |
| `scanner_smoke_failed` | Safety Smoke ist nicht PASS |
| `required_exclusion_missing` | Mindestens ein Pflicht-Ausschluss fehlt |
| `sensitive_details_not_excluded` | Eine Section wuerde sensible Details nicht ausschliessen |

## Abgesicherte Tests

Abgedeckt durch `friday/tests/test_local_data_export_guard.py`:

- gueltiges Preview plus exakter Token erlaubt den Guard-Pfad,
- fehlendes Preview blockiert,
- falsche Tokens blockieren,
- Token mit angehaengtem Leerzeichen blockiert,
- Safety Smoke FAIL blockiert,
- Ziel ausserhalb `local_data/exports` blockiert,
- fehlender Pflicht-Ausschluss blockiert,
- sensible Details in einer Section blockieren,
- Guard-Flags bleiben preview-only, nicht persistiert und ohne externe Lookups,
- Guard erstellt keinen Exportordner,
- gepruefte Sections werden im Ergebnis ausgewiesen.

## Nicht-Ziele

- Kein echter Export.
- Kein ZIP.
- Keine CLI-Anbindung.
- Keine Datenbankabfrage.
- Keine Migration.
- Kein Obsidian Write.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Kein Modell-/Provider-Aufruf.

## Safety-Bewertung

- Keine externe Aktion.
- Keine Netzwerkaktion.
- Keine Dateioperation im Guard.
- Keine Datenbankschema-Aenderung.
- Keine Safety-Flag-Aenderung.
- Delete-Policy unveraendert.
- Safety Smoke PASS.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export Guard Readiness Gate` folgen. Dieses Gate sollte pruefen, ob Preview und Guard sauber getrennt sind, keine Dateioperationen enthalten, scanner-clean bleiben und fuer eine spaetere CLI-/Export-Planung freigegeben werden koennen.
