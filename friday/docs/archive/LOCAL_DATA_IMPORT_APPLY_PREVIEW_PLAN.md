# Local Data Import Apply Preview Plan

## Ziel

Dieses Dokument plant eine spaetere Import-Apply-Vorschau. Es wird noch kein Import gebaut, kein Restore aktiviert und keine aktive Friday-Datei veraendert.

Die Vorschau soll spaeter zeigen, was ein Import anwenden wuerde, bevor ein harter Token wie `IMPORT ANWENDEN` ueberhaupt akzeptiert wird.

## Ausgangslage

Vor einer spaeteren Import-Apply-Vorschau muessen bereits erfolgreich sein:

- Manifest Reader,
- Import Dry-Run,
- Safety-Pruefung,
- Exportdatei-Pruefung,
- Blockiergrund-Pruefung.

Wenn einer dieser Schritte blockiert ist, darf keine Apply-Vorschau als freigegeben angezeigt werden.

## Geplante Vorschau-Inhalte

Eine spaetere Import-Apply-Vorschau sollte mindestens anzeigen:

| Bereich | Inhalt |
|---|---|
| Quelle | Exportordner und Manifest-Zusammenfassung |
| Safety | externe Aktionen aus, Safety Smoke Status |
| Aufgaben | Anzahl geplanter Task-Importe oder Updates |
| Kontakte | Anzahl geplanter Kontakt-Kontext-Importe |
| Review | Anzahl geplanter Review-Status-Uebernahmen |
| Konflikte | blockierende Konflikte und Warnungen |
| Backup-Schutz | ob vor Apply ein lokales Backup erforderlich und verfuegbar ist |
| Ergebnis | Apply moeglich oder blockiert |

## Vorschau-Status

Die Vorschau sollte einen klaren Status liefern:

| Status | Bedeutung |
|---|---|
| `blocked` | Import darf nicht angewendet werden |
| `preview_ready` | Vorschau ist vollstaendig, Apply waere spaeter mit hartem Token denkbar |
| `warnings` | Vorschau ist moeglich, aber Nutzer muss Warnungen sehen |
| `invalid` | Exportdaten sind ungueltig oder unvollstaendig |

## Harte Blockiergruende

Ein spaeterer Import-Apply muss blockieren bei:

- fehlendem Manifest,
- ungueltigem Manifest,
- fehlenden Exportdateien,
- ungueltigem JSON,
- externen Flags auf aktiv,
- sensiblen Kontakt-Freitexten,
- `external_lookup_used = True`,
- fehlendem Backup-Schutz,
- Konflikten ohne Nutzerentscheidung,
- Versuch, aktive SQLite-Rohdatei direkt zu ersetzen.

## Keine automatische Aktion

Die Apply-Vorschau darf nicht:

- importieren,
- Daten schreiben,
- aktive Daten ersetzen,
- Konflikte automatisch loesen,
- externe Aktionen ausfuehren,
- Netzwerkzugriffe starten,
- Provider aufrufen.

## Spaeterer Testplan

Wenn die Vorschau spaeter modelliert wird, sollten Tests pruefen:

- valide Exportdaten erzeugen `preview_ready`,
- fehlendes Manifest erzeugt `blocked`,
- fehlende Datei erzeugt `blocked`,
- sensible Felder erzeugen `blocked`,
- externe Flags erzeugen `blocked`,
- fehlender Backup-Schutz erzeugt `blocked`,
- Warnungen bleiben sichtbar,
- keine Datei wird geschrieben,
- keine aktive Datenbank wird veraendert.

## Safety-Bewertung

- Dieses Dokument ist nur Planung.
- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Kein Import implementiert.
- Kein Restore implementiert.
- Keine Datenbankschema-Aenderung.
- Keine externen Aktionen.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Local Data Import Apply Preview Model.
