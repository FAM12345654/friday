# Privacy Cleanup Write Guard Model

## Ziel

Dieses Dokument beschreibt das isolierte, side-effect-free Guard-Modell fuer spaetere Privacy-Cleanup-Writes.

Das Modell prueft, ob ein spaeterer Cleanup-Write vorbereitet werden duerfte. Es fuehrt selbst keine Aktion aus.

## Neue Dateien

| Datei | Zweck |
|---|---|
| `friday/app/privacy_cleanup_write_guard.py` | Isoliertes Guard-Modell fuer spaetere Privacy-Cleanup-Writes |
| `friday/tests/test_privacy_cleanup_write_guard.py` | Unit-Tests fuer Token-, Scope- und Safety-Blockaden |

## Gepruefte Regeln

- Bekannte Cleanup-Bereiche werden erkannt.
- Unbekannte Bereiche werden blockiert.
- Fehlende Preview wird blockiert.
- Falsche Tokens werden blockiert.
- `ja` wird blockiert.
- `JA` wird blockiert.
- Whitespace-Abweichungen beim Token werden blockiert.
- Fehlender Safety Smoke wird blockiert.
- Aktivierte externe Aktionen werden blockiert.
- Fehlende Zielpfade fuer Datei-Cleanup werden blockiert.
- Pfade ausserhalb des erlaubten Scopes werden blockiert.
- Projektwurzel und Root-Laufwerk werden blockiert.
- Sensitive Pfade wie `.env`, Secrets und Tokens werden blockiert.
- Obsidian-Vault-Pfade werden blockiert.
- Aktive SQLite-Hauptdatenbank wird blockiert.
- Projektdateien, Tests und Skripte werden blockiert.

## Safety-Eigenschaften

Das Guard-Modell:

- loescht keine Dateien,
- schreibt keine Dateien,
- oeffnet keine SQLite-Verbindung,
- nutzt keine externen Provider,
- nutzt kein Netzwerk,
- nutzt kein `input()`,
- nutzt kein `print()`,
- veraendert keinen globalen Zustand,
- liefert nur ein strukturiertes Ergebnis.

## Ergebnisstruktur

Das Ergebnis enthaelt:

- `allowed`,
- `cleanup_area`,
- `target_path`,
- `allowed_base_path`,
- `required_token`,
- `blocked_reasons`,
- `message`,
- `preview_required`,
- `token_required`,
- `preview_only`,
- `persisted`,
- `external_action_used`,
- `write_performed`.

`write_performed` bleibt im Guard immer `False`.

## Nicht freigegeben

- Kein Cleanup Writer.
- Keine CLI-Anbindung.
- Keine Datei-Loeschung.
- Keine SQLite-Loeschung.
- Keine Kontakt-Loeschung.
- Kein Export-/Backup-/Restore-Cleanup.
- Keine externen Aktionen.

## Safety-Bewertung

- Keine echte Cleanup-Ausfuehrung.
- Keine externen Aktionen.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert:
  - `"ja"` loescht nicht,
  - `"JA"` loescht,
  - `" JA "` bleibt durch `strip()` erlaubt.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: **Privacy Cleanup Write Guard Readiness Gate**.

Ziel:

- Guard-Modell final pruefen,
- Fokus-Tests, Full Regression, Compilecheck, Safety Smoke und Diff-Check dokumentieren,
- keine neue Produktlogik,
- keine Cleanup-Ausfuehrung.
