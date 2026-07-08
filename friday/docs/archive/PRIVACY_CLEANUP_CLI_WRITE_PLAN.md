# Privacy Cleanup CLI Write Plan

## Ziel

Dieses Dokument plant, wie eine spaetere CLI-Anbindung fuer Privacy Cleanup Writes sicher aussehen duerfte.

Dieser Schritt ist bewusst nur Planung:

- keine CLI-Implementierung,
- keine Produktlogik,
- keine Datei-Loeschung,
- keine SQLite-Loeschung,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Bereits vorhanden:

- Privacy Cleanup Policy,
- Privacy Cleanup Preview Model,
- Privacy Cleanup CLI Read-Only Preview,
- Privacy Cleanup Write Guard Model,
- Privacy Cleanup Writer Model,
- Readiness Gates fuer Guard und Writer.

Aktuell ist die CLI nur read-only:

```text
Hauptmenue -> 12. Privacy Dashboard -> 7. Privacy Cleanup Preview anzeigen
```

Ein produktiver Cleanup-Write ist nicht im CLI erreichbar.

## Geplanter CLI-Grundsatz

Eine spaetere CLI-Anbindung darf Cleanup nie direkt ausfuehren.

Die CLI muss immer diese Reihenfolge erzwingen:

1. Read-only Cleanup Preview anzeigen.
2. Nutzer waehlt einen konkret erlaubten Cleanup-Bereich.
3. CLI zeigt Zielpfad und Risiko erneut an.
4. Safety Smoke wird ausgefuehrt oder sein aktueller Status wird geprueft.
5. Guard wird mit Preview, Zielpfad, Scope und Token-Regeln vorbereitet.
6. Harte Token-Abfrage erfolgt erst nach der Warnung.
7. Guard muss `allowed=True` liefern.
8. Writer wird mit `dry_run=False` nur fuer erlaubte Datei-Scopes aufgerufen.
9. Ergebnis wird angezeigt.

## Geplante Menue-Erweiterung

Eine spaetere CLI-Erweiterung koennte im Privacy Dashboard separat erscheinen:

```text
Privacy Dashboard
1. Safety-Flags anzeigen
2. Lokale Datenbereiche anzeigen
3. Schreib-/Exportstatus anzeigen
4. Scanner-Status anzeigen
5. Externe Aktionen anzeigen
6. Privacy Data Management Inventory anzeigen
7. Privacy Cleanup Preview anzeigen
8. Privacy Cleanup ausfuehren
9. Zurueck zum Hauptmenue
```

Wichtig:

- Option `8` existiert aktuell noch nicht.
- Die Rueckkehr-Option wuerde sich in einem spaeteren Step von `8` auf `9` verschieben.
- Das darf nur mit Tests und Doku-Synchronisierung passieren.

## Geplante CLI-Flow-Regeln

| Schritt | Regel |
|---|---|
| Bereich auswaehlen | Nur bekannte Bereiche, unbekannte Eingaben blockieren |
| Preview anzeigen | Immer vor Token-Abfrage |
| Ziel anzeigen | Pfad/Scope klar zeigen, keine sensiblen Inhalte |
| Warnung anzeigen | Klare deutsche Warnung vor Loeschung |
| Token abfragen | Exakter bereichsspezifischer Token |
| Guard pruefen | Muss `allowed=True` liefern |
| Writer aufrufen | Nur fuer Datei-Scopes und nur nach Guard |
| Ergebnis anzeigen | Anzahl geloescht/uebersprungen, keine sensiblen Inhalte |

## Geplante harte Tokens

| Bereich | Token |
|---|---|
| Export-Cleanup | `EXPORT AUFRAEUMEN` |
| Backup-Cleanup | `BACKUP AUFRAEUMEN` |
| Restore-Work-Cleanup | `RESTORE AUFRAEUMEN` |

Weiterhin nicht per CLI freigegeben:

- `REVIEW AUFRAEUMEN`,
- `KONTAKT LÖSCHEN`.

Diese Bereiche brauchen eigene DB-/Kontakt-Gates.

## Geplante Warntexte

Beispiel fuer spaetere CLI:

```text
WARNUNG: Diese Aktion kann lokale Dateien entfernen.
Friday zeigt zuerst eine Vorschau und prueft danach den Safety Guard.
Es werden keine externen Aktionen ausgefuehrt.
```

Vor dem Token:

```text
Zum Ausfuehren tippe exakt:
EXPORT AUFRAEUMEN
```

Abbruch:

```text
Cleanup wurde abgebrochen.
```

Erfolg:

```text
Privacy Cleanup wurde lokal ausgefuehrt.
```

## Geplante Block-Regeln

Die CLI muss abbrechen, wenn:

- keine Preview vorhanden ist,
- der Bereich unbekannt ist,
- der Zielpfad nicht angezeigt werden kann,
- Safety Smoke nicht erfolgreich ist,
- der Token nicht exakt passt,
- Guard blockiert,
- Writer blockiert,
- Bereich DB-/Kontakt-Cleanup betrifft,
- Zielpfad ausserhalb erlaubter Scopes liegt,
- Ziel das neueste Backup ist,
- Nutzer nur `ja` oder `JA` eingibt.

## Tests fuer spaetere Implementierung

Wenn die CLI-Anbindung spaeter gebaut wird:

- Menue zeigt Cleanup-Write-Option.
- Preview wird vor Token-Abfrage angezeigt.
- Enter bricht ab.
- `ja` bricht ab.
- `JA` bricht ab.
- Falscher Token bricht ab.
- Richtiger Token ruft Guard und Writer auf.
- Guard-Block zeigt Fehlermeldung.
- Writer-Block zeigt Fehlermeldung.
- Dry-Run-/Preview-Pfad bleibt unveraendert.
- Rueckkehr ins Privacy Dashboard bleibt stabil.
- Exit aus Hauptmenue bleibt stabil.

## Nicht-Ziele dieses Schritts

- Keine CLI-Option implementieren.
- Keine Menue-Aenderung.
- Keine Writer-Anbindung.
- Keine Dateioperation.
- Keine SQLite-Operation.
- Keine Loeschung.
- Keine Tests.
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

Naechster sinnvoller Build Step: **Privacy Cleanup CLI Write Preview Gate**.

Ziel:

- vor der Implementierung pruefen, ob Preview, Guard, Writer und Menue-Safety zusammenpassen,
- keine CLI-Implementierung,
- keine produktive Cleanup-Ausfuehrung.
