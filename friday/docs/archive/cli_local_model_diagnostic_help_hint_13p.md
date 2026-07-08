# Local Model Diagnostic Help Hint 13P

## Ziel

Kleiner lokaler Produkt- Schritt: ein kurzer Hinweis in der bestehenden Hilfe / Übersicht ergänzt einen direkten Verweis auf den lokalen Modell-Diagnosemodus.

## Implementierte Änderung

- `friday/app/interface.py::_show_help_overview()` ergänzt die Zeile:
  - `Lokale Modell-Diagnose: siehe Sicherheitsstatus. Es werden keine externen Modellaufrufe genutzt.`

## Umfang

- Es wurde **keine** neue Menüoption hinzugefügt.
- Es wurden keine Modell-Adapter aufgerufen.
- Es wurde kein Provider, keine API-Keys und kein Netzwerkzugriff ergänzt.
- Keine Task-/Message-/Review-Logik wurde verändert.

## Testabdeckung

- `friday/tests/test_interface_main_menu_e2e.py::test_handle_menu_choice_help_overview`
  - prüft den neuen Hinweis in der Help-Ausgabe

## Safety-Bewertung

- Keine echten Modellaufrufe.
- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Safety-Flags unverändert.
- Delete-Policy unverändert:
  - `"ja"` löscht nicht
  - `"JA"` löscht
  - `" JA "` bleibt durch `strip()` erlaubt

## Nächster Schritt

Build Step 13Q (Local Model Diagnostic Documentation Integration) ist als sinnvolle nächster Schritt vorgesehen.
