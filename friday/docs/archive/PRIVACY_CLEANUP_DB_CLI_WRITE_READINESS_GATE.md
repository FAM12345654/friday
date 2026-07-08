# Privacy Cleanup DB CLI Write Readiness Gate

## Ziel

Dieses Gate prueft die neue guarded SQLite Privacy Cleanup DB Write-Anbindung im Privacy Dashboard.

Der Step bestaetigt:

- DB-Cleanup-Write ist nur ueber separaten Menuepunkt erreichbar,
- frische Preview ist Pflicht,
- lokaler Backup-Nachweis ist Pflicht,
- Safety Smoke ist Pflicht,
- harter Token ist Pflicht,
- DB Guard ist Pflicht,
- DB Writer laeuft nur bei Guard-Freigabe,
- keine externen Aktionen sind aktiv,
- keine Datenbankschema-Aenderung erfolgt.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/menu.py` | Privacy-Dashboard-Menue enthaelt DB-Cleanup Preview, DB-Cleanup Write und Zurueck |
| `friday/app/interface.py` | Guarded DB-Cleanup-Write-Flow vorhanden |
| `friday/app/privacy_cleanup_db_preview.py` | Read-only Preview-Modell vorhanden |
| `friday/app/privacy_cleanup_db_guard.py` | DB Guard vorhanden |
| `friday/app/privacy_cleanup_db_writer.py` | Guarded DB Writer vorhanden |
| `friday/tests/test_menu.py` | Menueoptionen abgesichert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Write-Blockierungs- und Erfolgspfade abgesichert |

## Readiness-Ergebnis

Die DB-Cleanup-Write-Anbindung ist bereit als lokal gegatete Privacy-Dashboard-Funktion.

Freigegeben ist:

- Review-History-Cleanup nach Preview, Backup, Safety Smoke, Token und Guard,
- Kontakt-Kontext-Cleanup fuer exakt ausgewaehlte `contact_id`,
- Anzeige sicherer Ergebniszaehler,
- Rueckkehr ins Privacy Dashboard nach Aktionen.

Nicht freigegeben ist:

- automatische Bereinigung,
- DB-Cleanup ohne Backup,
- DB-Cleanup ohne Safety Smoke,
- DB-Cleanup ohne harten Token,
- DB-Cleanup ohne Guard,
- Loeschung pending Vorschlaege,
- Loeschung aktiver Aufgaben,
- Loeschung aktiver Nachrichten,
- Loeschung von Kalenderdaten,
- Datenbankschema-Aenderung,
- externe Aktion.

## Aktueller Menue-Stand

```text
Privacy Dashboard
1. Lokale Datenbereiche anzeigen
2. Safety-Flags anzeigen
3. Externe Aktionen anzeigen
4. Gated Actions anzeigen
5. Safety Scanner anzeigen
6. Privacy Data Management Inventory anzeigen
7. Privacy Cleanup Preview anzeigen
8. Privacy Cleanup ausführen
9. DB-Cleanup Preview anzeigen
10. DB-Cleanup ausführen
11. Zurück zum Hauptmenü
```

## Abgesicherte Verhaltensweisen

| Verhalten | Status |
|---|---|
| DB-Cleanup Preview bleibt read-only | abgesichert |
| Fehlendes Backup blockiert Write | abgesichert |
| Falscher Token blockiert Write | abgesichert |
| Review-History Cleanup loescht nur sichere Kandidaten | abgesichert |
| Pending Vorschlaege bleiben erhalten | abgesichert |
| Lokale Aufgaben bleiben erhalten | abgesichert |
| Kontakt-Kontext Cleanup loescht nur ausgewaehlten Kontakt | abgesichert |
| Safety Smoke bleibt Bestandteil des Flows | abgesichert |

## Safety-Bewertung

- DB-Cleanup laeuft nur lokal.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine automatische Bereinigung.
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

## Tests

Erwartete Validierung:

```powershell
python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_privacy_cleanup_db_preview.py friday/tests/test_privacy_cleanup_db_guard.py friday/tests/test_privacy_cleanup_db_writer.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup DB Final Bundle Gate**.

Ziel:

- gesamten DB-Cleanup-Block von Policy bis CLI-Write zusammenfassend pruefen und dokumentieren.
