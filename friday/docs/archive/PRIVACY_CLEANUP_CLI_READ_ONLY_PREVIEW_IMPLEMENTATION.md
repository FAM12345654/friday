# Privacy Cleanup CLI Read-Only Preview Implementation

## Ziel

Dieser Schritt bindet die Privacy Cleanup Preview read-only in das bestehende Privacy Dashboard ein.

Die Anzeige bleibt rein informativ:

- keine Cleanup-Ausfuehrung,
- keine Token-Abfrage,
- kein Dateizugriff,
- kein SQLite-Zugriff,
- keine Loeschfunktion,
- keine externen Aktionen.

## Umsetzung

Geaenderte Dateien:

- `friday/app/menu.py`
- `friday/app/interface.py`
- `friday/tests/test_menu.py`
- `friday/tests/test_interface_main_menu_e2e.py`

Neue Dokumentation:

- `friday/docs/PRIVACY_CLEANUP_CLI_READ_ONLY_PREVIEW_IMPLEMENTATION.md`

## CLI-Verhalten

Das Privacy Dashboard hat jetzt einen zusaetzlichen read-only Menuepunkt:

| Menuepunkt | Funktion | Schreibt Daten? |
|---|---|---|
| `7` | Privacy Cleanup Preview anzeigen | Nein |
| `8` | Zurueck zum Hauptmenue | Nein |

Die Anzeige listet:

- Bereich,
- Cleanup-Typ,
- Zielpfad als Text,
- erlaubter Root,
- Count-Label,
- erforderlicher spaeterer Token,
- erlaubt/blockiert,
- Blockiergruende.

## Abgesicherte Safety-Grenzen

- Die Preview wird nur angezeigt.
- Es wird kein Token abgefragt.
- Es wird nichts geloescht.
- Es wird nichts exportiert.
- Es wird nichts importiert.
- Es wird keine Datei gelesen.
- Es wird keine SQLite-Datenbank geoeffnet.
- Es wird kein Netzwerk genutzt.
- Blockierte Bereiche bleiben sichtbar blockiert.

## Tests

Ergaenzte Tests pruefen:

- Privacy Dashboard Menueoptionen enthalten den neuen Cleanup-Preview-Punkt.
- Bestehende Privacy Dashboard Untermenues bleiben erreichbar.
- Rueckkehr erfolgt jetzt ueber `8`.
- Cleanup Preview zeigt erlaubte Bereiche und harte spaetere Tokens.
- Cleanup Preview zeigt blockierte Bereiche wie aktive SQLite-DB und globale Loeschaktion.
- Run-Loop mit Privacy Dashboard und Exit bleibt stabil.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Datenbankschema-Aenderung.
- Keine neuen Loeschpfade.
- Keine neuen Exportpfade.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer naechsten Build Step

Naechster sinnvoller Schritt:

`Privacy Cleanup CLI Read-Only Preview Readiness Gate`

Ziel: Pruefen und dokumentieren, dass die neue CLI-Anzeige weiterhin read-only bleibt und keine Cleanup-Ausfuehrung freischaltet.
