# Friday Microsoft Mail Read Gate

## Ziel

Dieses Gate aktiviert einen read-only Microsoft-Graph-Mail-Pfad fuer das Familienhelden-Postfach. Friday darf damit Mails lesen und lokal als Vorschau synchronisieren, aber keine E-Mails senden.

## Scope

Erlaubte Microsoft Graph Delegated Scopes:

- `Mail.Read`
- `offline_access`
- `User.Read`

Ausgeschlossen:

- `Mail.Send`
- Kalender-Schreibrechte ueber diesen Pfad
- automatische Antworten
- automatische externe Aktionen

## Aktivierungsmodell

Default in `friday/config.py`:

```python
ENABLE_MS_MAIL_READ = False
ENABLE_REAL_EMAIL = False
```

Aktivierung ist nur erlaubt, wenn alle Punkte erfuellt sind:

- Microsoft OAuth-Konto wurde verbunden.
- Test-Read gegen Graph war erfolgreich.
- Scanner Smoke ist erfolgreich.
- Nutzer gibt exakt `MAIL LESEN AKTIVIEREN` ein.
- `ENABLE_REAL_EMAIL` bleibt `False`.

## Lokale Speicherung

Token werden verschluesselt unter `local_data/accounts/ms_mail_account.json` gespeichert. Die Datei liegt unter `local_data/` und ist gitignoriert.

Mail-Vorschauen werden lokal in `ms_mail_messages` gespeichert:

- `message_id`
- `sender`
- `subject`
- `received_at`
- `snippet`
- `processed`
- `suggestion_created`

Vollstaendige Mail-Bodies werden nicht gespeichert.

## API-Endpunkte

- `POST /api/accounts/ms-mail/connect`
- `GET /api/accounts/ms-mail/status`
- `POST /api/accounts/ms-mail/activation-gate`
- `POST /api/accounts/ms-mail/sync`
- `DELETE /api/accounts/ms-mail`
- `GET /api/messages/ms-mail?limit=10`

`/sync` gibt `403` zurueck, solange `ENABLE_MS_MAIL_READ = False` ist.

## Agenten-Anbindung

Synchronisierte Mails werden lokal als Nachrichtenquelle `ms_mail` sichtbar. Friday verwendet Betreff plus Vorschau fuer:

- Termin-Vorschlaege im Review
- Aufgaben-Vorschlaege nur nach `is_relevant_for_user(text, sender_contact)`
- Kontakt-Zuordnung fuer unbekannte Absender

Es gibt keinen Auto-Reply und keinen Versand.

## Rollback

- `ENABLE_MS_MAIL_READ = False` setzen.
- Friday API neu starten.
- Konto mit `KONTO LOESCHEN` entfernen.
- Optional lokale `ms_mail_messages`-Eintraege aus der SQLite-DB loeschen.

## Safety-Bewertung

- Kein `Mail.Send`.
- `ENABLE_REAL_EMAIL = False` bleibt unveraendert.
- Netzwerkzugriff nur in `friday/app/ms_mail_provider.py`.
- Scanner-Allowlist ist eng auf das Provider-Modul begrenzt.
- Tests mocken OAuth und Graph komplett.
