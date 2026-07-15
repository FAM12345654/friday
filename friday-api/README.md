# Friday API

## Start

```bash
python -m pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Start-Friday-API-Autostart.ps1 -Port 8001
```

Der Launcher bindet ausschließlich an `127.0.0.1:8001` und verlangt einen
starken `FRIDAY_API_TOKEN`. Geräte verwenden Tailscale Serve per HTTPS.

## Wichtige Settings

- `FRIDAY_CORS_ORIGINS` (Komma-getrennte Liste) für Web-/Desktop-Origins.
- `FRIDAY_API_TOKEN` ist für jeden LAN-, Docker-, Tailscale- oder
  Tunnel-Zugriff erforderlich. Ohne Token werden nur direkte
  Loopback-Anfragen akzeptiert.
- `FRIDAY_API_PORT` / `FRIDAY_API_HOST` werden optional vom Desktop-Launcher genutzt.
- `FRIDAY_OAUTH_LEDGER_SECRET` ist ein optionales separates Secret mit
  mindestens 32 Zeichen für die verschlüsselten, kurzlebigen OAuth-Flows. Ohne
  DPAPI wird andernfalls der starke `FRIDAY_API_TOKEN` als Schlüsselquelle
  verwendet.

## API-Vereinheitlicher JSON-Vertrag

Alle Endpunkte antworten mit:

```json
{
  "ok": true,
  "data": { ... }
}
```

## Zentrale Endpunkte

- `GET /health`
- `GET /api/dashboard`
- `GET /api/tasks`, `GET /api/tasks/{id}`, `POST /api/tasks`, `PATCH /api/tasks/{id}`, `DELETE /api/tasks/{id}`
- `POST /api/tasks/{id}/done`, `POST /api/tasks/{id}/archive`
- `GET /api/messages`, `GET /api/messages/{id}`, `GET /api/messages/{id}/reply`, `GET /api/messages/suggestions`
- `POST /api/tasks/{id}/snooze` (`{"until": "YYYY-MM-DD"}`), `POST /api/tasks/{id}/unsnooze`
- `GET /api/calendar`, `GET /api/calendar/{message_id}/slots`
- `GET /api/contacts`
- `GET /api/privacy`
- `GET /metrics` — Cache-Trefferquote und Latenz/Fehler pro Endpunkt
- `GET /api/search?q=...` — lokale Suche über Aufgaben, Kontakte, Nachrichten, WhatsApp und Mail
- `GET /api/mail/followups?days=3` — gesendete Mails ohne Antwort
- `GET /api/events` — Server-Sent Events; feuert `change`-Events (dashboard/mail/calendar) bei Datenänderungen
- `GET /api/search/semantic?q=...`, `POST /api/search/semantic/reindex`,
  `GET /api/search/semantic/status` — semantische Suche über lokale
  Ollama-Embeddings (`OLLAMA_EMBED_MODEL`, nur localhost)
- `POST /api/push/register`, `DELETE /api/push/register`, `GET /api/push/status`,
  `POST /api/push/send-due-reminders` — Expo-Push-Erinnerungen (extern, nur aktiv
  wenn `ENABLE_PUSH_NOTIFICATIONS = True` in `friday/config.py`)
- `POST /api/voice/transcribe` (Audio-Upload → Text, lokales faster-whisper),
  `POST /api/voice/speak` (Text → WAV über lokalen Orpheus/Kokoro-Server),
  `POST /api/voice/command` und `POST /api/voice/command-audio`
  (Sprachbefehl → Intent → Agenten → optional gesprochene Antwort),
  `GET /api/voice/morning-briefing?speak=true`, `GET /api/voice/status`
  — Setup siehe SETUP.md Abschnitt 7

## Performance-Integration

`perf.py` stellt die gemeinsam genutzten Performance-Helfer bereit:

- `register_timing(app)` loggt pro Request Endpoint, Methode, Status und Dauer und setzt `Server-Timing`.
- `TTLCache(ttl=120)` cached kurzlebige Read-Payloads mit Single-Flight pro Cache-Key.
- `etag_response(...)` setzt `ETag`, `Cache-Control` und liefert bei `If-None-Match` HTTP `304`.

Geaenderte GET-Endpunkte:

- `GET /api/dashboard`: Dashboard-Payload mit 120s TTL und ETag.
- `GET /api/tasks`: ETag/304 fuer die Aufgabenliste.
- `GET /api/calendar`: Gesamtpayload mit 120s TTL und ETag; externe Kalenderquellen werden parallel gelesen.
- `GET /api/accounts/calendar/google/read-preview`: Google-Calendar-Read mit 120s TTL und ETag.
- `GET /api/messages/ms-mail`: Mail-Listenpayload mit 120s TTL und ETag.
- `GET /api/messages/mail`: Unified-Mail-Listenpayload mit 120s TTL und ETag.
- `GET /api/messages/email-inbox`: IMAP-Inbox-Preview mit 120s TTL und ETag.

Parallelisierte Fetch-Funktionen:

- `_collect_source_calendar_events(...)` liest aktive Google- und Outlook-ICS-Policies parallel.
- `sync_ms_mail_messages(...)` liest Microsoft-Graph-Konten parallel und schreibt danach sequentiell in SQLite.
- `sync_imap_mail_messages(...)` liest IMAP-Konten parallel und schreibt danach sequentiell in SQLite.

Gefundene blockierende Datenquellen:

- `GoogleCalendarProvider.list_events(...)`: `google-api-python-client`, blockierend, via `asyncio.to_thread`.
- `OutlookIcsCalendarProvider.list_events(...)`: `urllib` + ICS-Parsing, blockierend, via `asyncio.to_thread`.
- `list_ms_mail_messages(...)`: Microsoft Graph ueber `urllib`, blockierend, via `asyncio.to_thread`.
- `read_imap_mail_messages(...)` und `read_recent_inbox_emails(...)`: `imaplib`, blockierend, via `asyncio.to_thread`.

Gefundene echte Coroutines:

- Die FastAPI-Handler fuer Dashboard, Calendar, Mail-Reads und Mail-Sync sind async.
- Die externen Provider selbst sind keine echten async-Coroutines.

Erwartete Wirkung:

- Mehrere externe Kalender-Policies oder Mail-Konten warten nicht mehr sequentiell aufeinander.
- Wiederholte Dashboard-, Google-Calendar- und Mail-Reads innerhalb von 120 Sekunden vermeiden doppelte Provider-/DB-Arbeit.
- Clients mit ETag-Unterstuetzung sparen Response-Body-Transfer ueber HTTP `304`.
