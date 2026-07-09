# Friday PH-Zeitfenster und Agent-Notizen Gate

## Ziel

Dieses Gate dokumentiert zwei lokale Erweiterungen:

- PH-Termine aus der Outlook-ICS-Quelle `team-hampejs` werden lokal als Tagesblock `08:00` bis `18:00` angezeigt.
- Agent-Notizen koennen lokal fuer E-Mail, WhatsApp, Kontakte und Account-Policies gespeichert und fuer lokale KI-Entwuerfe genutzt werden.

## PH-Zeitfenster

Die PH-Zeitlogik ist bewusst deterministisch in Python umgesetzt.
Sie ist kein globaler Kalender-Hack, sondern ein per-Policy-Transform:

```json
{
  "fixed_daily_window": {
    "start": "08:00",
    "end": "18:00"
  }
}
```

Gilt nur, wenn:

- die Account-Policy `provider = "outlook_ics"` nutzt,
- die Policy den Transform enthaelt,
- der Termin nach den bestehenden Filtern weiterhin sichtbar ist.

Andere Google-, Outlook-Graph- oder lokale Kalendertermine werden dadurch nicht veraendert.

## Agent-Notizen

Agent-Notizen sind lokale, nutzereditierbare Kontextnotizen fuer Friday.
Sie duerfen in lokale KI-Drafts einfliessen, werden aber nicht extern versendet.

Unterstuetzte Bereiche:

| Bereich | Speicherort / Weg | Nutzung |
|---|---|---|
| E-Mail-Konto | lokaler Account-Store | Stil-/Kontext fuer E-Mail-Drafts |
| WhatsApp | `local_data/whatsapp/agent_notes.json` | Stil-/Kontext fuer WhatsApp-Drafts |
| Kontakt | lokale Kontakt-Tabelle | Personenbezogener Kontext fuer Weiterleiten-Drafts |
| Account-Policy | lokale `account_policies` | Kalender-/Account-Kontext fuer lokale Agenten |

## Mobile/API-Anbindung

Ergaenzt wurden lokale Endpunkte und Mobile-Felder fuer:

- Kontakt-Notizen bearbeiten,
- E-Mail-Agent-Notiz speichern,
- WhatsApp-Agent-Notiz speichern,
- Outlook-ICS-PH-Zeitfenster in Account-Policies speichern.

## Safety-Bewertung

- Keine neuen externen Aktionen.
- Kein automatischer E-Mail- oder WhatsApp-Versand.
- Keine Cloud-KI.
- Agent-Notizen werden nicht geloggt und nicht an Provider gesendet.
- PH-Zeitfenster ist rein lokaler Transform.
- Keine Aenderung an den Safety-Flags.
- Kalender-Write bleibt weiterhin pro Termin hart gegatet.

## Tests

Abgesichert durch Fokus-Tests fuer:

- `account_policy_engine.apply_transforms`,
- Account-Policy-Transform-Persistenz,
- lokale Agent-Kontext-Erstellung,
- E-Mail-Agent-Notizen,
- WhatsApp-Agent-Notizen,
- KI-Weiterleiten-Draft mit lokalem Agent-Kontext,
- API-Endpunkte fuer Policy-Transform, Kontakt-Notizen und Agent-Notizen.

## Empfehlung

Naechster sinnvoller Schritt: Agent-Notizen in der UI noch feiner trennen nach "Stilhinweis" und "private Notiz", bevor weitere echte Messaging-Aktionen freigegeben werden.
