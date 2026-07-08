# Privacy Cleanup Writer Plan

## Ziel

Dieses Dokument plant, wie ein spaeterer Privacy Cleanup Writer sicher aufgebaut werden duerfte.

Der Writer waere der erste Baustein, der spaeter echte lokale Cleanup-Aktionen vorbereiten koennte. Deshalb wird hier nur geplant.

Dieser Schritt baut bewusst noch keinen Writer:

- keine Produktlogik,
- keine Datei-Loeschung,
- keine SQLite-Loeschung,
- keine CLI-Anbindung,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Bereits vorhanden:

- Privacy Cleanup Policy,
- Privacy Cleanup Preview Model,
- Privacy Cleanup CLI Read-Only Preview,
- Privacy Cleanup Final Acceptance Gate,
- Privacy Cleanup Write Policy Plan,
- Privacy Cleanup Write Guard Plan,
- Privacy Cleanup Write Guard Model,
- Privacy Cleanup Write Guard Readiness Gate.

Der Guard ist isoliert und side-effect-free. Er prueft, ob ein spaeterer Cleanup vorbereitet werden duerfte.

Ein echter Writer ist weiterhin nicht implementiert.

## Writer-Grundsatz

Ein spaeterer Writer darf niemals direkt aus einer Nutzerentscheidung heraus arbeiten.

Er muss immer diese Reihenfolge erzwingen:

1. Read-only Cleanup Preview anzeigen.
2. Guard mit allen relevanten Daten aufrufen.
3. Guard muss `allowed=True` liefern.
4. Safety Smoke muss vor Write erfolgreich sein.
5. Harte bereichsspezifische Token-Pruefung muss bestanden sein.
6. Optionales Sicherheitsbackup muss bereit sein, falls Daten geloescht werden.
7. Erst dann darf ein eng begrenzter lokaler Write ausgefuehrt werden.

## Geplante Writer-Eingaben

| Feld | Zweck |
|---|---|
| `guard_result` | Ergebnis von `check_privacy_cleanup_write_allowed` |
| `cleanup_area` | Cleanup-Bereich, z. B. `exports`, `backups`, `restore_work`, `review_history`, `contact_context` |
| `target_path` | Konkret geplanter lokaler Zielpfad, falls Datei-Cleanup |
| `dry_run` | Wenn `True`, nie schreiben oder loeschen |
| `backup_ready` | Muss bei riskanten Aktionen `True` sein |
| `rollback_available` | Muss bei DB-/Kontakt-Aktionen `True` sein |
| `operation_id` | Lokale Nachvollziehbarkeit ohne sensible Inhalte |

## Geplante Writer-Ausgabe

Der spaetere Writer sollte eine reine Ergebnisstruktur liefern:

| Feld | Bedeutung |
|---|---|
| `performed` | `True`, wenn eine Aktion tatsaechlich ausgefuehrt wurde |
| `cleanup_area` | Bereich der Aktion |
| `target_path` | Betroffener lokaler Pfad oder leer |
| `deleted_count` | Anzahl entfernter Elemente, falls zutreffend |
| `skipped_count` | Anzahl uebersprungener Elemente |
| `dry_run` | Ob nur simuliert wurde |
| `backup_used` | Ob ein Sicherheitsbackup genutzt wurde |
| `rollback_available` | Ob Rollback vorbereitet war |
| `blocked_reasons` | Gruende, falls keine Aktion ausgefuehrt wurde |
| `message` | Kurze Nutzer-/Logmeldung |
| `external_action_used` | Muss immer `False` sein |

## Guard-Pflicht

Ein spaeterer Writer muss blockieren, wenn:

- kein Guard-Ergebnis uebergeben wurde,
- `guard_result.allowed` nicht `True` ist,
- `guard_result.write_performed` nicht `False` ist,
- `guard_result.external_action_used` nicht `False` ist,
- `guard_result.cleanup_area` nicht zum Writer-Request passt,
- `guard_result.target_path` nicht zum Writer-Request passt,
- `guard_result.required_token` leer ist,
- Safety Smoke nicht aktuell erfolgreich ist.

## Backup- und Rollback-Regeln

| Cleanup-Art | Backup-Pflicht | Rollback-Pflicht | Hinweis |
|---|---|---|---|
| Export-Cleanup | nein, falls nur alte Exportordner | nein | Nur innerhalb erlaubter Exportordner |
| Backup-Cleanup | ja, Schutz fuer neuestes Backup | nein | Neueste Sicherung nie loeschen |
| Restore-Work-Cleanup | nein | nein | Nur temporaere Restore-Arbeitsordner |
| Review-History-Cleanup | ja | ja | Keine pending Vorschlaege loeschen |
| Kontakt-Kontext-Cleanup | ja | ja | Nur explizit ausgewaehlter Kontakt |

## Geplante erlaubte Writer-Scopes

| Bereich | Erlaubter Scope |
|---|---|
| `exports` | `local_data/exports/` |
| `backups` | `local_data/backups/`, aber nicht neueste Sicherung |
| `restore_work` | `local_data/restore_work/` oder spaeter definierter Restore-Arbeitsordner |
| `review_history` | Nur lokale Review-Historie nach eigenem DB-Gate |
| `contact_context` | Nur lokaler Kontakt-Kontext nach eigenem DB-Gate |

## Weiterhin gesperrte Bereiche

Ein spaeterer Writer darf nicht schreiben oder loeschen in:

- Projektquellcode,
- Tests,
- `friday/docs` ausser explizit erlaubten Cleanup-Artefakten,
- `requirements.txt`,
- Start-/Setup-Skripten,
- aktiver SQLite-Hauptdatenbank ohne eigenes Gate,
- Obsidian Vault,
- `.env`-Dateien,
- Secrets,
- Tokens,
- beliebigen absoluten Pfaden ausserhalb erlaubter Scopes,
- externen Diensten.

## Transaktionsregeln fuer spaetere DB-Cleanup-Aktionen

Falls spaeter Review-Historie oder Kontakt-Kontexte geloescht werden duerfen:

- nur mit SQLite-Transaktion,
- vorab Backup-Pflicht,
- kein Schemawechsel,
- kein Loeschen aktiver pending Vorschlaege,
- Rollback bei Fehler,
- Ergebnisbericht ohne sensible Inhalte.

## Datei-Cleanup-Regeln

Falls spaeter lokale Dateien geloescht werden duerfen:

- nur innerhalb erlaubter Scopes,
- keine Symlink-Flucht,
- keine Root-/Projektwurzel-Loeschung,
- keine `.env`-/Secret-/Token-Dateien,
- keine Obsidian-Vault-Dateien,
- keine aktive Datenbank,
- keine neueste Backup-Sicherung,
- Ergebnisbericht mit Anzahl, nicht mit sensiblen Inhalten.

## Empfohlene spaetere Tests

Wenn der Writer implementiert wird:

- blockiert ohne Guard,
- blockiert bei `guard_result.allowed=False`,
- blockiert bei Guard-Area-Mismatch,
- blockiert bei Guard-Target-Mismatch,
- blockiert bei fehlendem Backup fuer riskante Bereiche,
- blockiert bei fehlendem Rollback fuer DB-Cleanup,
- dry-run loescht nichts,
- Datei-Cleanup bleibt innerhalb erlaubtem `tmp_path`,
- neuestes Backup wird nicht geloescht,
- DB-Cleanup nutzt Transaktion und Rollback,
- externe Aktionen bleiben `False`.

## Nicht-Ziele dieses Schritts

- Kein Writer-Code.
- Keine Tests.
- Keine CLI-Anbindung.
- Keine Dateioperationen.
- Keine SQLite-Operationen.
- Keine Loeschung.
- Keine externen Aktionen.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine echte Cleanup-Ausfuehrung.
- Keine externen Aktionen.
- Keine Datenbankschema-Aenderung.
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

Naechster sinnvoller Build Step: **Privacy Cleanup Writer Model**.

Ziel:

- isoliertes Writer-Modell mit `dry_run` und Guard-Pflicht implementieren,
- zunaechst ohne CLI-Anbindung,
- nur mit `tmp_path` Tests,
- keine produktive Datei- oder Datenbankloeschung.
