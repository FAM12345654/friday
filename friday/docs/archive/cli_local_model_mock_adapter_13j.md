# Local Model Mock Adapter 13J

## Ziel

Dieser Schritt ergänzt einen kleinen lokalen, produktionsfreien Adapter für spätere Modell-Integration:
ein deterministischer Mock, der nur lokale, kontrollierte Ergebnisse liefert.

## Scope

- Kein echter Modell-Call.
- Keine Provider-/Netzwerkaufrufe.
- Keine API-Keys oder externen Environment-Aktionen.
- Kein automatischer Eingriff in Task-/Message-/Review-Flows.
- Der Adapter ist isoliert, testbar und lokal-first.

## Implementierung

Neue Datei:

- `friday/app/local_model_mock.py`

Wichtige Bestandteile:

- `LocalModelMockAdapter`
  - `provider`: `"mock-local"`
  - `model`: `"mock-readiness"`
- `LocalModelMockResult`
  - deterministische Felder inklusive `is_mock` und `external_call_used`
- `LocalModelReadinessStatus`
  - `mode_supported`
  - `provider_config_present`
  - `approval_flow_available`
  - `safety_flags_locked`
  - `fallback_path_defined`
  - `fallback_status` (`"local_rule_based"`)

Verhalten:

- `generate("Hallo")` -> deterministische Mock-Antwort mit `external_call_used == False`
- `generate("   ")` -> leeres `prompt`-Feld, ebenfalls `is_mock == True`
- `get_readiness_status()` -> lokaler Readiness-Pfad ohne Seitenwirkungen

## Safety-Bewertung

- Keine externen Aktionen.
- Keine externen Nachrichten, kein WhatsApp, keine SMS.
- Keine echten Kalendertermine.
- Keine Wetter-/Musik-Aktionen.
- Safety-Flags bleiben unverändert lokal-first:
  - `ENABLE_REAL_EMAIL = False`
  - `ENABLE_REAL_WHATSAPP = False`
  - `ENABLE_REAL_SMS = False`
  - `ENABLE_REAL_CALENDAR = False`
  - `ENABLE_REAL_WEATHER = False`
  - `ENABLE_REAL_MUSIC = False`
  - `REQUIRE_USER_APPROVAL = True`
  - `USE_SQLITE_STORAGE = True`
- Delete-Policy bleibt unverändert:
  - `"ja"` löscht nicht.
  - `"JA"` löscht.
  - `" JA "` bleibt durch `strip()` erlaubt.

## Tests

- `friday/tests/test_local_model_mock_adapter.py`
  - Verfügbarkeit
  - deterministische Mock-Response
  - leere Eingabe
  - lokale Readiness-Flags

Zusatz:

- `python -m pytest friday/tests`
- `python -m compileall friday`
- `git diff --check`

## Empfehlung für Build Step 13K

Build Step 13K: `Local Model Mock Integration Preview`

- Nutzung des Mock-Adapters nur in einem isolierten Vorschau-Pfad
- kein Produktfluss verbunden
- weiterhin vollständig lokal und ohne echte Modellaufrufe
