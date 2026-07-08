# Friday Local MVP Post-Release Roadmap

## Ziel

Diese Roadmap beschreibt die sinnvolle Weiterentwicklung nach dem lokalen MVP-GO von Friday.

Der lokale MVP ist freigegeben. Externe Integrationen, Cloud-Provider und echte Nachrichten-/Kalenderaktionen bleiben weiterhin deferred und brauchen eigene Gates.

## Ausgangslage

| Bereich | Stand |
|---|---|
| Lokaler MVP | GO |
| Full Regression | `983 passed, 4 skipped` |
| Compilecheck | erfolgreich |
| Safety Smoke | `Overall: PASS` |
| Externe Aktionen | NO-GO / deferred |

## Leitprinzipien nach MVP-GO

- Keine riskanten Features ohne eigenes Plan-/Guard-/Readiness-Gate.
- Lokale Features zuerst.
- Read-only vor Write.
- Preview vor Apply.
- Harte Tokens fuer riskante lokale Writes.
- Externe Integrationen zuletzt.
- Safety Smoke bleibt Pflichtcheck.

## Phase 1: Lokale Stabilisierung

| Thema | Ziel | Risiko |
|---|---|---|
| User-Journey Smoke Runs | Echte lokale Demo-Pfade regelmaessig pruefen | niedrig |
| README_USER Feinschliff | Nutzerstart weiter vereinfachen | niedrig |
| CLI Text Polish | Menues und Fehlermeldungen weiter vereinheitlichen | niedrig |
| Doku-Link-Check | Lokale Markdown-Links pruefen | niedrig |
| Release Notes | Aktuelle MVP-Version kurz beschreiben | niedrig |

## Phase 2: Lokale Produktverbesserungen

| Thema | Ziel | Risiko |
|---|---|---|
| Review Export mit Guard | Lokale Review-Uebersicht exportieren | mittel |
| Task Contact Snapshot | Kontaktbezug in Aufgaben sichtbarer machen | mittel |
| Tagesplanung verfeinern | Lokale Tagesplanung nutzerfreundlicher machen | niedrig bis mittel |
| Kontakt-CLI UX verbessern | Kontakte einfacher suchen/bearbeiten | mittel |
| Privacy Data View verbessern | Gespeicherte Daten noch transparenter anzeigen | niedrig |

## Phase 3: Lokale Write-Flows haerten

| Thema | Ziel | Risiko |
|---|---|---|
| Obsidian Write UX | Hart gegatete Writes nutzerfreundlicher machen | mittel |
| Restore Write UX | Restore-Flows weiter absichern | mittel |
| Forget Person Audit | Loeschpfade noch klarer dokumentieren | mittel |
| Backup Rotation | Alte lokale Backups kontrolliert verwalten | mittel |

## Phase 4: Lokale AI nur kontrolliert

| Thema | Ziel | Risiko |
|---|---|---|
| Local Model Settings | Mock bleibt Default, lokale Adapter optional | mittel |
| Ollama Health Check | Nur lokale Erreichbarkeit pruefen | mittel |
| Model Output Validation | Modellantworten strikt validieren | mittel |
| Logic Check Integration | Nur sichere Plausibilitaetspruefungen | mittel |

## Phase 5: Externe Integrationen erst spaeter

Diese Bereiche bleiben nicht freigegeben, bis eigene Gates erstellt sind:

- echte E-Mail,
- echtes WhatsApp,
- echte SMS,
- echte Kalendertermine,
- Wetter-/Musik-Provider,
- Cloud-AI,
- Mobile/Publish/Cloudflare-Flows.

## Empfohlene naechste konkrete Steps

| Prioritaet | Step | Warum |
|---|---|---|
| 1 | Friday Local MVP User Acceptance Script | Ein kurzer manueller Ablauf prueft, ob die lokale Nutzung fuer dich rund ist |
| 2 | Release Notes for Local MVP | Dokumentiert den aktuellen GO-Stand kompakt |
| 3 | Documentation Link Checker Plan | Reduziert Doku-Verweisfehler nach vielen parallelen Docs |
| 4 | CLI Demo Journey Script Plan | Plant einen wiederholbaren lokalen Demo-Durchlauf |
| 5 | Review Export Guard Plan | Erstes groesseres Post-MVP-Feature, aber lokal und guardbar |
| abgeschlossen | Friday Local MVP Phase 1 Stabilization Gate | Doku-Link-Check, README-Pruefung und CLI-Text-Polish-Review abgeschlossen |

## Pflichtchecks fuer jede Post-Release-Aenderung

```bash
python -m pytest friday/tests
python -m compileall friday
python scripts/friday_safety_smoke.py
git diff --check
```

## Safety-Bewertung

- Lokaler MVP bleibt freigegeben.
- Externe Aktionen bleiben deferred.
- Safety-Flags bleiben lokal-only.
- Harte Tokens bleiben fuer riskante Flows Pflicht.
- Neue Writes brauchen eigene Guards.
- Neue externe Provider brauchen eigene Plan-/Mock-/Readiness-Gates.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Export mit Guard.
