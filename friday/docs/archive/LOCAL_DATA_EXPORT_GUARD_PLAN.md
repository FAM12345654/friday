# Local Data Export Guard Plan

## Ziel

Dieses Dokument plant den Schutzmechanismus fuer einen spaeteren echten lokalen Datenexport.

Der Schritt bleibt bewusst dokumentationsorientiert. Es wird noch kein Export geschrieben, kein ZIP erzeugt, keine Datenbank gelesen und keine CLI-Aktion eingebaut.

## Ausgangslage

Vorhanden ist bereits:

- `LOCAL_DATA_EXPORT_READINESS_PLAN.md`
- `LOCAL_DATA_EXPORT_PREVIEW_MODEL.md`
- `friday/app/local_data_export_preview.py`
- `friday/tests/test_local_data_export_preview.py`

Das Preview-Modell beschreibt nur, welche Daten spaeter exportiert werden koennten. Der Guard soll im naechsten technischen Schritt entscheiden, ob ein echter Export ueberhaupt erlaubt waere.

## Geplante Guard-Regeln

| Regel | Bedeutung |
|---|---|
| Zielpfad unter `local_data/exports` | Export darf nicht ausserhalb des lokalen Exportordners landen |
| Harter Token `DATEN EXPORTIEREN` | Weiche Eingaben wie `ja` oder `ok` duerfen keinen Export ausloesen |
| Safety Smoke muss PASS sein | Scanner muessen vor Exportfreigabe sauber sein |
| Preview muss vorhanden sein | Export darf nur auf Basis des Preview-Modells geplant werden |
| Excludes muessen aktiv sein | `.env`, Tokens, Cache-Dateien, Obsidian Vault und rohe DB-Kopie bleiben ausgeschlossen |
| Keine externen Aktionen | Kein Netzwerk, keine Provider, keine Cloud, keine echten Nachrichten |
| Keine Datenbankschema-Aenderung | Export-Guard darf keine Migration erfordern |

## Geplantes Guard-Ergebnis

Der spaetere Guard sollte ein reines Ergebnisobjekt liefern, zum Beispiel:

| Feld | Bedeutung |
|---|---|
| `allowed` | Ob Export erlaubt waere |
| `reason` | Kurze maschinenlesbare Begruendung |
| `target_root` | Geplanter lokaler Zielpfad |
| `approval_token_required` | Erwarteter harter Token |
| `scanner_smoke_required` | Ob Safety Smoke erforderlich ist |
| `blocked_items` | Liste blockierter Inhalte |
| `preview_only` | Guard selbst bleibt ohne Export |
| `persisted` | Guard speichert nichts |
| `external_lookup_used` | Guard nutzt keine externen Quellen |

## Blockierfaelle

Der Guard soll blockieren, wenn:

- der Token nicht exakt `DATEN EXPORTIEREN` ist,
- der Zielpfad nicht unter `local_data/exports` liegt,
- Safety Smoke nicht PASS ist,
- das Preview-Modell fehlt,
- ausgeschlossene Inhalte im Exportplan auftauchen,
- ein externer Provider oder Netzwerkzugriff beteiligt waere,
- ein Export rohe aktive Datenbankkopien enthalten wuerde,
- ein Export Obsidian Vault oder Secrets enthalten wuerde.

## Nicht-Ziele

- Kein echter Export.
- Kein ZIP.
- Keine CLI-Anbindung.
- Keine Datenbankabfrage.
- Keine Migration.
- Kein Kontaktimport.
- Kein Obsidian Write.
- Keine echten E-Mails, SMS, WhatsApp-Nachrichten oder Kalenderaktionen.
- Kein Modell-/Provider-Aufruf.

## Geplanter Testumfang fuer den naechsten technischen Schritt

Eine spaetere Guard-Implementierung sollte Tests enthalten fuer:

- exakter Token `DATEN EXPORTIEREN` erlaubt den Guard-Pfad,
- `ja`, `JA`, `ok`, leere Eingabe und Whitespace blockieren,
- Zielpfad ausserhalb `local_data/exports` blockiert,
- Safety Smoke FAIL blockiert,
- fehlendes Preview blockiert,
- ausgeschlossene Inhalte blockieren,
- Guard erstellt keine Dateien,
- Guard liest keine Datenbank,
- Guard nutzt keine externen Aktionen.

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

Als naechster Schritt sollte das `Local Data Export Guard Model` umgesetzt werden:

- isoliertes Guard-Modell in Python,
- keine CLI-Anbindung,
- keine Dateioperation,
- keine Datenbankabfrage,
- Tests fuer Token, Zielpfad, Safety Smoke und Excludes,
- Full Regression, Compilecheck, Safety Smoke und `git diff --check`.
