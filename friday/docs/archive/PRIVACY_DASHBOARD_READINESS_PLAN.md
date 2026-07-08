# Privacy Dashboard Readiness Plan

## Ziel

Dieses Dokument plant ein spaeteres lokales Privacy Dashboard fuer Friday.

Das Dashboard soll dem Nutzer sichtbar machen:

- welche lokalen Datenbereiche existieren,
- welche Module lokal schreiben duerfen,
- welche Aktionen hart gegatet sind,
- welche externen Aktionen deaktiviert bleiben,
- welche lokalen Safety-Scanner vorhanden sind.

Dieser Schritt ist nur Planung. Es wird noch kein Privacy Dashboard implementiert.

## Geplanter Anzeigenumfang

| Bereich | Anzeige | Schreibaktion |
|---|---|---|
| Safety-Flags | aktiv/deaktiviert | keine |
| Lokale Datenbank | Pfad/Status | keine |
| Aufgaben | Anzahl und Storage-Hinweis | keine |
| Kontakt-Kontexte | Anzahl und Consent-Hinweis | keine |
| Review-Vorschlaege | Pending-/Status-Hinweis | keine |
| Backup / Restore | lokale Pfade und Tokens | keine |
| Obsidian | Preview/Dry-Run/Write-Gate-Status | keine |
| Local Model | Mock-/Preview-Status | keine |
| Safety Scanner | Scanner-Namen und letzter Smoke-Hinweis | keine |

## Safety-Flags

Das Dashboard soll diese Werte sichtbar machen:

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

## Geplante Nutzertexte

Das Dashboard soll knapp und eindeutig sein:

```text
Privacy Dashboard

Friday arbeitet lokal.
Externe Aktionen sind deaktiviert.
Schreibaktionen brauchen harte Tokens.

Lokale Daten:
- Aufgaben: lokal in SQLite
- Kontakte: lokal in SQLite, nur mit SPEICHERN
- Backups: local_data/backups/
- Restore-Kopien: local_data/restores/
```

## Nicht-Ziele

- Keine Daten loeschen.
- Keine Daten exportieren.
- Keine Schreibrechte aendern.
- Keine Tokens speichern.
- Keine externen Dienste pruefen.
- Keine Netzwerkaktionen.
- Keine Provider-Aufrufe.
- Kein Obsidian Write.
- Kein Restore Write.
- Keine Datenbankschema-Aenderung.

## Spaetere Implementierungsgrenzen

Wenn das Privacy Dashboard spaeter implementiert wird:

1. Es soll read-only starten.
2. Es soll keine `input()`-/`print()`-Logik in isolierten Hilfsmodulen enthalten.
3. Es soll vorhandene Repository-/Agent-Methoden nur lesend verwenden.
4. Es soll keine personenbezogenen Details ungefragt voll ausgeben.
5. Es soll sensible Freitexte nicht anzeigen, sondern nur einen Hinweis auf gespeicherte Felder geben.
6. Es soll keine externen Integrationen aktivieren.

## Testplanung

Spaetere Tests sollten pruefen:

- Privacy Dashboard zeigt alle Safety-Flags.
- Externe Aktionen werden als deaktiviert angezeigt.
- Backup-/Restore-Pfade werden lokal angezeigt.
- Contact/Task/Review-Daten werden nur zusammengefasst.
- Kein Write wird ausgefuehrt.
- Keine Datenbankschema-Aenderung.
- CLI-Rueckkehr bleibt stabil.

## Safety-Bewertung

- Dieser Schritt ist Doku-only.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine externen Aktionen.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung

Naechster sinnvoller Build Step:

Privacy Dashboard Read-Only Model.
