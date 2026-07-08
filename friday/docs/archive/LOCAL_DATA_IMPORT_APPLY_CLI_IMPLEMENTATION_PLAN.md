# Local Data Import Apply CLI Implementation Plan

## Ziel

Dieses Dokument plant eine spaetere sichere CLI-Implementierung fuer einen lokalen Import-Apply-Write.

Der Schritt ist bewusst plan-only:

- keine Produktlogik,
- keine Tests,
- kein neuer Menuepunkt,
- keine CLI-Token-Abfrage,
- kein Import,
- kein aktiver SQLite-Write,
- keine Datenbankschema-Aenderung.

## Ausgangsstand

Bereits vorhanden sind:

- read-only Import-Review im Backup-/Restore-Menue,
- read-only Import-Apply-Vorschau im Backup-/Restore-Menue,
- Import Apply Write Guard Model,
- Import Apply Writer Model,
- CLI Write Preview Gate.

Ein echter CLI-Import bleibt weiterhin nicht freigegeben.

## Spaeter erlaubte Aenderungsdateien

Eine spaetere Implementierung sollte nur diese Dateien anfassen:

| Datei | Zweck |
|---|---|
| `friday/app/interface.py` | neuer getrennter CLI-Handler fuer Import Apply |
| `friday/app/menu.py` | neuer getrennter Backup-/Restore-Menuepunkt |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-E2E-Tests fuer Token, Guard und Writer |
| `friday/tests/test_menu.py` | Menuepunkt-Test |
| `friday/docs/README_USER.md` | Nutzerhinweis erst nach Implementierung |
| `friday/docs/SAFETY_MATRIX.md` | Status nachziehen |
| `friday/docs/TEST_MATRIX.md` | Teststatus nachziehen |
| `friday/docs/cli_documentation_index_12l.md` | Doku-Index nachziehen |

Nicht noetig sein sollten:

- Datenbankschema-Dateien,
- Storage-Migrationen,
- Agent-Logik,
- externe Provider,
- Scanner-Code.

## Vorgeschlagener Menuepunkt

Der bestehende Punkt bleibt unveraendert:

```text
7. Import-Apply-Vorschau anzeigen
```

Ein spaeterer neuer Punkt sollte getrennt sein, zum Beispiel:

```text
8. Import nach Freigabe anwenden
9. Zurueck zum Hauptmenue
```

Wichtig: Der Preview-Punkt darf nicht still zum Write-Punkt werden.

## Vorgeschlagene CLI-Methode

Eine spaetere Methode koennte heissen:

```python
_apply_local_data_import_from_input()
```

Sie sollte:

1. Exportordner abfragen.
2. Manifest Reader ausfuehren.
3. Import Dry-Run ausfuehren.
4. Apply Preview bauen.
5. Backup-Schutz pruefen.
6. Safety Smoke ausfuehren.
7. Guard ausfuehren.
8. Bei Guard-Block keine Token-Abfrage machen.
9. Nur bei Guard allowed den Token `IMPORT ANWENDEN` abfragen.
10. Bei falschem Token abbrechen.
11. Writer aufrufen.
12. Ergebnis, created/skipped/rollback anzeigen.

## Token-Policy

Nur exakt:

```text
IMPORT ANWENDEN
```

darf spaeter den Writer starten.

Explizit nicht erlaubt:

- `ja`,
- `JA`,
- `ok`,
- `import`,
- `Import anwenden`,
- `IMPORT`,
- leere Eingabe,
- Eingaben mit fuehrenden oder nachgestellten Zeichen.

## Pflichtausgaben

Die CLI sollte spaeter mindestens anzeigen:

- Manifest-Status,
- Dry-Run-Status,
- Apply-Preview-Status,
- Guard-Status,
- Blockiergruende,
- Warnungen,
- Write-Scope,
- ob Token abgefragt wurde,
- Writer-Ergebnis,
- Rollback-Hinweis bei Fehler.

## Tests fuer spaetere Implementierung

Mindesttests:

- Menue zeigt getrennten Apply-Punkt.
- Preview-Punkt bleibt read-only.
- Guard blocked fragt keinen Token ab.
- Falscher Token schreibt nicht.
- `ja` schreibt nicht.
- `JA` schreibt nicht.
- Exakt `IMPORT ANWENDEN` ruft Writer nur bei Guard allowed auf.
- Writer-Block/Invalid/Rollback wird angezeigt.
- Erfolgreicher Writer zeigt created/skipped Counts.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.

## Nicht-Ziele

Dieser Plan baut nicht:

- CLI-Anbindung,
- Import-Menuepunkt,
- Token-Abfrage,
- Writer-Ausfuehrung aus der CLI,
- Datenbankmigration,
- In-Place-Restore,
- Konfliktloesungs-UI,
- externe Provider,
- Netzwerkaktionen.

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein CLI-Import implementiert.
- Kein neuer Menuepunkt.
- Kein Import ausgefuehrt.
- Kein aktiver SQLite-Write.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply CLI Implementation.

Dieser Schritt duerfte erstmals eine getrennte CLI-Anbindung bauen, muss aber Preview-Punkt und Apply-Punkt strikt trennen und mit Fokus-/Full-Regression validiert werden.
