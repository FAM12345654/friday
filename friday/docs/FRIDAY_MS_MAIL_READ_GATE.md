# Friday Microsoft Mail Read Gate

## Ziel

Dieses Gate aktiviert einen read-only Microsoft-Graph-Mail-Pfad fuer mehrere Familienhelden-Postfaecher. Friday darf damit Mails lesen und lokal als Vorschau synchronisieren, aber keine E-Mails senden.

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

`ENABLE_MS_MAIL_READ` ist ein nutzer-aktivierbarer Read-Flag. Er wird nicht mehr vom Safety-Flag-Baseline-Scanner auf `False` erzwungen, damit eine spaetere bewusste Aktivierung den Safety Smoke nicht bricht. Die Sende-Flags bleiben weiterhin hart erzwungen.

Aktivierung ist nur erlaubt, wenn alle Punkte erfuellt sind:

- Mindestens ein Microsoft OAuth-Konto wurde verbunden.
- Mindestens ein Konto hat einen erfolgreichen Test-Read gegen Graph.
- Scanner Smoke ist erfolgreich.
- Nutzer gibt exakt `MAIL LESEN AKTIVIEREN` ein.
- `ENABLE_REAL_EMAIL` bleibt `False`.

## Multi-Account Speicherung

Token werden verschluesselt pro Konto unter `local_data/accounts/ms_mail_accounts/<account_id>.json` gespeichert. Die Dateien liegen unter `local_data/` und sind gitignoriert.

Jedes Konto enthaelt tokenfreie Metadaten:

- `account_id`
- `username`
- `tenant`
- `connected_at`
- `last_test_ok`
- `encryption_method`

### Legacy-Migration

Das alte Einzelkonto unter `local_data/accounts/ms_mail_account.json` bleibt erhalten. Beim ersten Status-/Ladevorgang kopiert Friday dieses Konto idempotent in den neuen Multi-Account-Store. Dadurch geht das bereits verbundene `office@...`-Postfach nicht verloren.

## Lokale Mail-Vorschauen

Mail-Vorschauen werden lokal in `ms_mail_messages` gespeichert:

- `account_id`
- `account_username`
- `message_id` (lokal eindeutig, bei Multi-Account mit Konto-Prefix)
- `provider_message_id` (originale Graph Message-ID)
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
- `POST /api/accounts/ms-mail/sync` mit optionalem `account_id`
- `DELETE /api/accounts/ms-mail/{account_id}`
- `GET /api/messages/ms-mail?limit=10`
- `GET /api/messages/ms-mail?limit=10&account_id=<account_id>`

`/sync` gibt `403` zurueck, solange `ENABLE_MS_MAIL_READ = False` ist.

## Mobile/CLI Anzeige

Die Mobile-App zeigt:

- Liste der verbundenen Microsoft-Postfaecher,
- Sync fuer alle Konten,
- Sync fuer ein einzelnes Konto,
- Trennen eines einzelnen Kontos mit `KONTO LOESCHEN`,
- Read-only-Hinweis pro Bereich.

Die CLI-Sicherheitsansicht zeigt die Anzahl der Microsoft-Mail-Postfaecher und deren maskierten Status.

## Agenten-Anbindung

Synchronisierte Mails aller Konten werden lokal als Nachrichtenquelle `ms_mail` sichtbar. Friday verwendet Betreff plus Vorschau fuer:

- Termin-Vorschlaege im Review,
- Aufgaben-Vorschlaege nur nach `is_relevant_for_user(text, sender_contact)`,
- Kontakt-Zuordnung fuer unbekannte Absender,
- konto-spezifische Anzeige ueber `account_id` und `account_username`.

Es gibt keinen Auto-Reply und keinen Versand.

## Rollback

- `ENABLE_MS_MAIL_READ = False` setzen.
- Friday API neu starten.
- Einzelnes Konto mit `KONTO LOESCHEN` ueber `DELETE /api/accounts/ms-mail/{account_id}` entfernen.
- Optional lokale `ms_mail_messages`-Eintraege aus der SQLite-DB loeschen.

## Safety-Bewertung

- Kein `Mail.Send`.
- `ENABLE_REAL_EMAIL = False` bleibt unveraendert.
- Netzwerkzugriff nur in `friday/app/ms_mail_provider.py`.
- Scanner-Allowlist bleibt eng auf das Provider-Modul begrenzt.
- Tests mocken OAuth und Graph komplett.
- Tokens/Secrets werden nicht in Status, Tests oder Doku ausgegeben.

## Volle Mail-Inhalte und KI-Relevanz

- Microsoft Graph bleibt read-only mit `Mail.Read`.
- Friday holt zusaetzlich den vollen Mail-Body, Empfaenger und CC aus demselben Read-Call.
- Volltexte werden lokal in SQLite gespeichert (`ms_mail_messages.body_full`) und nicht ins Git geschrieben.
- Fuer `office@familienhelden.at` entscheidet Friday zuerst deterministisch. Wenn der Fall unklar ist, prueft die lokale KI den vollen Body. Bei KI-Fehlern wird konservativ sichtbar markiert.
- Die mobile App laedt den Volltext erst in der Mail-Detailansicht. Listen bleiben Vorschauen.
- Es gibt weiterhin keinen Mail-Versand und keine Schreibrechte.

## Mail-Fix: Token-Refresh, Relevanz, Tempo

- Beim Microsoft-Mail-Sync versucht Friday ein gespeichertes `refresh_token` zu nutzen und speichert das aktualisierte Token-Bundle wieder lokal verschluesselt.
- Wenn Refresh fehlschlaegt, wird das betroffene Konto im Sync-Ergebnis als `reconnect_required` markiert. Friday ruft dann Graph fuer dieses Konto nicht auf.
- Die Scopes bleiben read-only: `Mail.Read` und `User.Read`. Es wird kein `Mail.Send` hinzugefuegt.
- Das geteilte `office@familienhelden.at`-Postfach wird zuerst deterministisch bewertet:
  - Philip/Phips/Zeitler in Empfaenger, Betreff, Absender oder Inhalt,
  - Philip, Alex und Flo gemeinsam,
  - bekannter Kunde mit Betreuer `philip`.
- Social-/Newsletter-Rauschen wie Instagram, LinkedIn, `noreply`, Newsletter, Mailer-Daemon und Marketing bleibt lokal ausgeblendet.
- Unsichere Office-Mails bleiben sichtbar mit Grund `unsicher`.
- Die lokale KI wird im normalen Sync nicht pro Mail blockierend aufgerufen. Sie kann weiterhin in Tests oder explizit injizierten Pruefpfaden als zweite Meinung genutzt werden.
