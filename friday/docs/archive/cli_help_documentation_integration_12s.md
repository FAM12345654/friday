# CLI Help Documentation Integration 12S

## Ziel

Der Build Step 12S integriert den existierenden Help-/Command-Overview-Path in die zentrale Dokumentationsstruktur ohne neue Produktlogik oder neue Features.

## Ergänzte Stellen

- `friday/docs/README_USER.md`
  - Punkt `Hilfe / Übersicht` in „Was kann Friday im Moment?“ ergänzt.
  - Neue Sektion `## Hilfe / Übersicht` mit klarer Beschreibung der lokalen Grenzen.
- `friday/docs/cli_documentation_index_12l.md`
  - Bestehende Index-Tabelle ergänzt um:
    - `cli_help_overview_12q.md`
    - `cli_help_edge_cases_12r.md`
    - `cli_help_documentation_integration_12s.md`
- `friday/docs/cli_runtime_readiness_12o.md`
  - Stabilitätsbereich „CLI Help / Command Overview“ ergänzt.
- `friday/app/interface.py`
  - Help-Text wurde geprüft; das in 12S genannte bekannte Typoskript ist bereits korrekt hinterlegt:
    - `Help ist lokal, es werden nur Informationen angezeigt.`

## Integrationshinweis

- Der Hilfe-/Überblickspfad bleibt reine Informationsanzeige (`8. Hilfe / Übersicht`) und verändert keine Daten oder Status.
- Es bleiben die Sicherheitsgrenzen bestehen:
  - keine echten Nachrichten,
  - keine echten Kalendertermine,
  - keine externen APIs/Provider-Aufrufe.

## Safety

- Keine Produktlogik geändert.
- Keine externen Aktionen aktiviert.
- Keine Datenbankschemaänderung.
- Safety-Flags unverändert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy unverändert:
  - `"ja"` löscht nicht.
  - `"JA"` löscht.
  - `" JA "` bleibt durch `.strip()` erlaubt.

## Empfehlung für Build Step 12T

- Abschlussstatus dokumentieren, dass 12S stabil in Nutzer- und Dokuindex integriert ist.
