# Gmail IMAP Read-only Gate

## Ziel

Friday kann ein Gmail-Konto ueber IMAP nur lesend in den vereinten lokalen Posteingang einbinden. Die Verbindung nutzt ein Gmail-App-Passwort und speichert Mail-Vorschauen lokal in SQLite.

## Was umgesetzt ist

- Neuer verschluesselter Multi-Account-Store: `friday/app/imap_mail_account_store.py`.
- Neuer Read-only-Reader: `friday/app/imap_mail_reader.py`.
- Neues Aktivierungs-Gate: `friday/app/imap_mail_read_activation_gate.py`.
- Neue API-Endpunkte:
  - `GET /api/accounts/imap-mail/status`
  - `POST /api/accounts/imap-mail/connect`
  - `POST /api/accounts/imap-mail/activation-gate`
  - `POST /api/accounts/imap-mail/sync`
  - `DELETE /api/accounts/imap-mail/{account_id}`
- Vereinter Mail-Endpunkt:
  - `GET /api/messages/mail`
  - `GET /api/messages/mail/{message_id}`
- Mobile Setup-Karte `Gmail (nur lesen)`.

## Ablauf in der App

1. Gmail-App-Passwort bei Google erzeugen.
2. In Friday Mobile unter `Mehr > Einrichten > Gmail (nur lesen)` eintragen.
3. Token `KONTO SPEICHERN` eingeben und `Gmail verbinden` ausfuehren.
4. Token `MAIL LESEN AKTIVIEREN` eingeben und `Gmail-Read-Gate aktivieren` ausfuehren.
5. Friday API neu starten, falls die App darauf hinweist.
6. `Gmail-Sync starten` ausfuehren.

## Safety-Regeln

- Kein SMTP.
- Kein Gmail OAuth.
- Keine Gmail API.
- Kein `Mail.Send`.
- Kein echtes Senden.
- IMAP verwendet `select(..., readonly=True)`.
- Mail-Abruf nutzt `BODY.PEEK[]`, damit keine Nachricht als gelesen markiert wird.
- Das App-Passwort wird lokal verschluesselt gespeichert und nie in API-Antworten ausgegeben.
- `ENABLE_REAL_EMAIL = False` bleibt unveraendert.
- `ENABLE_IMAP_MAIL_READ = False` ist der Default und wird nur ueber das harte Gate aktiviert.

## Tests

- `friday/tests/test_imap_mail_account_store.py`
- `friday/tests/test_imap_mail_reader.py`
- `friday/tests/test_imap_mail_read_activation_gate.py`
- `friday/tests/test_friday_api_imap_mail.py`
- Erweiterungen in Repository- und Scanner-Tests.

## Ergebnis

Gmail-Mails erscheinen zusammen mit Microsoft-Mails im lokalen Posteingang. Die Quelle bleibt pro Nachricht als `imap_mail` oder `ms_mail` unterscheidbar. Spam-/Blockierlogik bleibt lokal und veraendert kein echtes Postfach.
