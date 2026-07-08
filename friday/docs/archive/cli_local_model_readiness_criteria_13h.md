# Local Model Readiness Criteria & Integration Boundaries 13H

## Ziel

Dieser Schritt legt fest, wann Friday eine Modell-Funktionalität überhaupt als „bereit für lokale Vorbereitung“ betrachtet.

## Gated Kriterien (Vorlage)

| Bereich | Prüfkriterium | Erwarteter Zustand |
|---|---|---|
| Safety | Alle externen Real-Flags bleiben `False` | `ENABLE_REAL_EMAIL = False`, `ENABLE_REAL_WHATSAPP = False`, `ENABLE_REAL_SMS = False`, `ENABLE_REAL_CALENDAR = False`, `ENABLE_REAL_WEATHER = False`, `ENABLE_REAL_MUSIC = False` |
| Datenhaltung | Lokaler Storage bleibt aktiv | `USE_SQLITE_STORAGE = True` |
| Freigabe | Nutzerfreigabe bleibt aktiv | `REQUIRE_USER_APPROVAL = True` |
| Aktionen | Keine neue Live-Aktion in diesem Schritt | Keine direkten Modell-Ausgaben mit Seiteneffekten |
| Modellmodus | Mode ist klar definiert | Nur `disabled` oder `dry_run` erlaubt |
| Fallback | Deterministischer Rückfallpfad existiert | Bei Blocker oder unsicheren Eingaben bleibt lokale Regel-Logik aktiv |
| Risiko | Keine ungeklärte Datenschutz- oder Provider-Risiko-Route | Keine externen Datenabflüsse vorgesehen |

## Bewertungslogik

- `disabled`: alle Modellpfade sind ausgeschaltet.
- `dry_run`: Nur strukturierte Readiness-Checks laufen, keine echten Calls.
- Kein neuer `local_data` oder Dateisystemschreibpfad für Modell-Daten in 13H.
- Bestehende Tests/Flüsse (Task/Review/Safety) dürfen nicht verändert werden.

## Sicherheit in Review-/Decision-Pfaden

- Keine versteckte Freigabe in Modelllogik.
- Falls später ein Vorverarbeitungs-Schritt ergänzt wird:
  - klarer Status (pending/approved/rejected) erforderlich,
  - keine stillen Aktionen auf Task- oder Nachrichtendaten.
- Bestehende Delete-Policy bleibt unberührt.

## Offene Risiken

- Fehlende zentrale, formale Modell-Policy (wird erst nach 13H implementiert).
- Klares Mapping von Kontextfeldern in Review-Flows noch nicht produktiv.
- UI-Text für Modell-Status noch nicht definiert.

## Sicherheitscheck

- Keine externen Aktionen in diesem Schritt.
- Keine neuen externen Provider.
- Keine neuen Datenbankänderungen.
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` bleibt durch `strip()` zugelassen

## Empfohlener nächster Schritt 13I

13I sollte als **Local Model Readiness Gate & Rollout-Proposal** dienen:

- kurze Zusammenfassung, dass Modell-Funktionen noch nicht aktiv sind,
- dokumentierter freigegebener Umsetzungsumfang für den nächsten Schritt,
- klare Empfehlung für den nächsten kleinen Implementations-Block.
