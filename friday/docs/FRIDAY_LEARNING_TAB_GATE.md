# Friday Lernen-Reiter Gate

## Ziel

Der neue Bereich `Lernen` zeigt lokale Routine-Kandidaten aus vorhandenen Friday-Daten und wandelt Nutzerantworten in lokale Regeln um. Lernen bedeutet hier gespeicherte Regeln und Praeferenzen, kein Modell-Nachtraining.

## Lokal erkannte Routinen

| Muster | Frage | Wirkung nach Antwort |
|---|---|---|
| Haeufiger unbekannter Absender | "Wer ist das?" | Kontakt wird lokal eingeordnet, optional mit Betreuer |
| Kunde ohne Betreuer | "Wer betreut diesen Kunden?" | Kontakt bekommt lokal einen Betreuer |
| Wiederkehrendes Mail-Thema | "Daraus Aufgabe vorschlagen?" | Aktive Regel kann spaeter Task-Suggestions erlauben |
| Wiederkehrender Kalendertermin ohne Kategorie | "Welche Kategorie ist das?" | Lokale Kalender-Kategorisierungsregel |

## Gespeicherte Daten

Neue lokale SQLite-Tabellen:

- `learning_questions`
- `learned_rules`

Beide Tabellen sind additiv und idempotent. Sie speichern nur lokale Fragen, Antworten und Regeln.

## Mobile und CLI

- Mobile: neuer Tab `Lernen` mit offenen Fragen, Antwortbuttons, `Später` und Regelverlauf.
- CLI: neuer Hauptmenuepunkt `17. Lernen`.
- Regeln koennen angezeigt und aktiviert/deaktiviert werden.

## Agentenwirkung

Aktive Regeln werden lokal genutzt:

- `is_relevant_for_user` kann gelernte Sender-/Task-Regeln beruecksichtigen.
- `build_agent_context` nimmt aktive Regeln als lokale Kontextnotiz auf.
- Antworten wirken dadurch direkt auf lokale Vorschlaege und KI-Drafts.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine neuen Netzwerkziele.
- Kein Modell-Nachtraining.
- Keine neuen Pakete oder Scopes.
- Routine-Erkennung liest nur lokale Daten.
- Sende-Flags bleiben unveraendert:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
- Kalender-Schreiben bleibt nur ueber bestehende harte Gates erlaubt.

## Tests

Fokus-Tests:

- `friday/tests/test_routine_detector.py`
- `friday/tests/test_learning_repository.py`
- `friday/tests/test_friday_api_learning.py`
- Erweiterungen in:
  - `friday/tests/test_todo_relevance.py`
  - `friday/tests/test_agent_context_builder.py`
  - `friday/tests/test_menu.py`

## Empfehlung

Als naechsten Schritt sollte der Lern-Reiter um feinere Regeltypen erweitert werden, z. B. regelbasierte Kalender-Kategorien in der Kalenderansicht oder eine Such-/Filterfunktion fuer gelernte Regeln.
