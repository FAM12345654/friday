# Privacy Cleanup Runtime Smoke Guide

## Ziel

Dieser Guide beschreibt die empfohlenen lokalen Smoke Checks nach Aenderungen am Privacy-Cleanup-Flow.

Er deckt ab:

- Privacy Dashboard Menue,
- read-only Cleanup Preview,
- Privacy Cleanup Write Guard,
- Privacy Cleanup Writer,
- guarded CLI-Cleanup,
- read-only DB-Cleanup Preview,
- guarded DB-Cleanup Write,
- Full Regression,
- Compilecheck,
- Safety Smoke,
- Diff-/Whitespace-Check.

## Wann ausfuehren?

Fuehre diesen Guide aus, wenn sich einer dieser Bereiche aendert:

- `friday/app/menu.py`
- `friday/app/interface.py`
- `friday/app/privacy_cleanup_preview.py`
- `friday/app/privacy_cleanup_write_guard.py`
- `friday/app/privacy_cleanup_writer.py`
- `friday/app/privacy_cleanup_db_preview.py`
- `friday/app/privacy_cleanup_db_guard.py`
- `friday/app/privacy_cleanup_db_writer.py`
- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_privacy_cleanup_write_guard.py`
- `friday/tests/test_privacy_cleanup_writer.py`
- `friday/tests/test_privacy_cleanup_db_preview.py`
- `friday/tests/test_privacy_cleanup_db_guard.py`
- `friday/tests/test_privacy_cleanup_db_writer.py`
- Privacy-Cleanup-Dokumentation unter `friday/docs/`

## Fokus-Smoke

```powershell
python -m pytest friday/tests/test_menu.py friday/tests/test_interface_main_menu_e2e.py friday/tests/test_privacy_cleanup_writer.py friday/tests/test_privacy_cleanup_write_guard.py friday/tests/test_privacy_cleanup_db_preview.py friday/tests/test_privacy_cleanup_db_guard.py friday/tests/test_privacy_cleanup_db_writer.py
```

Erwartung:

```text
151 passed
```

## Full Regression

```powershell
python -m pytest friday/tests
```

Erwartung:

```text
763 passed
```

## Compilecheck

```powershell
python -m compileall friday
```

Erwartung:

```text
erfolgreich
```

## Safety Smoke

```powershell
python scripts/friday_safety_smoke.py
```

Erwartung:

```text
Overall: PASS
```

## Diff-/Whitespace-Check

```powershell
git diff --check
```

Erwartung:

```text
sauber
```

## Manuelle Safety-Checkliste

- Read-only Preview bleibt auf `7. Privacy Cleanup Preview anzeigen`.
- Guarded Datei-Cleanup bleibt auf `8. Privacy Cleanup ausfuehren`.
- DB-Cleanup Preview bleibt auf `9. DB-Cleanup Preview anzeigen`.
- Guarded DB-Cleanup bleibt auf `10. DB-Cleanup ausführen`.
- Rueckkehr bleibt auf `11. Zurueck zum Hauptmenue`.
- Datei-Cleanup braucht konkreten Zielpfad.
- Datei-Cleanup braucht Safety Smoke `PASS`.
- Datei-Cleanup braucht Guard-Freigabe.
- Datei-Cleanup braucht exakten harten Token.
- DB-Cleanup braucht lokalen Backup-Nachweis.
- DB-Cleanup braucht Safety Smoke `PASS`.
- DB-Cleanup braucht Guard-Freigabe.
- DB-Cleanup braucht exakten harten Token.
- `ja` und `JA` reichen fuer Privacy Cleanup nicht aus.
- Kontakt-Kontext-Cleanup ist nur ueber den guarded DB-Cleanup mit `KONTAKT LÖSCHEN` erlaubt.
- Review-History-Cleanup ist nur ueber den guarded DB-Cleanup mit `REVIEW AUFRAEUMEN` erlaubt.
- Pending Vorschlaege, Aufgaben, Nachrichten und Kalenderdaten bleiben fuer DB-Cleanup blockiert.
- Obsidian-Cleanup bleibt blockiert.
- Externe Aktionen bleiben deaktiviert.

## Aktuelle harte Tokens

| Bereich | Token |
|---|---|
| Exporte | `EXPORT AUFRAEUMEN` |
| Backups | `BACKUP AUFRAEUMEN` |
| Restore-Kopien | `RESTORE AUFRAEUMEN` |
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Provider-/Netzwerkaktionen.
- Keine Datenbankschema-Aenderung.
- Datei-Cleanup ist nur lokal und guarded.
- DB-Cleanup ist nur lokal, backup-geschuetzt und guarded.
- Safety-Flags bleiben lokal-only.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup Full Runtime Acceptance Gate**.

Ziel:

- README, Runtime Summary, Smoke Guide und Doku-Index gemeinsam final pruefen,
- keine Produktlogik aendern,
- keine Tests erweitern.
