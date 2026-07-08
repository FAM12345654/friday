# CLI Task Menu Contract Stability Check

## Ziel

Dieser Schritt stabilisiert den sichtbaren Eingabekontrakt des lokalen Aufgabenmenues.

Der Schritt fuehrt keine neue Produktfunktion ein.

## Ausgangslage

Das Aufgabenmenue nutzt absichtlich diese Optionen:

- `1` bis `7`,
- `9` bis `12`.

Die Auswahl `8` ist nicht belegt und bleibt ungueltig.

## Umsetzung

Die Eingabeaufforderung des Aufgabenmenues wurde praezisiert:

```text
Auswahl (1-7, 9-12):
```

Damit passt der sichtbare Prompt zum tatsaechlichen Menuekontrakt.

## Tests

Ergaenzt wurde eine Absicherung in:

`friday/tests/test_menu.py`

Der Test prueft:

- Task-Menueoptionen bleiben unveraendert,
- `show_task_menu()` trimmt Eingaben weiterhin,
- der sichtbare Prompt nennt `1-7, 9-12`.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine echten E-Mails.
- Keine echten WhatsApp- oder SMS-Aktionen.
- Keine Wetter- oder Musikaktionen.
- Keine Netzwerk- oder Provider-Aufrufe.
- Keine Datenbankschema-Aenderung.
- Keine Aenderung an Task-Delete-Policy.
- Safety-Flags bleiben unveraendert.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Produkt- und CLI-Fertigstellung Finalization Gate.
