# Local Model Readiness Planning 13G

## Ziel

Dieser Schritt definiert einen kleinen, lokalen und sicheren Rahmen für eine spätere Modell-Nutzung in Friday, ohne in diesem Schritt irgendeinen echten Modellaufruf zu implementieren.

## Problemstellung

Friday braucht eine klare Grundlage, damit spätere Modell-Funktionen (z. B. bessere Priorisierung, Kontextanreicherung oder intelligente Vorschläge) kontrolliert, nachvollziehbar und lokal-first aufgebaut werden können.

## Grundprinzipien

- Modellfunktionalität bleibt in 13G bewusst deaktiviert.
- Nur lokale Logik, keine Provider- oder Netzwerkanrufe.
- Alle bestehenden Safety- und Approval-Grenzen bleiben unangetastet.
- Lokale Workflows (Tasks, Messages, Review, Export) bleiben unverändert.

## Geplante Definitionen

- **Modellstrategie-Modus** (nur Konfiguration, noch nicht aktiv):
  - `disabled`
  - `dry_run`
  - `local_mock`
  - `future_provider`
- **Readiness-Merkmale**:
  - `mode_supported`
  - `provider_config_present`
  - `approval_flow_available`
  - `safety_flags_locked`
  - `fallback_path_defined`
- **Fallback-Policy**:
  - Bei jedem Unsicherheitsfall wird ein deterministischer lokal-regelbasierter Pfad genutzt.
  - Keine impliziten externen Annahmen.

## Nicht-Ziele in 13G

- Keine echten Modellaufrufe.
- Kein neuer Datenbank-Schema-Änderungen.
- Keine neuen Produktflüsse in der Live-CLI.
- Keine Änderungen an Delete-/Done-/Archive-/Review-Logik.

## Vorbereitete Artefakte für spätere Schritte

- Standardisierte Readiness-Felder für spätere Tests.
- Sicherheitsgrenzen für spätere Review- und Entscheidungspfade.
- Explizite Übergabepunkte für die lokale Mock-/Fallback-Strategie.

## Safety-Grenzen

- Keine externen Nachrichten.
- Kein echter WhatsApp-Flow.
- Kein echtes E-Mail-Verhalten.
- Keine echte SMS.
- Kein echter Kalenderzugriff.
- Kein echtes Wetter-/Musik-Verhalten.
- Alle externen Flags bleiben unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` bleibt durch `strip()` zugelassen

## Empfohlener nächster Schritt 13H

13H sollte als **Local Model Readiness Criteria & Integration Boundaries** umgesetzt werden:

- welche Felder im Readiness-Payload verpflichtend sind,
- wie der lokale Fallback standardmäßig reagiert,
- wie Risiken und Freigaben in Review- und Entscheidungsabläufen bewertet werden.
