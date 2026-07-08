# Local Provider Mock Interface 19B

## Ziel

Build Step 19B ergänzt ein isoliertes lokales Provider-Interface mit einem deterministischen Mock-Provider.

Der Mock ist nur eine lokale technische Vorbereitung:
- keine echten Modellaufrufe,
- keine Netzwerkaktionen,
- keine Cloud-Provider,
- keine Produktanbindung,
- keine Datenbankschema-Aenderung.

## Umgesetzte Datei

| Datei | Zweck |
|---|---|
| `friday/app/local_model_provider.py` | Provider-Datenmodelle, Interface-Basis und Mock-Provider |
| `friday/tests/test_local_model_provider.py` | Tests fuer Health-Check, JSON-Ergebnis und Safety-Metadaten |

## Datenmodelle

| Modell | Zweck |
|---|---|
| `ProviderConfig` | Beschreibt Provider, Modell, Modus und externe Aktivierung |
| `ProviderHealth` | Beschreibt lokale Verfuegbarkeit und Safety-Status |
| `ProviderResult` | Strukturiertes Ergebnis mit Output, Schema und Safety-Metadaten |

## Mock-Provider

`MockLocalModelProvider` liefert deterministische Daten:
- `provider = "mock"`
- `model = "mock-local-json"`
- `external_call_used = False`
- `product_flow_connected = False`
- `is_mock = True`

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Provider-/Cloud-Aufrufe.
- Kein Netzwerk.
- Keine Produktlogik-Anbindung.
- Safety-Flags bleiben lokal-only.
- Delete-Policy bleibt unveraendert.

## Tests

- `python -m pytest friday/tests/test_local_model_provider.py`
- `python -m pytest friday/tests`

## Empfehlung fuer Build Step 19C

Build Step 19C sollte nur eine Ollama Local Adapter Preview planen oder vorbereiten.

Wichtig:
- kein Live-Zwang,
- kein Cloud-Fallback,
- Adapter nur hinter explizitem Flag,
- Tests mit Fake/Mock, nicht mit echtem laufendem Ollama.
