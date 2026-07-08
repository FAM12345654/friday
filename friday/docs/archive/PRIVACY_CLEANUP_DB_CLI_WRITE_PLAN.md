# Privacy Cleanup DB CLI Write Plan

## Ziel

Dieses Dokument plant, ob und wie ein spaeterer SQLite Privacy Cleanup DB Write sicher im Privacy Dashboard angeboten werden duerfte.

Der Schritt bleibt bewusst reine Planung:

- keine Produktlogik,
- keine Tests,
- keine neue CLI-Write-Funktion,
- keine SQLite-Schreiboperation,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Der DB-Cleanup-Stack ist vorhanden:

- read-only DB Preview,
- DB Guard,
- DB Writer,
- read-only DB-Cleanup-Preview-Anzeige im Privacy Dashboard.

Noch nicht aktiv:

- DB-Cleanup-Write im Privacy Dashboard,
- Nutzerfluss fuer DB-Cleanup-Ausfuehrung,
- Backup-Nachweis im DB-Cleanup-Menue,
- Safety-Smoke-Gate im DB-Cleanup-Menue.

## Geplanter CLI-Write-Pfad

Ein spaeterer DB-Cleanup-Write duerfte nur nach einer separaten Menue-Option angeboten werden.

Vorgeschlagener Pfad:

```text
Privacy Dashboard
9. DB-Cleanup Preview anzeigen
10. DB-Cleanup ausführen
11. Zurück zum Hauptmenü
```

Wichtig:

- Die bestehende read-only Preview muss erhalten bleiben.
- Write darf nie ueber denselben Menuepunkt wie Preview laufen.
- Write darf nie automatisch nach Preview starten.

## Geplanter Nutzerfluss

### 1. Bereich waehlen

```text
DB-Cleanup ausführen
1. Review-History
2. Einzelner Kontakt-Kontext
Enter/z. Zurueck
```

### 2. Preview erzeugen

Friday erzeugt direkt im Write-Flow eine frische read-only Preview.

Die Preview muss zeigen:

- Bereich,
- Kandidatenanzahl,
- Filter,
- erforderlicher Token,
- Backup-/Transaktions-/Rollback-Anforderung.

### 3. Backup-Nachweis

Vor Write muss ein Backup-Nachweis vorhanden sein.

Moegliche spaetere Regel:

- entweder letztes lokales Backup ist vorhanden,
- oder Nutzer wird auf Backup-Menue verwiesen,
- oder Write wird blockiert.

Kein DB-Write ohne Backup-Nachweis.

### 4. Safety Smoke

Vor Write muss `python scripts/friday_safety_smoke.py` bzw. der lokale Safety-Smoke-Runner `PASS` liefern.

Bei `FAIL`:

```text
DB-Cleanup wurde abgebrochen.
Safety Smoke ist fehlgeschlagen.
```

### 5. Harter Token

Erlaubte Tokens:

| Bereich | Token |
|---|---|
| Review-History | `REVIEW AUFRAEUMEN` |
| Kontakt-Kontext | `KONTAKT LÖSCHEN` |

Blockiert:

- leere Eingabe,
- `ja`,
- `JA`,
- Tokens mit Leerzeichen,
- falscher Bereichs-Token.

### 6. Guard und Writer

Ablauf:

1. Preview erzeugen.
2. Safety Smoke pruefen.
3. Backup-Nachweis pruefen.
4. Token abfragen.
5. Guard ausfuehren.
6. Nur bei `guard.allowed is True` Writer ausfuehren.
7. Ergebniszaehler anzeigen.

## Geplante Fehlermeldungen

| Situation | Meldung |
|---|---|
| Nutzer bricht ab | `DB-Cleanup wurde abgebrochen.` |
| Kein Backup | `DB-Cleanup wurde blockiert: Backup fehlt.` |
| Safety Smoke FAIL | `DB-Cleanup wurde blockiert: Safety Smoke fehlgeschlagen.` |
| Falscher Token | `DB-Cleanup wurde nicht freigegeben.` |
| Guard blockiert | `DB-Cleanup wurde nicht freigegeben.` |
| Writer rollbackt | `DB-Cleanup wurde nicht ausgefuehrt.` |
| Erfolg | `DB-Cleanup wurde lokal ausgefuehrt.` |

## Geplante Tests fuer spaetere Implementierung

Eine spaetere CLI-Write-Implementierung braucht Tests fuer:

- Preview wird vor Write angezeigt,
- Review-History falscher Token blockiert,
- Review-History exakter Token loescht nur sichere Kandidaten,
- Kontakt-Kontext falscher Token blockiert,
- Kontakt-Kontext exakter Token loescht nur ausgewaehlten Kontakt,
- `ja` und `JA` blockieren,
- fehlendes Backup blockiert,
- Safety-Smoke-Fehler blockiert,
- Guard-Fehler blockiert,
- Writer-Rollback wird angezeigt,
- Rueckkehr ins Privacy Dashboard bleibt stabil,
- keine externen Aktionen.

## Nicht-Ziele dieses Schritts

- Keine CLI-Write-Implementierung.
- Keine neue Menueoption.
- Keine SQLite-Loeschung.
- Keine Tests.
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

Naechster sinnvoller Build Step: **Privacy Cleanup DB CLI Write Preview Gate**.

Ziel:

- pruefen, ob CLI-Write-Plan, Preview, Guard, Writer und Safety-Smoke-Anforderungen bereit fuer eine spaetere Implementierung sind,
- noch keine neue Write-Funktion bauen.
