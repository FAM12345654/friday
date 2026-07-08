# Local Data Export CLI Approval Plan

## Ziel

Dieser Plan beschreibt, wie ein echter lokaler Datenexport spaeter sicher aus der CLI gestartet werden darf.

Der Schritt ist bewusst nur Planung:

- keine Produktlogik,
- kein neuer Menuepunkt,
- kein Token-Prompt,
- kein Writer-Aufruf,
- kein Export,
- keine Tests.

## Ausgangslage

Vorhanden sind bereits:

- Export-Preview ohne Dateioperation,
- Export-Guard mit Zielpfad-, Token-, Safety-Smoke- und Exclude-Pruefung,
- Export-Writer fuer explizit uebergebene Daten,
- read-only CLI-Preview im Backup-/Restore-Menue.

Noch nicht freigegeben ist:

- echter Export aus der CLI,
- automatische Datensammlung aus Repositories,
- Token-Abfrage im Interface,
- Writer-Aufruf aus dem Interface.

## Geplanter CLI-Ablauf

Ein spaeterer CLI-Export sollte in getrennten Schritten ablaufen:

1. Export-Preview anzeigen.
2. Safety Smoke Status anzeigen.
3. Guard-Voraussetzungen anzeigen.
4. Harten Token abfragen.
5. Nur bei exakt `DATEN EXPORTIEREN` fortfahren.
6. Exportdaten lokal und explizit zusammenstellen.
7. Guard ausfuehren.
8. Nur bei erlaubtem Guard-Ergebnis Writer aufrufen.
9. Ergebnisordner anzeigen.

## Harter Token

Der einzige geplante Export-Token ist:

```text
DATEN EXPORTIEREN
```

Nicht erlaubt sind:

- `ja`,
- `JA`,
- `ok`,
- `export`,
- leere Eingabe,
- abweichende Schreibweisen.

## Safety Smoke vor Export

Vor dem Token-Prompt sollte Friday anzeigen, ob der lokale Safety Smoke zuletzt erfolgreich war.

Ein echter Export darf nur starten, wenn:

- Safety Smoke `PASS` ist,
- Guard `allowed=True` liefert,
- Zielpfad unter `local_data/exports` liegt,
- ausgeschlossene Bereiche weiterhin ausgeschlossen sind.

## Guard-Blockiergruende im CLI

Wenn der Guard blockiert, soll die CLI verstaendlich ausgeben:

- Export wurde nicht erstellt.
- Grund: Token fehlt oder ist falsch.
- Grund: Zielpfad liegt ausserhalb von `local_data/exports`.
- Grund: Safety Smoke ist nicht PASS.
- Grund: erforderliche Ausschluesse fehlen.
- Grund: sensible Kontaktdetails waeren enthalten.

Die Ausgabe soll keine sensiblen Daten wiederholen.

## Abbruchpfade

Der Export muss ohne Dateioperation abbrechen bei:

- Enter/leerer Eingabe,
- falschem Token,
- Guard-Blockierung,
- Safety Smoke nicht PASS,
- Zielpfad ausserhalb des erlaubten Bereichs,
- bereits vorhandenem Exportziel, falls Ueberschreiben nicht separat freigegeben ist.

## Datenquellen fuer spaetere Implementierung

Die spaetere Implementierung darf nur lokale Daten verwenden:

- lokale Aufgaben,
- lokale Kontakt-Kontexte ohne sensible ausgeschlossene Felder,
- lokale Review-Historie oder Vorschlagsmetadaten ohne Rohdaten,
- Safety-/Manifest-Informationen.

Nicht exportiert werden duerfen:

- aktive SQLite-Datenbank als Rohdatei,
- `.env`,
- Secrets,
- API-Keys,
- Obsidian Vault,
- Cache-/Temp-Dateien,
- sensible Kontakt-Freitexte,
- externe Providerdaten.

## Vorgeschlagene Tests fuer die spaetere Implementierung

Wenn der echte CLI-Export gebaut wird, sollten Tests absichern:

- Preview bleibt weiterhin read-only.
- Falscher Token erstellt keinen Export.
- Leere Eingabe erstellt keinen Export.
- Exakt `DATEN EXPORTIEREN` kann Export starten, wenn Guard erlaubt.
- Guard-Blockierung verhindert Writer-Aufruf.
- Safety Smoke FAIL verhindert Export.
- Exportziel bleibt unter `local_data/exports`.
- Erfolgreicher Export erzeugt erwartete Dateien.
- Keine sensiblen ausgeschlossenen Daten erscheinen im Export.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Kein Export erstellt.
- Kein Writer aufgerufen.
- Kein Token-Prompt eingebaut.
- Keine Datenbank gelesen.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine Netzwerkaktion.
- Safety-Flags unveraendert.
- Delete-Policy unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt kann `Local Data Export CLI Approval Implementation` folgen.

Dieser Schritt sollte den echten CLI-Export nur dann anbinden, wenn:

- Safety Smoke PASS ist,
- der Nutzer exakt `DATEN EXPORTIEREN` eingibt,
- der Guard erlaubt,
- der Writer nur unter `local_data/exports` schreibt,
- Tests alle Abbruch- und Erfolgsfaelle abdecken.
