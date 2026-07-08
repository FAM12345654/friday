# Privacy Cleanup Write Guard Plan

## Ziel

Dieses Dokument plant ein spaeteres isoliertes Guard-Modell fuer echte Privacy-Cleanup-Writes.

Der Guard soll vor jeder spaeteren Cleanup-Ausfuehrung entscheiden, ob eine Aktion sicher blockiert oder vorbereitet werden darf.

Dieser Schritt ist bewusst nur Planung:

- keine Produktlogik,
- kein Guard-Code,
- kein Writer,
- keine Datei-Loeschung,
- keine SQLite-Loeschung,
- keine CLI-Anbindung,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Der aktuelle Privacy-Cleanup-Stand ist read-only:

- Privacy Cleanup Policy ist dokumentiert.
- Privacy Cleanup Preview Model existiert ohne Ausfuehrung.
- Privacy Cleanup CLI Preview zeigt nur Informationen.
- Privacy Cleanup Final Acceptance Gate hat den read-only Block abgeschlossen.
- Privacy Cleanup Write Policy Plan definiert spaetere Tokens, Sperrbereiche und Grundregeln.

Ein echter Cleanup-Write ist weiterhin nicht freigegeben.

## Geplanter Guard-Zweck

Das spaetere Guard-Modell soll:

- bekannte Cleanup-Bereiche erkennen,
- unbekannte Bereiche blockieren,
- Zielpfade gegen erlaubte Scopes pruefen,
- gefaehrliche Ziele blockieren,
- harte Tokens validieren,
- Preview-Pflicht pruefen,
- Safety-Smoke-Pflicht dokumentieren,
- externe Aktionen ausschliessen,
- ohne Seiteneffekte arbeiten.

## Geplante Guard-Eingaben

Ein spaeterer Guard-Aufruf sollte nur explizite, bereits vorbereitete Daten erhalten:

| Feld | Zweck |
|---|---|
| `cleanup_area` | Bereich, z. B. `exports`, `backups`, `restore_work`, `review_history`, `contact_context` |
| `target_path` | Geplanter lokaler Zielpfad, falls Datei-Cleanup betroffen ist |
| `project_root` | Erlaubte Projektwurzel |
| `allowed_base_path` | Enger erlaubter Unterordner fuer den konkreten Bereich |
| `preview_was_shown` | Muss `True` sein |
| `approval_token` | Eingabe fuer harte Token-Pruefung |
| `expected_token` | Bereichsspezifischer erwarteter Token |
| `safety_smoke_passed` | Muss vor Write `True` sein |
| `external_actions_enabled` | Muss `False` sein |

## Geplante Guard-Ausgabe

Der Guard sollte eine reine Datenstruktur zurueckgeben:

| Feld | Bedeutung |
|---|---|
| `allowed` | `True`, wenn der Cleanup technisch vorbereitet werden darf |
| `cleanup_area` | Gepruefter Bereich |
| `target_path` | Gepruefter Zielpfad oder leer |
| `reason` | Kurze Ergebnisbeschreibung |
| `block_reasons` | Liste konkreter Blockgruende |
| `preview_required` | Dokumentiert Preview-Pflicht |
| `token_required` | Dokumentiert Token-Pflicht |
| `external_action_used` | Muss immer `False` sein |
| `write_performed` | Muss im Guard immer `False` sein |

## Geplante erlaubte Bereiche

| Bereich | Erlaubter Scope | Token |
|---|---|---|
| `exports` | Nur lokale Export-Unterordner | `EXPORT AUFRAEUMEN` |
| `backups` | Nur lokale Backup-Unterordner, nie neueste Sicherung | `BACKUP AUFRAEUMEN` |
| `restore_work` | Nur lokale Restore-Arbeitsordner | `RESTORE AUFRAEUMEN` |
| `review_history` | Nur lokale Review-Historie, keine pending Vorschlaege | `REVIEW AUFRAEUMEN` |
| `contact_context` | Nur explizit ausgewaehlter Kontakt-Kontext | `KONTAKT LÖSCHEN` |

## Geplante Block-Regeln

Der spaetere Guard muss blockieren, wenn:

- `cleanup_area` unbekannt ist,
- `preview_was_shown` nicht `True` ist,
- `approval_token` nicht exakt dem erwarteten Token entspricht,
- `approval_token` leer ist,
- `approval_token` nur `ja` oder `JA` ist,
- `safety_smoke_passed` nicht `True` ist,
- `external_actions_enabled` nicht `False` ist,
- `target_path` ausserhalb des erlaubten Scopes liegt,
- `target_path` die Projektwurzel ist,
- `target_path` ein Root-Laufwerk ist,
- `target_path` leer ist, obwohl ein Pfad benoetigt wird,
- Zielpfade `.env`, Secrets oder Credentials betreffen,
- Zielpfade den Obsidian Vault betreffen,
- Zielpfade die aktive SQLite-Hauptdatenbank betreffen,
- Zielpfade Quellcode, Tests, Setup-Skripte oder Anforderungen betreffen.

## Side-Effect-Free-Regeln

Das spaetere Guard-Modell darf:

- keine Dateien loeschen,
- keine Dateien schreiben,
- keine SQLite-Verbindung oeffnen,
- keine Netzwerkverbindung oeffnen,
- keine externen Provider importieren,
- kein `input()` verwenden,
- kein `print()` verwenden,
- keinen globalen Zustand veraendern.

## Empfohlene spaetere Testfaelle

Wenn der Guard implementiert wird, sollten mindestens diese Tests entstehen:

- bekannter Bereich mit korrektem Token wird vorbereitet,
- unbekannter Bereich wird blockiert,
- fehlende Preview wird blockiert,
- falscher Token wird blockiert,
- `ja` wird blockiert,
- `JA` wird blockiert,
- leerer Token wird blockiert,
- fehlender Safety Smoke wird blockiert,
- externe Aktionen aktiviert wird blockiert,
- Pfad ausserhalb des erlaubten Scopes wird blockiert,
- Projektwurzel wird blockiert,
- `.env`-Datei wird blockiert,
- Obsidian-Vault-Pfad wird blockiert,
- aktive SQLite-Hauptdatenbank wird blockiert,
- Guard setzt `write_performed` immer auf `False`.

## Nicht-Ziele dieses Schritts

- Keine Guard-Implementierung.
- Keine Tests.
- Kein Cleanup Writer.
- Keine CLI-Anbindung.
- Keine Dateioperation.
- Keine SQLite-Operation.
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

Naechster sinnvoller Build Step: **Privacy Cleanup Write Guard Model**.

Ziel:

- isoliertes side-effect-free Guard-Modell implementieren,
- harte Token-Regeln und Scope-Blockaden testen,
- keine Datei- oder Datenbankloeschung,
- keine CLI-Anbindung.
