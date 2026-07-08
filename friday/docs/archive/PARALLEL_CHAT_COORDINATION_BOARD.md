# Parallel Chat Coordination Board

## Ziel

Dieses Dokument hilft dabei, die Arbeit aus Chat 1, Chat 2 und Chat 3 spaeter sauber zusammenzufuehren.

Es ist nur eine Koordinationshilfe:

- keine Produktlogik,
- keine Tests,
- keine Datenbankschema-Aenderung,
- keine externen Aktionen.

## Aktuelle Chat-Aufteilung

| Chat | Verantwortungsbereich | Start-Step | Status |
|---|---|---|---|
| Chat 1 | Produktfunktionen und CLI | Next Local Product Feature Planning after Review Activity Status Filter | fertig gemeldet |
| Chat 2 | Safety, Privacy, Backup, Restore | Privacy / Backup / Restore Finalization Audit | fertig gemeldet |
| Chat 3 | Obsidian, Local AI, Self-Building, Release-Doku | Obsidian Brain Finalization Plan | fertig gemeldet |

## Konsolidierter Stand nach den drei Chats

| Bereich | Ergebnis |
|---|---|
| Chat 1 Produkt/CLI | Review Activity Type Filter, Search und weitere Review-CLI-Erweiterungen sind im aktuellen Projektstand sichtbar |
| Chat 2 Safety/Privacy/Backup/Restore | Forget Person, Backup/Restore Safety und Privacy-Erweiterungen sind im aktuellen Projektstand sichtbar |
| Chat 3 Obsidian/Local AI/Self-Building/Release-Doku | Obsidian, Local AI, Self-Building und Release-Doku-Artefakte sind im aktuellen Projektstand sichtbar |
| Full Regression | `983 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Diff Check | sauber |

## Rueckmeldung pro Chat

Jeder Chat sollte am Ende jedes Blocks diese Punkte liefern:

1. Selected Sub-Agents
2. Implementation Summary
3. Changed Files
4. Complete Code / Content for changed documentation files
5. Safety Check
6. Test Commands + Results
7. Simple German Explanation
8. Next Recommended Build Step

## Zusammenfuehrungs-Checkliste

| Check | Zweck | Status |
|---|---|---|
| Geaenderte Dateien vergleichen | Ueberschneidungen zwischen Chats erkennen | vorlaeufig konsolidiert |
| Teststaende vergleichen | Pruefen, welcher Stand zuletzt voll gruen war | `983 passed, 4 skipped` |
| Safety Checks vergleichen | Sicherstellen, dass keine externen Aktionen aktiviert wurden | `Overall: PASS` |
| Doku-Index zusammenfuehren | Neue Dokumente aus allen Chats zentral einordnen | vorlaeufig konsolidiert |
| README_USER zusammenfuehren | Nutzer-Doku ohne doppelte oder widerspruechliche Abschnitte halten | vorlaeufig konsolidiert |
| Final Full Regression | Nach Zusammenfuehrung komplette Tests ausfuehren | erledigt |
| Final Safety Smoke | Nach Zusammenfuehrung Scanner pruefen | erledigt |

## Potenzielle Konfliktdateien

Diese Dateien werden wahrscheinlich von mehreren Chats beruehrt und sollten spaeter bewusst zusammengefuehrt werden:

- `friday/docs/README_USER.md`
- `friday/docs/cli_documentation_index_12l.md`
- `friday/docs/SAFETY_MATRIX.md`
- `friday/docs/DATA_MODELS.md`
- `friday/app/interface.py`
- `friday/tests/test_interface_combined_review.py`
- `friday/tests/test_interface_main_menu_e2e.py`

## Safety-Grenzen fuer alle Chats

- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine externen Provider.
- Keine Netzwerkaktionen.
- Keine Datenbankschema-Aenderung ohne eigenes Gate.
- Keine Obsidian Writes ohne Guard und harten Token.
- Keine echten AI-Modellaufrufe im Produktfluss.
- Safety-Flags bleiben lokal-only.
- Delete-Policy bleibt unveraendert.

## Finaler Merge-Plan

Wenn alle drei Chats Statusmeldungen geliefert haben:

1. Changed Files aus allen Chats sammeln.
2. Konfliktdateien zuerst manuell vergleichen.
3. Doku-Index und README_USER konsolidieren.
4. Full Regression ausfuehren.
5. Compilecheck ausfuehren.
6. Safety Smoke ausfuehren.
7. Finales Release-/Readiness-Gate aktualisieren.

## Naechster sinnvoller Schritt

Nach den drei fertig gemeldeten Chats sollte als naechstes ein gemeinsames lokales MVP Release Consolidation Gate erstellt werden.

Dieses Gate sollte bestaetigen:

1. welche Bereiche jetzt MVP-ready sind,
2. welche Bereiche bewusst deferred bleiben,
3. dass Full Regression, Compilecheck, Safety Smoke und Diff Check gruen sind,
4. dass keine externen Aktionen aktiviert wurden,
5. dass README_USER, Safety Matrix, Test Matrix und Release-Doku zusammenpassen.
