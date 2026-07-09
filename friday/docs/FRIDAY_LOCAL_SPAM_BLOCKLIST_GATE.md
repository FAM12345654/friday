# Friday Local Spam / Sender Blocklist Gate

## Ziel

Friday kann Nachrichten lokal als Spam markieren und den jeweiligen Absender lokal blockieren.
Das betrifft vor allem synchronisierte Microsoft-Mail-Vorschauen und gespiegelte WhatsApp-Nachrichten.

Wichtig: Friday verändert kein echtes Postfach.

## Verhalten

- `Spam / Absender blockieren` setzt lokal `is_spam = 1`.
- Gleichzeitig wird der Absender in `blocked_senders` gespeichert.
- Standardlisten blenden lokale Spam-Nachrichten aus.
- Spam-Ansichten können mit `include_spam=true` geladen werden.
- Entblocken entfernt den lokalen Blocklisten-Eintrag und macht passende lokale Spam-Vorschauen wieder sichtbar.

## Datenmodell

Additive lokale SQLite-Erweiterungen:

- `messages.is_spam`
- `whatsapp_messages.is_spam`
- `ms_mail_messages.is_spam`
- Tabelle `blocked_senders`

`blocked_senders` speichert:

- `source`: `message`, `ms_mail` oder `whatsapp`
- `sender_key`: normalisierter lokaler Absenderschlüssel
- `label`: lokale Anzeige
- `created_at`: lokaler Zeitstempel

WhatsApp-Schlüssel werden gehasht. Roh-Telefonnummern werden nicht in der Blockliste gespeichert.

## API

- `POST /api/messages/{source}/{message_id}/spam`
- `GET /api/senders/blocked`
- `DELETE /api/senders/blocked/{id}`
- `GET /api/messages?include_spam=true`
- `GET /api/messages/ms-mail?include_spam=true`
- `GET /api/whatsapp/messages?include_spam=true`

Alle Endpunkte bleiben lokale Friday-API-Aktionen.

## Mobile / CLI

Mobile:

- Nachrichtenkarten haben `Spam / Absender blockieren`.
- Der Tab `Spam` zeigt blockierte Absender und lokale Spam-Nachrichten.
- `Entblocken / Wiederherstellen` entfernt den lokalen Block.

CLI:

- Hauptmenüpunkt `Spam / Blockiert` zeigt lokale Blockliste und Spam-Vorschauen.
- Entblocken ist lokal möglich.

## Safety-Bewertung

- Kein `Mail.ReadWrite`.
- Kein echtes Verschieben oder Löschen im Microsoft-/Exchange-Postfach.
- Kein echter WhatsApp-Schreibzugriff.
- Keine neuen Netzwerkziele.
- Keine neuen Pakete.
- `ENABLE_REAL_EMAIL = False` bleibt unverändert.
- Die Sende-Flags bleiben unverändert.
- Microsoft-Mail bleibt `Mail.Read`.
- Tests nutzen lokale `tmp_path`-SQLite und gemockte Provider.

## Rollback

- Lokale Absender im `Spam`-Tab oder CLI-Menü entblocken.
- Optional lokale `is_spam`-Werte in SQLite zurücksetzen.
- Keine Provider-Rollback-Aktion nötig, weil echte Postfächer nie verändert werden.
