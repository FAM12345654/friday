# Local Provider Interface Plan 19A

## Ziel

Build Step 19A plant ein spaeteres lokales Provider-Interface fuer Modellfunktionen.

Dieser Schritt ist bewusst nur Planung:
- keine Produktlogik,
- keine echten Modellaufrufe,
- keine Netzwerkaktionen,
- keine Cloud-Provider,
- keine Ollama-Anbindung,
- keine Datenbankschema-Aenderung.

## Ausgangslage

Friday hat bereits einen lokalen Mock-/Preview-Pfad fuer Modell-Readiness.

Der aktuelle Produktfluss nutzt weiterhin keine echten Modelle. Help und Sicherheitsstatus zeigen nur lokale Diagnosehinweise.

## Geplantes Interface

Spaeter soll ein gemeinsames Interface moeglich sein:

```python
class LocalModelProvider:
    def health_check(self) -> ProviderHealth:
        ...

    def generate_json(self, prompt: str, schema: dict) -> ProviderResult:
        ...
```

## Geplante Datenmodelle

| Modell | Zweck |
|---|---|
| `ProviderHealth` | Beschreibt, ob ein Provider lokal erreichbar und nutzbar waere |
| `ProviderResult` | Enthält Antwortdaten, Fehlerstatus, Provider-Name und Safety-Metadaten |
| `ProviderConfig` | Beschreibt Modus, Timeout, Provider-Name und Aktivierungsflags |

## Safety-Regeln

| Regel | Bedeutung |
|---|---|
| Mock bleibt Default | Ohne explizites spaeteres Gate wird nur Mock verwendet |
| Kein Cloud-Fallback | Fehler duerfen nicht still zu Cloud-Providern wechseln |
| Keine Produktanbindung | Provider-Ergebnis darf noch keinen Task/Review/Kontakt automatisch aendern |
| Keine Netzwerkaktion in 19A | Dieser Schritt plant nur |
| Schema-Validierung spaeter | Antworten muessen vor Nutzung validiert werden |
| Nutzerfreigabe bleibt Pflicht | Riskante Aktionen bleiben approval-pflichtig |

## Nicht-Ziele

- Kein Ollama-Adapter.
- Kein OpenAI-/Cloud-Adapter.
- Kein echter HTTP-Call.
- Kein lokaler Modellstart.
- Keine automatische Aufgaben-, Kontakt- oder Review-Entscheidung.
- Keine Persistenz von Prompts oder Antworten.

## Vorgeschlagener Testplan fuer 19B

Wenn 19B umgesetzt wird:
- Mock-Provider liefert deterministische JSON-Daten.
- `health_check()` meldet lokale Mock-Verfuegbarkeit.
- `generate_json()` nutzt keine externen Calls.
- Ergebnis enthaelt `external_call_used=False`.
- Ungueltige/fehlende Schema-Daten werden stabil behandelt.
- Safety-Flags bleiben unveraendert.

## Safety-Bewertung

- Keine externen Aktionen.
- Keine echten Nachrichten.
- Keine echten Kalendertermine.
- Keine Cloud-Provider.
- Keine Netzwerkaktionen.
- Keine Datenbankschema-Aenderung.
- Safety-Flags bleiben unveraendert.
- Delete-Policy bleibt unveraendert.

## Empfehlung fuer Build Step 19B

Build Step 19B sollte ein isoliertes Mock-Provider-Interface bauen:
- neue Python-Datei nur fuer Provider-Abstraktion und Mock,
- keine Produktanbindung,
- keine Netzwerkaufrufe,
- fokussierte Tests fuer Mock-Ergebnis, Health-Check und Safety-Metadaten.
