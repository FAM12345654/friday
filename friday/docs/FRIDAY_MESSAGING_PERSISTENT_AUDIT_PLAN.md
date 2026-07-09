# Friday Messaging Persistent Audit Plan

## Ziel

Dieses Dokument plant, wie Friday spaeter ein lokales Messaging-Audit speichern duerfte.

Aktuell gibt es nur eine Anzeige in der App:

- Entwurf,
- Mock Provider,
- Approval Token,
- Audit Preview.

Dieses Gate baut noch keine Persistenz.

## Nicht-Ziele

- Kein echter Versand.
- Kein Provider.
- Kein OAuth/Login.
- Keine externe Netzwerkaktion fuer Nachrichten.
- Keine Datenbankschema-Aenderung in diesem Schritt.
- Kein dauerhaftes Audit in diesem Schritt.

## Warum ein Audit noetig waere

Wenn Friday spaeter echte E-Mails oder WhatsApp-Nachrichten senden darf, muss lokal nachvollziehbar sein:

- welche Aufgabe weitergeleitet wurde,
- an welchen Kontakt,
- ueber welchen Kanal,
- welches Ziel genutzt wurde,
- welcher Entwurf freigegeben wurde,
- welcher Approval-Token verwendet wurde,
- wann die Aktion stattfand,
- ob es Mock oder Live war.

## Geplantes Datenmodell

Moegliche Tabelle:

```sql
CREATE TABLE messaging_audit_events (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    task_id INTEGER,
    task_title TEXT,
    contact_id INTEGER,
    contact_name TEXT,
    channel TEXT NOT NULL,
    target TEXT,
    draft_text TEXT NOT NULL,
    approval_token TEXT,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    provider TEXT,
    external_message_id TEXT,
    notes TEXT
);
```

## Erlaubte Modi

| Modus | Bedeutung |
|---|---|
| `preview` | Nur Anzeige, keine Speicherung |
| `mock` | Lokale Simulation, kein Versand |
| `live` | Spaeterer echter Versand nach Provider-Gate |

## Statuswerte

| Status | Bedeutung |
|---|---|
| `drafted` | Entwurf erstellt |
| `simulated` | Mock Provider simuliert Versand |
| `approval_rejected` | Token war falsch |
| `approval_accepted` | Token war korrekt, aber noch kein Live-Versand |
| `sent` | Spaeterer echter Versand erfolgreich |
| `failed` | Spaeterer echter Versand fehlgeschlagen |

## Datenschutz-Regeln

- Audit bleibt lokal in SQLite.
- Keine sensiblen Provider-Secrets speichern.
- Keine OAuth-Tokens speichern.
- `draft_text` darf nur gespeichert werden, wenn der Nutzer ein Messaging-Gate akzeptiert hat.
- Kontakt-Ziel darf lokal gespeichert werden, aber spaeter ueber Privacy/Forget-Flows loeschbar sein.
- Audit muss in Datenexport/Privacy-Ansicht sichtbar sein.
- Spaeterer Cleanup braucht ein hartes Token.

## Loeschregeln

Spaetere Optionen:

- Audit nach Kontakt loeschen.
- Audit nach Aufgabe loeschen.
- Audit nach Zeitraum loeschen.
- Alles nur lokal und nur mit hartem Token, z. B.:

```text
MESSAGING AUDIT LOESCHEN
```

## Safety-Bewertung

- Dieses Gate ist Doku-only.
- Es wird nichts gespeichert.
- Es wird nichts gesendet.
- Keine Provider werden aktiviert.
- Keine Datenbankschema-Aenderung.
- Keine Safety-Flags werden geaendert.

## Naechster sinnvoller Build-Step

`Messaging Persistent Audit Preview Model`

Ziel:

- isoliertes Python-Modell fuer Audit-Preview,
- keine DB,
- keine API,
- keine Mobile-Schreibaktion,
- Tests fuer Felder, Statuswerte und Safety.

Status: umgesetzt in `FRIDAY_MESSAGING_PERSISTENT_AUDIT_PREVIEW_MODEL.md`.
