# CLI Onboarding Text 12T

## Ziel

Nach einem stabilen Help- und Review-Bereich wurde der erste Einstiegspunkt für neue Nutzer:innen noch klarer gemacht.

`Friday` zeigt jetzt beim Start einen sichtbaren Onboarding-Hinweis direkt im Dashboard, damit sofort erkennbar ist:

- die CLI läuft lokal,
- welche Hauptbereiche im Menü vorhanden sind,
- dass Aktionen lokal bleiben.

## Geänderte Ausgabe

In `friday/app/interface.py` wurde im Dashboard der Startpfad ergänzt:

- `Start-Hinweis`-Abschnitt
- Begrüßungstext `Willkommen bei Friday (lokale CLI).`
- kurzer Hinweis auf verfügbare Arbeitsbereiche
- Sicherheitshinweis (keine echten Nachrichten, keine echten Termine)

## Abgesicherte Verhaltensweisen

- Dashboard zeigt den Onboarding-Hinweis auf dem Start.
- Die Hinweiszeile erscheint beim `run()`-Start genau einmal.
- Der Hinweis wird nicht als eigene Aktion im Menü verändert.

### Relevante Tests

- `friday/tests/test_interface_main_menu_e2e.py`
  - `test_show_dashboard_includes_local_onboarding_note`
  - `test_run_shows_onboarding_note_once_on_startup`

## Safety-Bewertung

- Keine Produktionslogik verändert.
- Keine neuen externen Aktionen.
- Der Onboarding-Text beschreibt die bestehende lokale Einschränkung.
- Delete-Policy unverändert (`ja` löscht nicht, `JA` löscht).

## Empfehlung für Build Step 12U

- Weiter mit gezielter CLI-Benutzerführung: optional `12U` als kleinen Leittext für häufige Startpfade, falls gewünscht.
