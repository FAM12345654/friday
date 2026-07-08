# Privacy Cleanup DB CLI Write Implementation Plan

## Ziel

Dieses Dokument beschreibt den konkreten Implementierungsplan fuer eine spaetere SQLite Privacy Cleanup DB Write-Anbindung im Privacy Dashboard.

Der Schritt bleibt bewusst reine Planung:

- keine Produktlogik,
- keine Tests,
- keine neue CLI-Write-Funktion,
- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Geplante Menue-Aenderung

Aktueller Stand:

```text
9. DB-Cleanup Preview anzeigen
10. Zurück zum Hauptmenü
```

Geplanter spaeterer Stand:

```text
9. DB-Cleanup Preview anzeigen
10. DB-Cleanup ausführen
11. Zurück zum Hauptmenü
```

Die Preview bleibt separat und read-only.

## Geplante Interface-Methode

Neue spaetere Methode:

```python
def _run_privacy_cleanup_db_from_input(self) -> None:
    ...
```

Diese Methode darf nur:

1. Bereich abfragen.
2. Frische DB-Preview erzeugen.
3. Preview anzeigen.
4. Backup-Nachweis pruefen.
5. Safety Smoke ausfuehren.
6. Harten Token abfragen.
7. Guard ausfuehren.
8. Writer nur bei Guard-Freigabe ausfuehren.
9. Sichere Ergebniszaehler anzeigen.

## Geplante Eingaben

### Bereichsauswahl

```text
DB-Cleanup ausführen
1. Review-History
2. Einzelner Kontakt-Kontext
Enter/z. Zurück
```

### Kontakt-Kontext

Nur fuer Bereich `2`:

```text
Kontakt-ID eingeben:
```

Leere Eingabe bricht ab.

### Token

```text
Zum Ausführen tippe exakt:
REVIEW AUFRAEUMEN
Token:
```

Oder:

```text
Zum Ausführen tippe exakt:
KONTAKT LÖSCHEN
Token:
```

## Backup-Regel

Eine spaetere Implementierung darf nur ausfuehren, wenn ein lokales Backup vorhanden ist.

Geplante einfache erste Regel:

- pruefe `local_data/backups/`,
- mindestens ein Backup-Ordner muss vorhanden sein,
- sonst blockieren mit:

```text
DB-Cleanup wurde blockiert: Backup fehlt.
```

Kein automatisches Backup in diesem Flow.

## Safety-Smoke-Regel

Vor dem Writer muss Safety Smoke laufen.

Bei `PASS`:

```text
Safety Smoke: PASS
```

Bei `FAIL`:

```text
Safety Smoke: FAIL
DB-Cleanup wurde blockiert: Safety Smoke fehlgeschlagen.
```

## Guard-/Writer-Ablauf

Geplanter Ablauf:

1. `build_privacy_cleanup_db_preview(...)`
2. `_print_privacy_cleanup_db_preview(...)`
3. `_latest_backup_path(...)` oder eigener Backup-Check
4. `run_safety_smoke()`
5. Token abfragen
6. `check_privacy_cleanup_db_write_allowed(...)`
7. bei Blockierung Gruende anzeigen
8. `apply_privacy_cleanup_db_write(...)`
9. Ergebniszaehler anzeigen

## Geplante Erfolgsmeldung

```text
DB-Cleanup wurde lokal ausgefuehrt.
Gelöschte Datensätze:
- message_suggestions: 1
- task_suggestions: 1
```

Oder:

```text
DB-Cleanup wurde lokal ausgefuehrt.
Gelöschte Datensätze:
- contact_contexts: 1
```

## Geplante Blockierungs-Meldungen

| Situation | Meldung |
|---|---|
| Abbruch | `DB-Cleanup wurde abgebrochen.` |
| Ungueltige Auswahl | `Ungültige Auswahl. Bitte erneut versuchen.` |
| Fehlendes Backup | `DB-Cleanup wurde blockiert: Backup fehlt.` |
| Safety Smoke FAIL | `DB-Cleanup wurde blockiert: Safety Smoke fehlgeschlagen.` |
| Guard blockiert | `DB-Cleanup wurde nicht freigegeben.` |
| Writer blockiert | `DB-Cleanup wurde nicht ausgefuehrt.` |

## Geplante Tests

Neue oder erweiterte Tests in:

- `friday/tests/test_interface_main_menu_e2e.py`

Pflichtfaelle:

- DB-Cleanup-Write-Menuepunkt erscheint separat.
- Enter/z bricht ab.
- falscher Token blockiert.
- `ja` blockiert.
- `JA` blockiert.
- fehlendes Backup blockiert.
- Safety-Smoke-Fehler blockiert.
- Review-History exakter Token loescht nur sichere Kandidaten.
- Kontakt-Kontext exakter Token loescht nur ausgewaehlten Kontakt.
- pending Vorschlaege bleiben erhalten.
- Aufgaben bleiben erhalten.
- Rueckkehr ins Privacy Dashboard bleibt stabil.

## Nicht-Ziele dieses Schritts

- Keine Implementierung.
- Keine Tests.
- Keine neue Menueoption.
- Keine SQLite-Loeschung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine SQLite-Schreiboperation.
- Keine SQLite-Loeschung.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Write Implementation**.

Ziel:

- guarded DB-Cleanup-Write im Privacy Dashboard implementieren,
- nur mit Preview, Backup-Nachweis, Safety Smoke, hartem Token, Guard und Writer,
- Tests fuer Blockierungs- und Erfolgspfade ergaenzen.
