# CLI Task Journey Final Check

## Ziel

Dieser Schritt prueft die lokale Task-Journey vom Hauptmenue ueber Aufgabenaktionen bis zur Rueckkehr und zum Exit.

Der Schritt fuehrt keine neue Produktfunktion ein.

## Gepruefte Task-Pfade

| Bereich | Status |
|---|---|
| Aufgabenmenue vom Hauptmenue oeffnen | abgesichert |
| Aufgabe lokal erstellen | abgesichert |
| Quick Add lokal erstellen | abgesichert |
| Aufgabe bearbeiten | abgesichert |
| Aufgabe suchen und filtern | abgesichert |
| Aufgabe als erledigt markieren | abgesichert |
| Aufgabe archivieren | abgesichert |
| Aufgaben lokal als Markdown exportieren | abgesichert |
| Aufgabe loeschen mit bestehender Delete-Policy | abgesichert |
| Rueckkehr ins Hauptmenue | abgesichert |
| Exit aus der Hauptschleife | abgesichert |

## Wichtige Journey-Tests

- Vollstaendige lokale Task-Journey: erstellen, suchen und erledigen.
- Aufgabenmenue oeffnen, zurueckkehren, Hilfe anzeigen und beenden.
- Quick Add, Markdown-Export und Tagesplan-Vorschau.
- Delete-Policy:
  - `ja` loescht nicht,
  - `JA` loescht,
  - leere oder ungueltige IDs loeschen nicht.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine echten E-Mails.
- Keine echten WhatsApp- oder SMS-Aktionen.
- Keine Wetter- oder Musikaktionen.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Task-Delete-Policy bleibt unveraendert.
- Safety-Flags bleiben unveraendert.

## Tests

Relevante Testbereiche:

- `friday/tests/test_task_interface_flow.py`
- `friday/tests/test_interface_main_menu_e2e.py`
- `friday/tests/test_task_agent.py`
- `friday/tests/test_task_repository.py`
- vollstaendige Suite `friday/tests`

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Exit- und Ruecksprungpfade final pruefen.
