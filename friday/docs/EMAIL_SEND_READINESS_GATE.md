# Email Send Readiness Gate

## Ziel

Dieses Gate dokumentiert, dass echter E-Mail-Versand weiterhin nicht freigegeben ist.

Friday 1.0 enthaelt nur:

- lokales Email Draft Model,
- lokalen Email Draft Renderer,
- in-memory CLI-Preview,
- keine Persistenz,
- keinen Provider,
- keinen Versand.

## Aktueller Status

| Bereich | Status |
|---|---|
| E-Mail-Entwurf lokal erstellen | erlaubt |
| E-Mail-Entwurf lokal bearbeiten | erlaubt |
| E-Mail-Entwurf lokal verwerfen | erlaubt |
| E-Mail-Entwurf speichern | nicht freigegeben |
| Provider verbinden | nicht freigegeben |
| Login/OAuth | nicht freigegeben |
| echte E-Mail senden | nicht freigegeben |

## Safety-Flags

```python
ENABLE_REAL_EMAIL = False
REQUIRE_USER_APPROVAL = True
```

Diese Werte bleiben unveraendert.

## Voraussetzungen fuer einen spaeteren Send-Gate

Ein spaeterer echter Send-Step braucht mindestens:

- eigenes Feature-Flag-Gate,
- Secrets-/Credential-Policy,
- Mock Provider vor Real Provider,
- Audit Trail,
- harte Token-Definition,
- Dry Run,
- Full Regression,
- Safety Smoke PASS,
- Nutzer-Doku.

## Blockierte Aktionen

- SMTP,
- Gmail,
- Outlook,
- OAuth,
- externe Kontakte,
- automatische Zustellung,
- Modellantwort direkt senden.

## Ergebnis

Friday ist fuer lokale E-Mail-Entwurfsarbeit bereit.
Friday ist nicht fuer echten E-Mail-Versand freigegeben.

## Empfehlung fuer Post-1.0

Post-1.0 sollte zuerst ein isoliertes Email Mock Provider Model bauen, nicht echten Versand.
