# Friday Local MVP User Acceptance Script

## Ziel

Dieses Dokument beschreibt einen kurzen manuellen Abnahmelauf fuer den lokalen Friday MVP.

Der Ablauf prueft, ob Friday lokal sinnvoll nutzbar ist, ohne externe Aktionen auszufuehren.

## Wichtige Regeln fuer den Abnahmelauf

- Keine echten Nachrichten senden.
- Keine echten Kalendertermine erstellen.
- Keine externen Provider aktivieren.
- Keine Cloud-AI verwenden.
- Riskante lokale Write-/Delete-Flows nur pruefen, wenn ein Backup vorhanden ist und der passende harte Token bewusst verwendet wird.
- Fuer eine reine Abnahme riskante Flows bevorzugt abbrechen.

## Vorbereitung

Im Projektordner ausfuehren:

```bash
cd "C:\Users\Phili\Documents\Friday Test Build"
```

Optional zuerst die automatischen Checks starten:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

Erwartung:

- Full Regression ist gruen.
- Compilecheck ist erfolgreich.
- Safety Smoke meldet `Overall: PASS`.
- Diff Check ist sauber.

## Start von Friday

Variante 1:

```bash
python -m friday.main
```

Variante 2 auf Windows:

```bash
start_friday.bat
```

## Manueller Abnahmelauf

| Schritt | Aktion | Erwartung |
|---|---|---|
| 1 | Friday starten | Dashboard und Hauptmenue erscheinen |
| 2 | Hilfe / Uebersicht oeffnen | Lokale Bereiche und Safety-Grenzen werden erklaert |
| 3 | Aufgabenbereich oeffnen | Aufgabenmenue erscheint stabil |
| 4 | Aufgaben anzeigen/suchen | Lokale Aufgaben werden angezeigt oder leere Ergebnisse verstaendlich gemeldet |
| 5 | Tagesplanung anzeigen | Lokale Tagesplanung bleibt read-only und zeigt Empfehlungen |
| 6 | Review-Bereich oeffnen | Nachrichten-/Aufgaben-/Kontakt-Hinweise werden lokal angezeigt |
| 7 | Review Activity Summary anzeigen | Lokale Zaehler erscheinen |
| 8 | Review Activity Detail View anzeigen | Lokale Review-Eintraege erscheinen als kurze Liste |
| 9 | Review Activity Status/Type/Combined Filter testen | Filter zeigen lokale Eintraege und bleiben read-only |
| 10 | Review Activity Search testen | Suche zeigt lokale Treffer oder klare Leer-Meldung |
| 11 | Privacy Dashboard oeffnen | Lokale Daten- und Safety-Informationen werden angezeigt |
| 12 | Backup/Restore Bereich oeffnen | Preview/Guard-Texte erscheinen, riskante Aktionen bleiben token-gated |
| 13 | Obsidian Brain Preview oeffnen | Nur lokale Vorschau/Dry-Run; kein automatischer Write |
| 14 | Self-Building Preview oeffnen | Nur Preview/Status; keine riskante automatische Ausfuehrung |
| 15 | Zurueck zum Hauptmenue und Exit | Friday beendet sauber |

## Riskante Flows im Abnahmelauf

Diese Bereiche duerfen im normalen Abnahmelauf nur angeschaut oder abgebrochen werden:

| Bereich | Sicheres Verhalten |
|---|---|
| Backup Write | Nur mit `BACKUP ERSTELLEN` ausfuehren |
| Restore Write | Nur mit `RESTORE ANWENDEN` ausfuehren |
| Import Apply | Nur mit `IMPORT ANWENDEN` ausfuehren |
| Forget Person | Nur mit `PERSON VERGESSEN` ausfuehren |
| Obsidian Write | Nur mit `OBSIDIAN SCHREIBEN` ausfuehren |

Weiche Eingaben wie `ja`, `JA`, `ok`, Enter oder falsche Tokens duerfen diese Flows nicht freigeben.

## Nach dem manuellen Abnahmelauf

Noch einmal pruefen:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Akzeptanzkriterien

Der lokale MVP-Abnahmelauf ist bestanden, wenn:

- Friday startet.
- Hauptmenue und Rueckspruenge stabil funktionieren.
- Aufgaben-, Review-, Privacy-, Backup/Restore-, Obsidian- und Self-Building-Bereiche erreichbar sind.
- Read-only Bereiche keine Daten veraendern.
- Riskante Flows harte Tokens verlangen.
- Externe Aktionen nicht angeboten oder nicht ausgefuehrt werden.
- Full Regression gruen bleibt.
- Safety Smoke `Overall: PASS` meldet.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Netzwerkaktionen.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben lokal-only.
- Harte Tokens bleiben fuer riskante Flows Pflicht.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Friday Local MVP Release Notes.
