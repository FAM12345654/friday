# Friday Gmail Cleanup Gate

## Ziel

Friday kann den Gmail-Posteingang lokal aufraeumen, aber nur fuer offensichtliche, deterministische Noise-Mails.

## Sicherheitsmodell

- Aktivierung nur mit `POSTFACH AUFRAEUMEN`.
- Standard-Flag bleibt `ENABLE_MAIL_ORGANIZE = False`.
- `ENABLE_REAL_EMAIL = False` bleibt unveraendert.
- Es wird nichts gesendet.
- Es wird nichts geloescht.
- Es wird kein `EXPUNGE` verwendet.
- Gmail-Mails werden nur reversibel aus `INBOX` nach `Friday/Aussortiert` verschoben.
- Rueckgaengig machen stellt das `INBOX`-Label wieder her.

## Auswahlregeln

Ausgewaehlt werden nur:

- lokal blockierte Gmail-Absender,
- klare Newsletter-/Marketing-/Noreply-/Social-Noise-Signale wie Instagram oder LinkedIn.

Nicht ausgewaehlt werden:

- bekannte Kontakte,
- Kunden,
- unsichere oder KI-geratene Faelle,
- Microsoft-/Outlook-Mails,
- Kalender-, Task- oder Kontakt-Daten.

## Audit

Jede verschobene Mail wird in `mailbox_cleanup_log` protokolliert:

- Konto,
- Provider-Message-ID,
- Absender,
- Betreff,
- Ziel-Label,
- Zeitpunkt,
- Rueckgaengig-Status.

## API

- `POST /api/mail/organize/activation-gate`
- `POST /api/mail/organize/run`
- `GET /api/mail/organize/log`
- `POST /api/mail/organize/undo/{log_id}`

## Mobile

Im Setup-Bereich gibt es die Karte `Posteingang aufraeumen (Gmail)` mit Aktivierung, manuellem Lauf, Log und Undo.
