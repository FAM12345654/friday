# Privacy Cleanup Write Policy Plan

## Ziel

Dieses Dokument plant, wie ein spaeterer echter Privacy-Cleanup-Write sicher aussehen duerfte.

Dieser Schritt ist bewusst nur Planung:

- keine Produktlogik,
- keine Datei-Loeschung,
- keine SQLite-Loeschung,
- kein Writer,
- keine CLI-Token-Abfrage,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Der aktuelle Privacy-Cleanup-Stand ist read-only:

- Privacy Dashboard zeigt lokale Privacy-Informationen.
- Privacy Data Management Inventory zeigt lokale Datenbereiche.
- Privacy Cleanup Preview zeigt moegliche Cleanup-Kandidaten.
- Privacy Cleanup Final Acceptance Gate hat den read-only Stand abgeschlossen.

Ein echter Cleanup-Write ist noch nicht freigegeben.

## Grundregel fuer spaetere Cleanup-Writes

Ein spaeterer Cleanup-Write darf nur ausgefuehrt werden, wenn alle Bedingungen erfuellt sind:

1. Der Bereich ist ausdruecklich fuer Cleanup freigegeben.
2. Eine read-only Preview wurde vorher angezeigt.
3. Ein Guard-Modell bestaetigt, dass der Cleanup sicher ist.
4. Ein harter bereichsspezifischer Token wurde exakt eingegeben.
5. Der Write bleibt lokal.
6. Safety Smoke ist gruen.
7. Es gibt keine externen Aktionen.

## Geplante harte Tokens

| Bereich | Geplanter Token | Zweck |
|---|---|---|
| Export-Cleanup | `EXPORT AUFRAEUMEN` | Lokale Exportdateien entfernen, falls spaeter erlaubt |
| Backup-Cleanup | `BACKUP AUFRAEUMEN` | Lokale alte Backups entfernen, falls spaeter erlaubt |
| Restore-Cleanup | `RESTORE AUFRAEUMEN` | Lokale Restore-Arbeitsdateien entfernen, falls spaeter erlaubt |
| Review-History-Cleanup | `REVIEW AUFRAEUMEN` | Lokale Review-Historie bereinigen, falls spaeter erlaubt |
| Kontakt-Loeschung | `KONTAKT LÖSCHEN` | Lokalen Kontakt-Kontext hart entfernen, falls spaeter erlaubt |

Token-Regeln:

- Tokens muessen exakt passen.
- `ja` ist nie ausreichend.
- `JA` ist nie ausreichend fuer Privacy Cleanup.
- Leere Eingabe bricht ab.
- Whitespace darf nicht stillschweigend riskante Eingaben akzeptieren, ausser ein spaeterer Guard dokumentiert exakt dieses Verhalten.

## Erlaubte Bereiche fuer spaetere Planung

| Bereich | Spaeterer Cleanup denkbar? | Bedingung |
|---|---|---|
| Lokale Exportdateien | ja | Nur innerhalb erlaubter Export-Unterordner |
| Lokale Backup-Dateien | ja | Nur alte lokale Backups, nie das neueste Sicherheitsbackup |
| Restore-Arbeitsdateien | ja | Nur temporaere lokale Restore-Pruefdateien |
| Review-Historie | eventuell | Nur lokale Historie, keine aktiven pending Vorschlaege |
| Kontakt-Kontexte | eventuell | Nur nach explizitem Kontakt-Loesch-Token und Vorschau |

## Gesperrte Bereiche

Diese Bereiche duerfen durch einen spaeteren Privacy-Cleanup-Write nicht geloescht werden:

- Projektquellcode,
- Tests,
- Dokumentation ausser explizit erlaubten Cleanup-Artefakten,
- `requirements.txt`,
- Start-/Setup-Skripte,
- Obsidian Vault,
- `.env`-Dateien,
- Secrets,
- API-Schluessel,
- unbekannte Pfade ausserhalb des Projektordners,
- beliebige absolute Pfade,
- aktive SQLite-Hauptdatenbank ohne eigenes spaeteres Gate,
- neueste Backup-Sicherung,
- Dateien ausserhalb ausdruecklich erlaubter Unterordner.

## Geplante Guard-Regeln

Ein spaeteres Guard-Modell sollte mindestens pruefen:

- Bereich ist bekannt.
- Zielpfad liegt innerhalb eines erlaubten lokalen Unterordners.
- Ziel ist nicht leer, nicht Root, nicht Projektwurzel.
- Ziel enthaelt keine `.env`-, Secret- oder Credential-Dateien.
- Ziel enthaelt keinen Obsidian-Vault-Pfad.
- Ziel enthaelt keine aktive SQLite-Hauptdatenbank.
- Preview wurde erzeugt.
- Harte Token-Regel ist fuer den Bereich definiert.
- Safety Smoke kann vor der Aktion ausgefuehrt werden.
- Operation ist lokal und hat keine Netzwerkabhaengigkeit.

## Spaetere technische Reihenfolge

Empfohlene Folgeschritte:

1. Privacy Cleanup Write Guard Plan.
2. Privacy Cleanup Write Guard Model.
3. Privacy Cleanup Write Guard Readiness Gate.
4. Privacy Cleanup Writer Plan.
5. Privacy Cleanup Writer Model mit `tmp_path` Tests.
6. Privacy Cleanup CLI Write Plan.
7. Privacy Cleanup CLI Write Implementation mit harter Token-Abfrage.
8. Privacy Cleanup Write Final Acceptance Gate.

## Nicht-Ziele dieses Schritts

- Kein Cleanup Writer.
- Keine CLI-Anbindung.
- Keine Dateioperationen.
- Keine SQLite-Operationen.
- Kein Loeschen.
- Kein Import/Export/Restore.
- Keine externen Integrationen.
- Keine neuen Tests.

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

Naechster sinnvoller Build Step: **Privacy Cleanup Write Guard Plan**.

Ziel:

- planen, welches isolierte Guard-Modell spaeter vor jedem Cleanup-Write prueft,
- erlaubte und gesperrte Pfade konkretisieren,
- noch keine Implementierung,
- keine Datei- oder Datenbankloeschung.
