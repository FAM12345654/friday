# Email Mock Provider Plan

## Ziel

Dieses Dokument plant eine spaetere Mock-Provider-Schicht fuer lokale E-Mail-Entwuerfe.

Der aktuelle Stand bleibt Draft-only:

- kein SMTP,
- kein Gmail,
- kein Outlook,
- kein OAuth,
- keine Secrets,
- kein Netzwerk,
- kein echter Versand.

## Geplanter Mock-Zweck

Ein spaeterer Mock Provider darf nur pruefen, ob ein lokaler Entwurf theoretisch provider-kompatibel waere.

Er darf nicht:

- echte Provider verbinden,
- Login starten,
- Credentials lesen,
- Nachrichten senden,
- externe Kontakte abrufen.

## Vorgeschlagene Schnittstelle

```text
EmailMockProvider.preview_delivery(draft) -> EmailMockProviderPreview
```

Geplante Rueckgabe:

| Feld | Bedeutung |
|---|---|
| `provider_name` | immer `mock` |
| `would_send` | immer `False` |
| `external_call_used` | immer `False` |
| `requires_real_provider` | immer `False` |
| `blocked_reasons` | Safety-/Validierungsgruende |

## Safety-Regeln

- Mock ist Default fuer jede spaetere Provider-Abstraktion.
- Real Provider duerfen erst nach eigenem Gate existieren.
- Kein Cloud-Fallback.
- Keine Credentials im Modell.
- Kein Versandstatus.

## Tests fuer spaetere Umsetzung

- Mock erzeugt nur Preview.
- Mock setzt `would_send = False`.
- Mock setzt `external_call_used = False`.
- Draft mit blockiertem Status bleibt blockiert.
- Kein Netzwerkimport und kein Providerimport.

## Empfehlung fuer den naechsten Build Step

Naechster technischer Schritt nach Friday 1.0: isoliertes Mock-Provider-Modell bauen, weiterhin ohne Real Provider.
