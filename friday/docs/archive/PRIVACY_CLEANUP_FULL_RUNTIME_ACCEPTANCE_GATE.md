# Privacy Cleanup Full Runtime Acceptance Gate

## Ziel

Dieses Dokument nimmt den gesamten lokalen Privacy-Cleanup-Runtime-Block final ab.

Abgedeckt sind:

- Privacy Dashboard,
- Privacy Data Management Inventory,
- Datei-Cleanup Preview,
- guarded Datei-Cleanup Write,
- DB-Cleanup Preview,
- guarded DB-Cleanup Write,
- Runtime Smoke Guide,
- README-Nutzerfuehrung,
- Doku-Index,
- Safety Smoke.

## Gepruefte Runtime-Bereiche

| Bereich | Status | Ergebnis |
|---|---|---|
| Privacy Dashboard | umgesetzt | Menuepunkte fuer Anzeige, Datei-Cleanup und DB-Cleanup vorhanden |
| Datei-Cleanup Preview | stabil | Read-only, ohne Token-Abfrage und ohne Write |
| Datei-Cleanup Write | stabil gegatet | Nur mit Safety Smoke, Guard und hartem Token |
| DB-Cleanup Preview | stabil | Read-only, ohne Guard/Writer und ohne DB-Loeschung |
| DB-Cleanup Write | stabil gegatet | Nur mit Backup-Nachweis, Safety Smoke, Guard und hartem Token |
| Runtime Summary | aktualisiert | Datei-Cleanup und DB-Cleanup gemeinsam dokumentiert |
| Runtime Smoke Guide | aktualisiert | Menuepunkte, Fokus-Tests, Tokens und gesperrte Bereiche synchron |
| README User Guide | aktualisiert | Nutzerpfade fuer Preview und Ausfuehrung dokumentiert |
| Doku-Index | aktualisiert | Privacy-Cleanup-Runtime-Block zeigt aktuellen Stand |

## Aktuelle Privacy-Dashboard-Menuepunkte

```text
1. Lokale Datenbereiche anzeigen
2. Safety-Flags anzeigen
3. Externe Aktionen anzeigen
4. Gated Actions anzeigen
5. Safety Scanner anzeigen
6. Privacy Data Management Inventory anzeigen
7. Privacy Cleanup Preview anzeigen
8. Privacy Cleanup ausfuehren
9. DB-Cleanup Preview anzeigen
10. DB-Cleanup ausführen
11. Zurueck zum Hauptmenue
```

## Harte Tokens

| Bereich | Token |
|---|---|
| Exporte | `EXPORT AUFRAEUMEN` |
| Backups | `BACKUP AUFRAEUMEN` |
| Restore-Kopien | `RESTORE AUFRAEUMEN` |
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

## Finales Acceptance-Ergebnis

- Datei-Cleanup ist lokal, guarded und tokenpflichtig.
- DB-Cleanup ist lokal, backup-geschuetzt, guarded und tokenpflichtig.
- Read-only Previews loeschen nichts und schreiben nichts.
- Safety Smoke ist fuer Cleanup-Writes Pflicht.
- DB-Cleanup benoetigt zusaetzlich einen lokalen Backup-Nachweis.
- Falsche Tokens blockieren Cleanup.
- `ja` und `JA` reichen fuer Privacy Cleanup nicht aus.
- Pending Vorschlaege, Aufgaben, Nachrichten und Kalenderdaten bleiben fuer DB-Cleanup blockiert.
- Obsidian-Cleanup bleibt blockiert.
- Externe Aktionen bleiben deaktiviert.

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

## Validierung

```powershell
python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_privacy_cleanup_writer.py friday/tests/test_privacy_cleanup_write_guard.py friday/tests/test_privacy_cleanup_db_preview.py friday/tests/test_privacy_cleanup_db_guard.py friday/tests/test_privacy_cleanup_db_writer.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup Block Closure Summary**.

Ziel:

- Den Privacy-Cleanup-Block als abgeschlossen markieren.
- Kurze Uebersicht fuer Nutzer und Entwickler erstellen.
- Danach wieder zu produktiven lokalen Features wechseln.
