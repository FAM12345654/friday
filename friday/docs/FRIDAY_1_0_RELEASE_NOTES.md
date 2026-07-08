# Friday 1.0 Release Notes

## Ziel

Friday 1.0 ist der lokale Windows-CLI-Stand des Assistenten Friday.

Friday bleibt local-first:

- Python,
- SQLite,
- lokale CLI,
- keine echten externen Aktionen,
- keine Cloud-AI,
- keine Provider-Logins.

## Start

```powershell
python -m friday.main
```

Alternativ koennen die vorhandenen Windows-Startdateien genutzt werden, z. B. `start_friday.bat` oder `start_friday_stack.bat`.

## Version

- App Name: `Friday`
- Version: `1.0.0`
- Start-Hinweis zeigt: `Friday 1.0.0 – lokaler Assistent gestartet.`

## Lokale Hauptfunktionen

| Bereich | Funktion |
|---|---|
| Aufgaben | Anzeigen, erstellen, bearbeiten, erledigen, archivieren, loeschen |
| Quick Add | Aufgaben in einer Zeile mit Markern wie `!hoch`, `@morgen`, `#taeglich` |
| Wiederholungen | `taeglich`, `woechentlich`, `monatlich`; Folgeaufgabe beim Erledigen |
| Suche/Filter | lokale Suche nach Titel/Notizen und Filter nach Status/Kategorie/Faelligkeit |
| Markdown Export | lokaler Aufgabenexport unter `local_data/exports/` |
| Tagesplanung | read-only lokale Tagesplan-Vorschau |
| Nachrichten | lokale Nachrichtenerkennung und Antwort-/Aufgaben-Vorschlaege |
| Review | lokale Vorschlaege pruefen, bearbeiten, ablehnen, freigeben oder batch-verarbeiten |
| Kontakt-Kontext | lokale Kontakte anzeigen, suchen, bearbeiten, speichern und vergessen, jeweils guarded |
| E-Mail-Entwurf | lokale in-memory Entwurfs-Preview, bearbeiten/verwerfen, kein Versand |
| Obsidian | lokale Notiz-Preview und hart gegateter Write |
| Backup/Restore | lokales Backup, Restore Copy, Rotation, Datenexport/-import, Cleanup |
| Privacy Dashboard | read-only Uebersicht plus getrennte Cleanup-Pfade |
| Local AI | Mock Default, Ollama nur opt-in via localhost und Validator |
| Safety | Scanner Smoke fuer Imports, Netzwerk, Input/Print, Flags und Tokens |

## E-Mail Draft-only

Friday 1.0 kann lokale E-Mail-Entwuerfe anzeigen und in der Session bearbeiten/verwerfen.

Wichtig:

- kein SMTP,
- kein Gmail,
- kein Outlook,
- kein Login,
- keine Secrets,
- kein Netzwerk,
- kein echter Versand,
- keine Persistenz von E-Mail-Entwuerfen.

## Datenhaltung

- Aktive lokale Datenbank: `local_data/friday.db`
- Demo-Datenbank bei Demo-Modus: `local_data/friday_demo.db`
- Demo-Seeds liegen unter `friday/data/`
- E-Mail-Entwuerfe bleiben in-memory in der CLI-Session.

## Safety-Flags

```python
ENABLE_REAL_EMAIL = False
ENABLE_REAL_WHATSAPP = False
ENABLE_REAL_SMS = False
ENABLE_REAL_CALENDAR = False
ENABLE_REAL_WEATHER = False
ENABLE_REAL_MUSIC = False
REQUIRE_USER_APPROVAL = True
USE_SQLITE_STORAGE = True
```

## Harte Tokens

- `SPEICHERN`
- `KONTAKT LÖSCHEN`
- `PERSON VERGESSEN`
- `OBSIDIAN SCHREIBEN`
- `BACKUP ERSTELLEN`
- `RESTORE AUSFUEHREN`
- `DATEN EXPORTIEREN`
- `IMPORT ANWENDEN`
- `EXPORT AUFRAEUMEN`
- `BACKUP AUFRAEUMEN`
- `RESTORE AUFRAEUMEN`
- `REVIEW AUFRAEUMEN`
- `REVIEW EXPORTIEREN`

## Bewusst deaktiviert

| Bereich | Status |
|---|---|
| echte E-Mail senden | deaktiviert |
| WhatsApp senden | deaktiviert |
| SMS senden | deaktiviert |
| echte Kalendertermine erstellen | deaktiviert |
| Wetter-/Musik-Provider | deaktiviert |
| Cloud-AI | deaktiviert |
| OAuth/Login/Secrets | deaktiviert |
| E-Mail-Draft-Persistenz | nicht freigegeben |
| In-Place-Restore | nicht freigegeben |
| Git Push/Remote/Tagging | nicht freigegeben |

## Validierungsstand

| Check | Ergebnis |
|---|---|
| Full Regression | `1081 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

Die vier Skips betreffen bekannte Windows-Symlink-Rechte und blockieren Friday 1.0 lokal nicht.

## Ergebnis

Friday 1.0 ist lokal fertiggestellt. Jede weitere Arbeit ist Post-1.0 und braucht eigene Gates, insbesondere fuer echte externe Aktionen.
