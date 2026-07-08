# Privacy Cleanup CLI Read-Only Preview Plan

## Ziel

Dieser Plan beschreibt, wie die Privacy Cleanup Preview spaeter read-only im Privacy Dashboard angezeigt werden kann.

Der Schritt bleibt bewusst Plan-only:

- keine Produktlogik,
- keine CLI-Aenderung,
- keine Tests,
- keine Loeschfunktion,
- keine Exportfunktion,
- kein Dateizugriff,
- kein SQLite-Zugriff,
- keine externen Aktionen.

## Ausgangslage

Das Privacy Dashboard hat aktuell:

| Menuepunkt | Funktion |
|---|---|
| `1` | Lokale Datenbereiche anzeigen |
| `2` | Safety-Flags anzeigen |
| `3` | Externe Aktionen anzeigen |
| `4` | Gated Actions anzeigen |
| `5` | Safety Scanner anzeigen |
| `6` | Privacy Data Management Inventory anzeigen |
| `7` | Zurueck zum Hauptmenue |

Das Preview-Modell `friday/app/privacy_cleanup_preview.py` ist isoliert und read-only.

## Geplante CLI-Erweiterung

Spaeter soll das Privacy Dashboard erweitert werden:

| Neuer Menuepunkt | Funktion | Schreibt Daten? |
|---|---|---|
| `7` | Privacy Cleanup Preview anzeigen | Nein |
| `8` | Zurueck zum Hauptmenue | Nein |

Dafuer muessten spaeter angepasst werden:

- `friday/app/menu.py`
- `friday/app/interface.py`
- `friday/tests/test_menu.py`
- `friday/tests/test_interface_main_menu_e2e.py`

## Geplante Anzeige

Die Anzeige soll nur aus dem Preview-Modell lesen und Folgendes zeigen:

- Bereich,
- Cleanup-Typ,
- Zielpfad als Text,
- erlaubter Root,
- Count-Label,
- erforderlicher spaeterer Token,
- erlaubt/blockiert,
- Blockiergruende.

Beispiel:

```text
Privacy Cleanup Preview
Hinweis: Diese Ansicht ist read-only.
Es wird nichts geloescht.

- Exporte
  Ziel: local_data/exports
  Erforderlicher Token: EXPORT AUFRAEUMEN
  Status: erlaubt fuer spaetere Preview

- aktive SQLite-DB
  Status: blockiert
  Grund: active_database_blocked
```

## Nicht-Ziele

- Kein Cleanup ausfuehren.
- Kein Token abfragen.
- Kein Dateisystem scannen.
- Keine Dateien lesen.
- Keine Dateien loeschen.
- Keine SQLite-Datenbank oeffnen.
- Keine Datenbankzeilen loeschen.
- Keine automatische Bereinigung.
- Kein Obsidian Vault Cleanup.
- Kein In-Place-Restore.

## Testplan fuer spaetere Implementierung

Spaetere Tests sollten pruefen:

- Privacy Dashboard zeigt neuen Cleanup-Preview-Menuepunkt.
- Rueckkehr erfolgt stabil ueber den neuen Zurueck-Menuepunkt.
- Cleanup Preview zeigt erlaubte Bereiche wie Exporte, Backups und Restore-Kopien.
- Cleanup Preview zeigt blockierte Bereiche wie aktive SQLite-DB, Secrets und Obsidian Vault.
- Ausgabe enthaelt klare read-only Hinweise.
- Es werden keine lokalen Pfade erstellt.
- Es werden keine Daten geloescht.
- Ungueltige Eingaben bleiben stabil.

Empfohlene Fokus-Tests:

```powershell
python -m pytest friday/tests/test_menu.py
python -m pytest friday/tests/test_privacy_cleanup_preview.py
python -m pytest friday/tests/test_interface_main_menu_e2e.py
```

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Loeschpfade.
- Keine neuen Exportpfade.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Cleanup CLI Read-Only Preview Implementation`

Ziel: Die Cleanup Preview als read-only Anzeige im Privacy Dashboard anbinden, ohne Cleanup-Ausfuehrung, Token-Abfrage, Dateizugriff oder SQLite-Zugriff.
