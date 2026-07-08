# Privacy Cleanup Runtime Readiness Summary

## Ziel

Dieses Dokument fasst den aktuellen lokalen Runtime-Stand fuer den gesamten Privacy-Cleanup-Bereich zusammen.

Es verbindet:

- Privacy Dashboard,
- Privacy Data Management Inventory,
- read-only Datei-Cleanup Preview,
- guarded Datei-Cleanup Write,
- read-only DB-Cleanup Preview,
- guarded DB-Cleanup Write,
- Safety Smoke,
- harte Approval-Tokens,
- Nutzer-Dokumentation.

## Runtime-Status

| Bereich | Status | Runtime-Verhalten |
|---|---|---|
| Privacy Dashboard | stabil | Lokales CLI-Untermenue fuer Privacy-Status, Datenbereiche, Scanner und Cleanup-Pfade |
| Privacy Data Management Inventory | stabil | Read-only Anzeige lokaler Datenbereiche ohne Schreibzugriff |
| Datei-Cleanup Preview | stabil | Zeigt lokale Datei-Cleanup-Kandidaten read-only an |
| Datei-Cleanup Write | stabil gegatet | Kann nur erlaubte lokale Datei-Scopes nach Safety Smoke, Guard und hartem Token bearbeiten |
| DB-Cleanup Preview | stabil | Zeigt SQLite-Cleanup-Kandidaten read-only an |
| DB-Cleanup Write | stabil gegatet | Kann nur erlaubte SQLite-Bereiche nach Backup, Safety Smoke, Guard und hartem Token bearbeiten |
| Safety Scanner / Smoke | stabil | Prueft Safety-Flags, verbotene Imports, Netzwerk-Muster, input/print und Approval-Tokens |
| Nutzer-Doku | stabil | README erklaert Preview, Ausfuehrung, Tokens und Safety-Grenzen |

## Aktueller CLI-Stand

Das Hauptmenue enthaelt den Privacy-Bereich:

```text
12. Privacy Dashboard
```

Das Privacy Dashboard enthaelt aktuell:

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

## Read-only Datei-Cleanup Preview

Menuepunkt `7. Privacy Cleanup Preview anzeigen` bleibt read-only:

- zeigt moegliche Datei-Cleanup-Bereiche,
- zeigt erforderliche Tokens,
- zeigt blockierte Bereiche,
- loescht nichts,
- fragt keinen Token ab,
- schreibt nichts.

## Guarded Datei-Cleanup Write

Menuepunkt `8. Privacy Cleanup ausfuehren` kann nur erlaubte lokale Datei-Cleanup-Bereiche ausfuehren:

| Bereich | Token |
|---|---|
| Exporte | `EXPORT AUFRAEUMEN` |
| Backups | `BACKUP AUFRAEUMEN` |
| Restore-Kopien | `RESTORE AUFRAEUMEN` |

Der Ablauf ist:

1. Warnung anzeigen.
2. Datei-Cleanup-Bereich auswaehlen.
3. Konkreten lokalen Zielpfad eingeben.
4. Preview anzeigen.
5. Safety Smoke pruefen.
6. Exakten harten Token abfragen.
7. Guard pruefen.
8. Writer ausfuehren.
9. Ergebnis anzeigen.

## Read-only DB-Cleanup Preview

Menuepunkt `9. DB-Cleanup Preview anzeigen` bleibt read-only:

- zeigt SQLite-Cleanup-Kandidaten,
- zeigt Bereich, Tabelle, Filter und Kandidatenanzahl,
- zeigt erforderliche Tokens,
- loescht nichts,
- schreibt nichts,
- fuehrt keinen Guard und keinen Writer aus.

## Guarded DB-Cleanup Write

Menuepunkt `10. DB-Cleanup ausführen` kann nur erlaubte lokale SQLite-Cleanup-Bereiche ausfuehren:

| Bereich | Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

Der Ablauf ist:

1. Warnung anzeigen.
2. DB-Cleanup-Bereich auswaehlen.
3. Konkrete lokale Zielangabe eingeben.
4. Frische DB-Cleanup Preview erstellen.
5. Lokalen Backup-Nachweis unter `local_data/backups/` pruefen.
6. Safety Smoke pruefen.
7. Exakten harten Token abfragen.
8. DB-Cleanup Guard pruefen.
9. DB-Cleanup Writer transaktional ausfuehren.
10. Ergebnis anzeigen.

## Lokal stabil funktionierende Bereiche

- Privacy Dashboard kann aus dem Hauptmenue geoeffnet werden.
- Safety-Flags koennen lokal angezeigt werden.
- Lokale Datenbereiche koennen read-only angezeigt werden.
- Export-/Schreibstatus kann read-only angezeigt werden.
- Scanner-Status kann read-only angezeigt werden.
- Externe Aktionen werden als deaktiviert angezeigt.
- Privacy Data Management Inventory zeigt lokale Datenbereiche ohne Schreibzugriff.
- Datei-Cleanup Preview zeigt Datei-Kandidaten ohne Loeschung oder Token-Abfrage.
- Datei-Cleanup Write blockiert falsche Tokens und nicht erlaubte Pfade.
- Datei-Cleanup Write fuehrt erlaubten lokalen Datei-Cleanup nur nach Safety Smoke, Guard und hartem Token aus.
- DB-Cleanup Preview zeigt SQLite-Kandidaten ohne Loeschung oder Token-Abfrage.
- DB-Cleanup Write blockiert ohne Backup-Nachweis.
- DB-Cleanup Write blockiert bei Safety-Smoke-Fehler.
- DB-Cleanup Write blockiert falsche Tokens.
- DB-Cleanup Write kann nur Review-History und einzelne Kontakt-Kontexte bearbeiten.
- Rueckkehr ins Hauptmenue bleibt stabil.

## Bewusst nicht freigegebene Bereiche

- Kein Obsidian-Cleanup.
- Keine externen Provider oder Netzwerkaktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine SQLite-Schema-Aenderung.
- Kein Loeschen von Pending Vorschlaegen ueber DB-Cleanup.
- Kein Loeschen von Aufgaben ueber DB-Cleanup.
- Kein Loeschen von Nachrichten ueber DB-Cleanup.
- Kein Loeschen von Kalenderdaten ueber DB-Cleanup.
- Kein Datei-Cleanup ohne konkreten Zielpfad.
- Kein DB-Cleanup ohne lokalen Backup-Nachweis.
- Kein Cleanup ohne Safety Smoke.
- Kein Cleanup ohne Guard-Freigabe.
- Kein Cleanup mit `ja` oder `JA`.

## Teststatus

- Vollstaendige Testsuite: `763 passed`
- Compilecheck: erfolgreich
- Safety Smoke: `PASS`
- Diff-/Whitespace-Check: sauber

Details:

- `PRIVACY_CLEANUP_RUNTIME_SMOKE_GUIDE.md`
- `PRIVACY_CLEANUP_DB_FINAL_BUNDLE_GATE.md`
- `PRIVACY_CLEANUP_DB_DOCUMENTATION_FINALIZATION.md`
- `cli_documentation_index_12l.md`

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Datei-Cleanup ist nur lokal, guarded und tokenpflichtig.
- DB-Cleanup ist nur lokal, backup-geschuetzt, guarded und tokenpflichtig.
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

## Verweise

- `README_USER.md`
- `PRIVACY_CLEANUP_RUNTIME_SMOKE_GUIDE.md`
- `PRIVACY_CLEANUP_FINAL_BUNDLE_GATE.md`
- `PRIVACY_CLEANUP_DOCUMENTATION_FINALIZATION.md`
- `PRIVACY_CLEANUP_FINAL_ACCEPTANCE_UPDATE.md`
- `PRIVACY_CLEANUP_DB_FINAL_BUNDLE_GATE.md`
- `PRIVACY_CLEANUP_DB_DOCUMENTATION_FINALIZATION.md`
- `PRIVACY_CLEANUP_DB_USER_GUIDE_UPDATE.md`
- `cli_documentation_index_12l.md`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup Full Runtime Acceptance Gate**.

Ziel:

- Datei-Cleanup und DB-Cleanup gemeinsam final als Runtime-Block abnehmen.
- README, Runtime Summary, Smoke Guide und Doku-Index synchron pruefen.
- Keine Produktlogik aendern.
- Keine Tests erweitern.
