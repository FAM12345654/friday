# Local Data Export CLI Plan

## Ziel

Dieses Dokument plant die spaetere CLI-Anbindung des lokalen Datenexports.

Der Schritt bleibt reine Planung. Es wird kein Menue geaendert, keine Produktlogik angepasst, kein Export ausgefuehrt und keine neue Eingabeabfrage eingebaut.

## Ausgangslage

Vorhanden und abgeschlossen:

- `LOCAL_DATA_EXPORT_PREVIEW_MODEL.md`
- `LOCAL_DATA_EXPORT_GUARD_MODEL.md`
- `LOCAL_DATA_EXPORT_WRITER_MODEL.md`
- `LOCAL_DATA_EXPORT_WRITER_READINESS_GATE.md`

Der Writer ist isoliert getestet. Eine CLI-Anbindung braucht ein eigenes Sicherheitsdesign, weil sie fuer Nutzer sichtbar wird und echte lokale Dateien erzeugen kann.

## Geplante Menueposition

Empfohlen ist eine spaetere Erweiterung des bestehenden Backup-/Restore- oder Privacy-Bereichs, nicht ein unklarer neuer Hauptmenuepunkt.

| Variante | Bewertung |
|---|---|
| Backup-/Restore-Menue erweitern | sinnvoll, weil Export/Backup thematisch nah sind |
| Privacy Dashboard erweitern | sinnvoll fuer Sichtbarkeit, aber Dashboard ist aktuell read-only |
| Neuer Hauptmenuepunkt | nicht empfohlen, weil Hauptmenue nicht unnoetig wachsen soll |

Empfehlung:

- Zuerst im Backup-/Restore-Menue als eigener Unterpunkt planen.
- Privacy Dashboard darf spaeter nur auf Export-Status und Doku verweisen, aber nicht direkt exportieren.

## Geplanter CLI-Ablauf

| Schritt | Verhalten |
|---|---|
| 1 | Nutzer oeffnet Backup-/Restore-Menue |
| 2 | Nutzer waehlt lokalen Datenexport |
| 3 | Friday zeigt Export-Preview und ausgeschlossene Inhalte |
| 4 | Friday zeigt Safety-Hinweis und Zielpfad unter `local_data/exports` |
| 5 | Friday prueft Safety Smoke Status |
| 6 | Friday ruft Guard mit Preview, Zielpfad, Safety Smoke und Token auf |
| 7 | Nutzer muss exakt `DATEN EXPORTIEREN` eingeben |
| 8 | Writer erstellt erst nach Guard-Freigabe lokale Exportdateien |
| 9 | CLI zeigt Zielordner und geschriebene Dateien |

## Geplante Untermenuepunkte

| Option | Bedeutung |
|---|---|
| `1` | Export-Preview anzeigen |
| `2` | Export-Safety anzeigen |
| `3` | Lokalen Datenexport starten |
| `4` | Zurueck |

## Sicherheitsmeldungen fuer Nutzer

Die CLI sollte vor einem echten Export klar anzeigen:

- Export bleibt lokal.
- Ziel liegt unter `local_data/exports`.
- Es werden keine externen Dienste genutzt.
- `.env`, Tokens, Cache-Dateien, Obsidian Vault und rohe aktive DB bleiben ausgeschlossen.
- Rohe private Nachrichtentexte werden nicht exportiert.
- Kontakt-Kontexte werden gefiltert.
- Fortfahren nur mit exakt `DATEN EXPORTIEREN`.

## Guard-Pflicht

Die CLI darf den Writer nie direkt aufrufen.

Pflichtreihenfolge:

1. Preview erstellen.
2. Safety Smoke Status bestimmen.
3. Token vom Nutzer abfragen.
4. Guard pruefen.
5. Nur bei `allowed=True` Writer aufrufen.

## Datenquellen fuer spaetere CLI-Anbindung

Die CLI darf spaeter lokale Daten sammeln aus:

- TaskAgent oder TaskRepository,
- Contact Context Repository,
- Message Suggestion Repositories,
- Safety-Flag-Konfiguration,
- Scanner-Smoke-Ergebnis.

Dabei gilt:

- keine externen Provider,
- keine Netzwerkaktion,
- keine rohe aktive DB-Kopie,
- keine privaten Roh-Nachrichtentexte,
- keine sensiblen Kontakt-Freitexte.

## Geplante Tests fuer spaetere CLI-Anbindung

Tests sollten abdecken:

- Export-Preview im CLI anzeigen,
- Export-Safety im CLI anzeigen,
- falscher Token blockiert,
- `ja`, `JA`, `ok`, leere Eingabe und Whitespace blockieren,
- exakter Token `DATEN EXPORTIEREN` startet Writer nur bei Guard-Freigabe,
- Safety Smoke FAIL blockiert,
- Zielordner existiert bereits blockiert,
- Ruecksprung ins Menue bleibt stabil,
- Exit bleibt stabil,
- keine externen Aktionen.

## Nicht-Ziele dieses Plans

- Keine Menue-Aenderung.
- Keine Interface-Aenderung.
- Keine neue Eingabeabfrage.
- Kein echter Export.
- Keine Datenbankabfrage.
- Keine Repository-Sammlung.
- Keine ZIP-Erstellung.
- Keine Cloud.
- Kein Obsidian Export.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.

## Safety-Bewertung

- Keine Produktlogik geaendert.
- Keine Tests geaendert.
- Keine CLI-Anbindung gebaut.
- Keine Dateioperation ausgefuehrt.
- Keine Datenbankabfrage.
- Keine externe Aktion.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer den naechsten Build Step

Als naechster Schritt sollte ein `Local Data Export CLI Read-Only Preview` folgen.

Dieser Schritt sollte nur:

- das Menue um eine read-only Export-Preview erweitern,
- noch keinen echten Export starten,
- keinen Token abfragen,
- keinen Writer aufrufen,
- keine Datei erzeugen,
- Tests fuer Menue, Preview-Anzeige und Ruecksprung ergaenzen.
