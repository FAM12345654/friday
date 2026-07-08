# Review Activity Status Filter CLI Plan

## Ziel

Dieser Schritt plant die read-only CLI-Anbindung des Review Activity Status Filters.

## Geplante CLI-Option

Im Review-Bereich wird eine read-only Option geplant:

```text
8. Review-Aktivitaet nach Status filtern
```

## Geplanter Ablauf

1. Nutzer waehlt im Review-Bereich `8`.
2. Friday fragt nach einem Statusfilter.
3. Erlaubte Werte sind `all`, `open`, `pending`, `edited`, `approved`, `rejected`, `converted`.
4. Friday zeigt passende lokale Review-Details an.
5. Die Review-Loop bleibt stabil.

## Safety-Bewertung

- CLI-Anbindung bleibt read-only.
- Keine Statusaenderung.
- Keine Schreiboperation.
- Keine externen Aktionen.
- Keine Datenbankschema-Aenderung.

## Empfehlung fuer den naechsten Build Step

Naechster sinnvoller Build Step: Review Activity Status Filter CLI Implementation.
