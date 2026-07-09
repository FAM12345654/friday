# Friday AI Task Forwarding Draft

## Ziel

Friday ist jetzt fuer den Aufgaben-Weiterleiten-Flow an die lokale KI-Provider-Schicht angebunden.
Der Flow erstellt nur einen sichtbaren lokalen Entwurf und sendet keine echte Nachricht.

## Umgesetzter Umfang

- Neuer Draft-Baustein: `friday/app/ai_task_forwarding_draft.py`.
- Neuer API-Endpunkt: `POST /api/ai/task-forward-draft`.
- Mobile Weiterleiten-Flow nutzt den API-Endpunkt nach Kontakt- und Kanal-Auswahl.
- Standard bleibt der lokale Mock-Provider.
- Optional kann spaeter ein lokaler Ollama-Provider genutzt werden, wenn `ENABLE_LOCAL_OLLAMA=True`, ein Modell gesetzt ist und der localhost-Guard greift.

## Bewusst nicht umgesetzt

- Kein echter E-Mail-Versand.
- Kein echter WhatsApp-Versand.
- Kein Cloud-Modell.
- Kein API-Key.
- Kein Login/OAuth.
- Keine Audit-Persistenz.
- Keine automatische Aktion aus Modellantworten.

## Safety

- `ENABLE_REAL_EMAIL = False`
- `ENABLE_REAL_WHATSAPP = False`
- `ENABLE_REAL_SMS = False`
- `ENABLE_REAL_CALENDAR = False`
- `ENABLE_REAL_WEATHER = False`
- `ENABLE_REAL_MUSIC = False`
- `REQUIRE_USER_APPROVAL = True`
- `USE_SQLITE_STORAGE = True`

Der Draft zeigt weiterhin harte Tokens fuer spaetere Gates:

- `EMAIL SENDEN`
- `WHATSAPP SENDEN`

Diese Tokens loesen aktuell keinen echten Versand aus.

## Tests

- `friday/tests/test_ai_task_forwarding_draft.py`
- Full Regression: `python -m pytest friday/tests`
- Safety Smoke: `python scripts/friday_safety_smoke.py`

## Naechster sinnvoller Schritt

Messaging Persistent Audit Repository Plan: planen, wie akzeptierte Mock-/Draft-Freigaben spaeter lokal protokolliert werden.

Status danach: Das lokale Ollama Activation Gate ist in `FRIDAY_LOCAL_OLLAMA_ACTIVATION_GATE.md` dokumentiert.
