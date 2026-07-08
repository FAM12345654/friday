# Next Local Product Feature Planning after Review Batch

## Ziel

Dieses Dokument plant den naechsten kleinen lokalen Produktblock nach dem final abgenommenen Review-Batch-Selection-Block.

Dieser Step bleibt bewusst Planung:

- keine Produktlogik-Aenderung,
- keine neuen Tests,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Ausgangslage

Der Review-Batch-Selection-Block ist abgeschlossen:

- Batch-Auswahl im Review-Bereich ist vorhanden.
- Batch-Preview ist vorhanden.
- Guarded Apply ist vorhanden.
- Harte Tokens sind dokumentiert.
- Nutzer-Doku ist aktualisiert.
- Full Regression ist gruen.

Damit ist der Review-Workflow deutlich produktiver, aber Nutzer haben noch keine kompakte lokale Uebersicht darueber, welche Review-Aktionen bereits lokal passiert sind.

## Bewertete Optionen

| Option | Nutzen | Risiko | Testaufwand | Empfehlung |
|---|---|---|---|---|
| Review Activity Summary | Zeigt lokale Review-Zustaende und kuerzlich veraenderte Vorschlaege kompakt an | niedrig, read-only moeglich | niedrig bis mittel | empfohlen |
| Review Batch Undo Plan | Koennte versehentliche lokale Batch-Aktionen rueckgaengig machen | hoeher, Statuswechsel/History komplex | hoch | spaeter planen |
| Task Follow-up Preview | Zeigt aus Review erzeugte Aufgaben als Follow-up-Liste | mittel | mittel | spaeter sinnvoll |
| Review Filters | Filtert offene/approved/rejected/converted Vorschlaege | mittel | mittel | nach Summary sinnvoll |
| Review Export | Exportiert Review-Zusammenfassung lokal | mittel, Schreibpfad noetig | mittel | spaeter nach read-only Summary |

## Empfohlener naechster Produktblock

**Name:** Review Activity Summary

**Kurzbeschreibung:**

Ein read-only CLI-Bereich im Review-Menue, der lokale Review-Aktivitaet zusammenfasst.

Der Bereich soll zeigen:

- Anzahl offener Nachrichten-Vorschlaege,
- Anzahl offener Aufgaben-Vorschlaege,
- Anzahl lokal freigegebener Nachrichten-Vorschlaege,
- Anzahl abgelehnter Vorschlaege,
- Anzahl konvertierter Aufgaben-Vorschlaege,
- zuletzt lokal veraenderte Vorschlaege, soweit vorhandene Daten das stabil hergeben.

## Warum dieser Step sinnvoll ist

- Er schliesst natuerlich an Review-Batch-Apply an.
- Er hilft Nutzern zu verstehen, was lokal bereits passiert ist.
- Er kann read-only gebaut werden.
- Er braucht keine externen Dienste.
- Er braucht voraussichtlich keine Datenbankschema-Aenderung.
- Er ist gut testbar mit vorhandenen Repositories und tmp_path SQLite.

## Nicht-Ziele

- Kein Undo.
- Kein echter Versand.
- Keine Kalenderaktion.
- Kein Export.
- Kein neues Datenbankschema, solange vorhandene Statusfelder reichen.
- Keine automatische Bereinigung.
- Keine Standing Approvals.

## Vorgeschlagener Build Step

Naechster Step: **Review Activity Summary Plan**.

Ziel des naechsten Steps:

- genauer planen, welche Daten aus vorhandenen Message- und Task-Suggestion-Repositories gelesen werden,
- CLI-Ort festlegen,
- Safety-Grenzen dokumentieren,
- Testplan festlegen,
- noch keine Implementierung.

## Vorgeschlagene spaetere Implementierung

Nach dem Plan koennte ein kleiner read-only Implementierungsstep folgen:

- neue reine Summary-Funktion oder Interface-Methode,
- Anzeige im Review-Bereich,
- keine Schreiboperation,
- Tests in `test_interface_combined_review.py` oder fokussiertem neuen Testmodul.

## Teststrategie fuer spaetere Implementierung

Fokus-Tests:

```bash
python -m pytest friday/tests/test_interface_combined_review.py
python -m pytest friday/tests/test_message_suggestion_repository.py
python -m pytest friday/tests/test_task_suggestion_repository.py
```

Full Checks:

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Naechster empfohlener Produktblock bleibt read-only.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung geplant.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Review Activity Summary Plan**.

Ziel:

- read-only Review-Aktivitaetsuebersicht sauber planen,
- keine Produktimplementierung im Plan-Step,
- bestehende Review-Batch-Safety beibehalten.
