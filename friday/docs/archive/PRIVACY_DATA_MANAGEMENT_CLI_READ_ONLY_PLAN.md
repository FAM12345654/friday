# Privacy Data Management CLI Read-Only Plan

## Ziel

Dieser Plan beschreibt, wie das read-only Privacy Data Management Inventory spaeter im bestehenden Privacy Dashboard angezeigt werden kann.

Der Schritt bleibt bewusst Plan-only:

- keine Produktlogik,
- keine neue CLI-Option,
- keine Aenderung an `friday/app/interface.py`,
- keine Aenderung an `friday/app/menu.py`,
- keine Loeschfunktion,
- keine Exportfunktion,
- keine externen Aktionen,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Vorhanden sind:

- `friday/app/privacy_dashboard.py`
- `friday/app/privacy_data_management.py`
- `friday/tests/test_privacy_dashboard.py`
- `friday/tests/test_privacy_data_management.py`
- `friday/docs/PRIVACY_DATA_MANAGEMENT_READINESS_GATE.md`

Das bestehende Privacy Dashboard ist bereits read-only und hat aktuell diese Bereiche:

| Menuepunkt | Funktion | Schreibt Daten? |
|---|---|---|
| `1` | Lokale Datenbereiche anzeigen | Nein |
| `2` | Safety-Flags anzeigen | Nein |
| `3` | Externe Aktionen anzeigen | Nein |
| `4` | Gated Actions anzeigen | Nein |
| `5` | Safety Scanner anzeigen | Nein |
| `6` | Zurueck zum Hauptmenue | Nein |

## Geplante CLI-Anbindung

Das Privacy Data Management Inventory soll spaeter als zusaetzlicher read-only Bereich im Privacy Dashboard erscheinen.

Empfohlene Menue-Erweiterung:

| Neuer Menuepunkt | Text | Verhalten |
|---|---|---|
| `6` | Privacy Data Management Inventory anzeigen | zeigt Inventory read-only |
| `7` | Zurueck zum Hauptmenue | verlaesst Privacy Dashboard |

Dabei muessten spaeter `show_privacy_dashboard_menu()` und `open_privacy_dashboard_menu()` angepasst werden.

## Geplante Anzeige

Die spaetere Anzeige soll nur zusammenfassen:

- Datenbereich,
- Speicherart,
- Pfad,
- sichtbare Zusammenfassung,
- aktueller Zugriff,
- spaetere Pflegeidee,
- Safety-Grenze,
- Count-Label,
- blockierte riskante Aktionen.

Sensitive Details werden nicht angezeigt.

Beispiel:

```text
Privacy Data Management Inventory
- Aufgaben
  Speicher: SQLite lokal
  Pfad: local_data/friday.db
  Sichtbarkeit: Anzahl, Status und lokaler DB-Bezug
  Pflege: spaeter gezielte lokale Pflege ueber bestehende Task-Gates
  Safety: keine Massenloeschung ohne eigenes Gate
```

## Bewusst nicht geplant fuer diese Anbindung

- Kein Loeschen aus dem Privacy Dashboard.
- Kein Export aus dem Privacy Dashboard.
- Kein Import aus dem Privacy Dashboard.
- Kein Restore aus dem Privacy Dashboard.
- Kein Obsidian Vault Scan.
- Kein Anzeigen sensibler Kontakt-Freitexte.
- Kein direkter Zugriff auf externe Provider.
- Keine automatische Datenbereinigung.
- Keine neue Datenbanktabelle.

## Testplan fuer spaeteren Implementierungsschritt

Wenn die read-only CLI-Anbindung spaeter umgesetzt wird, sollten Tests pruefen:

- Privacy Dashboard zeigt neuen Inventory-Menuepunkt.
- Inventory-Ausgabe enthaelt Datenbereiche wie Aufgaben, Kontakte, Exporte, Backups und Scanner.
- Inventory-Ausgabe enthaelt blockierte Aktionen.
- Sensitive Details werden nicht angezeigt.
- Ungueltige Eingaben bleiben stabil.
- Rueckkehr zum Hauptmenue funktioniert.
- Es werden keine Dateien erstellt.
- Es werden keine Daten geloescht.
- Es werden keine Daten exportiert.

Empfohlene Fokus-Tests:

```powershell
python -m pytest friday/tests/test_privacy_dashboard.py
python -m pytest friday/tests/test_privacy_data_management.py
python -m pytest friday/tests/test_interface_main_menu_e2e.py
```

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine Loeschfunktion.
- Keine Exportfunktion.
- Keine neue CLI-Anbindung in diesem Schritt.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Data Management CLI Read-Only Implementation`

Ziel: Das Inventory als zusaetzliche read-only Anzeige im bestehenden Privacy Dashboard anbinden, ohne Loesch-, Export-, Import- oder externe Aktionen einzubauen.
