# Friday Kontakt-Betreuer und To-do-Zustaendigkeit

## Ziel

Friday kann haeufige Kontakte lokal speichern und Kunden einen Betreuer zuordnen. Diese Information steuert deterministisch, ob aus einer task-artigen Nachricht ein lokaler Aufgaben-Vorschlag fuer Philip entstehen soll.

## Umgesetzte Regeln

| Bereich | Regel |
|---|---|
| Kontaktart | `contact_type` bleibt die freie Relation/Kategorie, z. B. `arbeit`, `freund`, `familie`, `kunde` oder ein eigener lokaler Begriff. |
| Betreuer | `betreuer` gilt nur fuer `contact_type = "kunde"`. Erlaubt sind `flo`, `philip`, `alex`. |
| Nicht-Kunden | Bei anderen Kontaktarten wird `betreuer` lokal ignoriert bzw. geleert. |
| Task-Relevanz | Ein task-artiger Text wird nur vorgeschlagen, wenn er ganzwoertig `Philip`, `Phips`, `PH` oder `Zeitler` enthaelt oder wenn der bekannte Absender ein Kunde mit `betreuer = "philip"` ist. |
| KI | Die Regel ist rein deterministisch in Python und nutzt keine Cloud-KI. |

## Mobile Flow

- Im Kontakte-Tab kann ein Kontakt mit Kontaktart gespeichert werden.
- Wenn `Kunde` gewaehlt ist, kann `Flo`, `Philip` oder `Alex` als Betreuer gewaehlt werden.
- In der Nachrichtenansicht zeigt Friday bei unbekannten Absendern eine lokale Zuordnung an.
- Dort kann der Absender als Kontakt gespeichert werden; bei Kunden wird ebenfalls der Betreuer ausgewaehlt.
- Diese Zuordnung wirkt danach auf die lokale To-do-Regel.

## CLI Flow

- Im Kontakt-Kontext-Menue bleibt `5` unveraendert der Rueckweg zum Hauptmenue.
- Zusaetzlich gibt es `6. Einfachen Kontakt speichern`.
- Dort kann ein lokaler Kontakt mit Kontaktart und optionalem Kunden-Betreuer angelegt werden.

## Agent-Kontext

Bei Kunden mit Betreuer enthaelt der lokale Agent-Kontext z. B.:

```text
Kunde Kunde Alpha, Betreuer: Alex
Kontaktart: kunde
```

Damit koennen lokale Entwurfsfunktionen den Betreuer-Kontext sehen, ohne externe Daten abzurufen.

## Safety-Bewertung

- Keine echten Nachrichten werden gesendet.
- Kein WhatsApp-/E-Mail-/SMS-Versand wurde aktiviert.
- Keine Cloud-KI wurde hinzugefuegt.
- Keine externen Provider-Aktionen wurden hinzugefuegt.
- Die Regel ist lokal und deterministisch.
- Kalender-Write bleibt die bestehende harte Ausnahme mit eigenem Token.
- Kontakt- und Task-Daten bleiben in der lokalen SQLite-Datenbank.

## Tests

Relevante Tests:

- `friday/tests/test_todo_relevance.py`
- `friday/tests/test_message_agent.py`
- `friday/tests/test_repositories.py`
- `friday/tests/test_agent_context_builder.py`
- `friday/tests/test_interface_task_suggestion_review.py`
- `friday/tests/test_interface_combined_review.py`
- `friday/tests/test_review_batch_apply_model.py`
- `friday/tests/test_whatsapp_inbox_store.py`

## Empfehlung fuer naechsten Schritt

Als naechstes sinnvoll: Die Mobile-App per Preview-Update verteilen und auf dem Handy pruefen, ob unbekannte Absender gespeichert werden koennen und danach passende To-do-Vorschlaege entstehen.
