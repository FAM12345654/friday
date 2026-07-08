# Next Local Product Feature Planning

## Ziel

Dieses Dokument waehlt den naechsten kleinen lokalen Produktblock nach dem abgeschlossenen lokalen Tagesplan-Block aus.

Der Schritt bleibt bewusst planend:

- keine Produktlogik-Aenderung,
- keine neuen Tests,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen,
- keine echten Nachrichten oder Kalenderaktionen.

## Ausgangslage

Der lokale Tagesplan-Block ist abgeschlossen und read-only nutzbar.

Stabil dokumentierte Bereiche:

- Hauptmenue und Aufgabenmenue,
- lokale Aufgabenverwaltung,
- Review- und Suggestion-Flows,
- Kontakt-Kontext-Flows,
- Obsidian Preview/Write-Gate,
- Backup/Restore,
- Privacy Dashboard und Cleanup,
- Local Data Export/Import/Apply,
- lokale Tagesplanung.

## Bewertete Optionen

| Option | Nutzen | Risiko | Testaufwand | Empfehlung |
|---|---|---|---|---|
| Local Review Batch Selection | Hoch: mehrere Vorschlaege schneller bearbeiten | Niedrig bis mittel, solange nur Parser/Preview gebaut wird | Mittel | empfohlen |
| Day Plan Apply | Hoch, aber schreibt Task-/Planungsstatus | Mittel bis hoch | Hoch | spaeter nach eigenem Safety-Gate |
| Contact Context Search Polish | Mittel: bessere Suche im Kontaktbereich | Niedrig | Mittel | sinnvoll, aber weniger wirksam als Review-Batch |
| Local Task Focus View | Mittel: Zusatzansicht zu Tagesplanung | Niedrig | Mittel | spaeter moeglich, teilweise Ueberschneidung mit Tagesplan |
| Review History Summary View | Mittel: bessere Nachvollziehbarkeit | Mittel, je nach Persistenz | Mittel bis hoch | spaeter nach Datenmodell-Check |

## Empfohlener naechster Produktblock

**Local Review Batch Selection**

Empfohlener Start:

```text
Review Batch Selection Parser Plan
```

Der erste Schritt soll nur planen, wie Batch-Eingaben fuer Review-Vorschlaege verstanden werden.

Beispiele fuer spaetere Eingaben:

```text
1,2,3
all
none
z
```

## Warum dieser Block

- Nutzer koennen spaeter mehrere Vorschlaege effizienter bearbeiten.
- Der Einstieg kann komplett side-effect-free bleiben.
- Ein Parser kann isoliert getestet werden.
- Keine Nachricht wird gesendet.
- Keine Aufgabe wird erstellt.
- Kein Kalendertermin wird erstellt.
- Keine Datenbankmigration ist erforderlich.
- Bestehende Review-Safety bleibt erhalten.

## Nicht-Ziele

Dieser Planungsschritt baut noch nicht:

- keine Batch-Anwendung,
- keine Statusaenderung an Vorschlaegen,
- keine neue CLI-Aktion,
- keinen echten Versand,
- keine echte Kalenderaktion,
- keine automatische Task-Erstellung,
- keine Datenbankschema-Aenderung.

## Safety-Grenzen fuer den naechsten Block

- Batch Parser darf nur Eingaben interpretieren.
- Batch Parser darf keine Aktionen ausfuehren.
- Batch Parser darf keine DB lesen oder schreiben.
- Batch Parser darf keine externen Dienste importieren.
- Batch Parser darf kein `input()` oder `print()` nutzen.
- Review-Aktionen bleiben weiter explizit und lokal.
- Externe Aktionen bleiben deaktiviert.

## Vorgeschlagener Testplan fuer den Folgeblock

Fuer den spaeteren Parser-Model-Schritt:

- `1,2,3` wird als konkrete ID-Auswahl erkannt.
- Doppelte IDs werden kontrolliert behandelt.
- Whitespace wird stabil verarbeitet.
- `all` wird als alle sichtbaren Vorschlaege erkannt.
- `none` wird als keine Auswahl erkannt.
- `z` wird als Ruecksprung erkannt.
- Sonderzeichen und ungueltige Eingaben liefern einen Invalid-Status.
- Parser bleibt ohne Seiteneffekte.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster Build Step: **Review Batch Selection Parser Plan**.

Ziel:

- Parser-Verhalten fuer Batch-Auswahl planen,
- keine Review-Aktionen ausfuehren,
- keine CLI-Anbindung bauen,
- keine Persistenz aendern,
- Safety-Grenzen fuer spaetere Batch-Aktionen dokumentieren.
