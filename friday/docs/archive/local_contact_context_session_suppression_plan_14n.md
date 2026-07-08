# Local Contact Context Session Suppression Plan 14N

## Ziel

Planen, wie Friday in einem lokalen Session-Kontext merkt, dass ein Kontakt-Kontext-Vorschlag für einen bestimmten Kontakt bereits übersprungen wurde und in derselben Session nicht erneut gestört werden soll.

Diese Planung gilt vor Implementierung und bleibt bewusst auf **rein konzeptioneller Ebene**.

## Scope (14N)

- kein Produktcode
- keine CLI-UI-Anbindung
- keine Persistenz
- keine DB-Migration
- keine externe Aktion
- keine neuen Integrationen

Die Planung bereitet die Implementierung für Build 14O vor:
- In-Memory-Suppression-State als isolierter Kern
- klare Statussemantik
- Kontext- und Scope-bezogenes Verhalten
- sichere Wiederholung von Abfragen nach Richtlinie

## Begriffe

- **Session**: Laufzeitfenster eines Programmlaufs oder definierter Review-Durchlauf.
- **Kontakt-Schlüssel**: Normalisierter Name (`normalized_name`) plus Kontext (`source_context`).
- **Skipped-Status**: Nutzer hat den Prompt für eine konkrete Kontakt/Context-Kombination bewusst übersprungen.
- **Suppressed-Status**: Der Kontakt/Context ist aktiv unterdrückt und erzeugt keine erneute Frage im selben Scope.

## Zustandsmodell (Plan)

Wir planen folgende Session-Zustände:

| Zustand | Bedeutung |
|---|---|
| `unknown` | Kontakt/Kontext wurde noch nicht bewertet |
| `known` | Kontakt ist bereits bekannt/verarbeitet |
| `skipped` | Nutzer hat explizit auf die Frage verzichtet |
| `ask_later` | Rückfrage ist erlaubt, aber zurückgestellt |
| `suppressed` | Frage soll in diesem Scope unterdrückt bleiben |

## Geplantes Verhalten

### 14N (Plan)

1. Kontakt-Kandidat wird im Review/Flow erkannt.
2. Vor Anzeige wird geprüft:
   - existiert bereits ein Suppression-Eintrag für `(normalized_name, source_context)`?
3. Falls vorhanden:
   - bei `suppressed`: keine neue Prompt-Anzeige im aktuellen Scope.
4. Falls kein suppressiver Treffer:
   - normale Darstellung/Verarbeitung wie bisher im Draft-Flow.
5. Bei Nutzer-Entscheidung:
   - `skip` setzt (Planung) den Kontakt auf *nicht persistentes* `skipped`.
   - `select` verändert den Status auf `known`/`selected` nach vorhandenem Flow.
   - `invalid` bleibt Fehlerpfad ohne Status-Fortschreibung.

## Scope-Regeln (zu implementierende Trennschärfe)

| Scope | Definition | Wirkung |
|---|---|---|
| pro CLI-Lauf | Laufzeit nur im aktuellen Prozess | nach Exit entfernt |
| pro Review-Lauf | Unterdrückung nur innerhalb eines laufenden Review-Durchgangs | nächste Session darf wieder anzeigen |
| pro Kontaktname | Key enthält normalisierten Namen | verhindert Wiederholung für dieselbe Person |
| pro Kontext | Key enthält Kontext (`nachrichten_review`, `person_bearbeiten` etc.) | gleiche Person in anderem Kontext möglich |

## Konfigurierbarkeit und Sicherheit (für spätere Implementierung)

- Keine gespeicherten personenbezogenen Daten außerhalb der Session.
- Keine globale Side-Effect.
- Keine Datei-/DB-Schreibvorgänge in 14N.
- Kein Implicit-Storage ohne Nutzerinteraktion.
- Delete-Policy bleibt unverändert.

## Geplante Kern-API (nur Entwurf)

- `normalize_suppression_key(display_name, source_context) -> tuple[str, str]`
- `mark_contact_prompt_skipped(display_name, source_context, entries) -> tuple[...]`
- `is_contact_prompt_suppressed(display_name, source_context, entries) -> bool`
- `clear_contact_prompt_suppression(display_name, source_context, entries) -> tuple[...]`

Die konkrete Implementierung folgt in 14O auf Basis dieses Plans.

## Prüfprinzip für Build 14N

- Plan dokumentiert und nachvollziehbar.
- Kein Datenfluss in Produktion.
- Keine Produktlogik-Änderung.
- Kein neuer Persistenzzustand.

## Sicherheit im 14N-Plan

- Externe APIs/Netzwerk **nicht genutzt**.
- Kontaktkontext bleibt lokal.
- Keine echte Speicherung.
- Safety-Flags bleiben:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` bleibt durch `strip()` weiterhin erlaubt (bestehender Verhalten).

## Empfehlung für Build Step 14O

14O — Session Suppression Model

- In-Memory-Modell implementieren
- Datentyp + pure Funktionen für Markierung/Abfrage/Löschen
- keine DB-Persistenz
- keine CLI-Anbindung
- Fokus auf vollständige Unit-Tests
