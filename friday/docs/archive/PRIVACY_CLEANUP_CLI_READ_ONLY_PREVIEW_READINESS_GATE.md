# Privacy Cleanup CLI Read-Only Preview Readiness Gate

## Ziel

Dieses Gate prueft die read-only CLI-Anbindung der Privacy Cleanup Preview im Privacy Dashboard.

Der gepruefte Stand:

- Privacy Dashboard zeigt die Cleanup Preview als Anzeige.
- Rueckkehr erfolgt ueber `8`.
- Die Preview bleibt read-only.
- Keine Cleanup-Ausfuehrung wurde freigeschaltet.

## Gepruefte Dateien

| Datei | Ergebnis |
|---|---|
| `friday/app/menu.py` | Privacy Dashboard Menue enthaelt Cleanup Preview und Rueckkehr |
| `friday/app/interface.py` | Cleanup Preview wird nur angezeigt |
| `friday/app/privacy_cleanup_preview.py` | Preview-Modell bleibt isoliert und read-only |
| `friday/tests/test_menu.py` | Menueoptionen abgesichert |
| `friday/tests/test_interface_main_menu_e2e.py` | CLI-Anzeige und Rueckkehr abgesichert |
| `friday/tests/test_privacy_cleanup_preview.py` | Preview-Modell abgesichert |
| `friday/docs/PRIVACY_CLEANUP_CLI_READ_ONLY_PREVIEW_IMPLEMENTATION.md` | Umsetzung dokumentiert |

## Readiness-Ergebnis

- Menuepunkt `7` zeigt die Privacy Cleanup Preview.
- Menuepunkt `8` kehrt zum Hauptmenue zurueck.
- Die Anzeige enthaelt erlaubte und blockierte Preview-Bereiche.
- Harte spaetere Tokens werden nur angezeigt.
- Es wird kein Token abgefragt.
- Es werden keine Dateien gelesen.
- Es werden keine Dateien geschrieben.
- Es werden keine Dateien geloescht.
- Es wird keine SQLite-Datenbank geoeffnet.
- Es werden keine externen Aktionen ausgefuehrt.

## Weiterhin blockiert

| Bereich | Status |
|---|---|
| Cleanup ausfuehren | blockiert |
| Dateisystem bereinigen | blockiert |
| SQLite-Daten bereinigen | blockiert |
| Exportordner loeschen | blockiert |
| Backupordner loeschen | blockiert |
| Restore-Kopien loeschen | blockiert |
| Review-Vorschlaege loeschen | blockiert |
| Kontakt-Kontexte ueber Privacy Cleanup loeschen | blockiert |
| Obsidian Vault bereinigen | blockiert |
| In-Place-Restore | blockiert |

## Safety-Bewertung

- Keine Cleanup-Ausfuehrung.
- Keine Token-Abfrage.
- Kein Dateizugriff.
- Kein SQLite-Zugriff.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Loeschpfade.
- Keine neuen Exportpfade.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Teststatus

Empfohlene Pruefkommandos:

```powershell
python -m pytest friday/tests/test_menu.py friday/tests/test_privacy_cleanup_preview.py friday/tests/test_interface_main_menu_e2e.py
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Cleanup Runtime Readiness Summary`

Ziel: Den aktuellen Privacy-/Cleanup-Stand zusammenfassen: Dashboard, Inventory, Policy, Preview-Modell und read-only CLI-Anzeige. Noch keine echte Cleanup-Ausfuehrung.
