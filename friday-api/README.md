# Friday API

## Start

```bash
cd friday-api
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Wichtige Settings

- `FRIDAY_CORS_ORIGINS` (Komma-getrennte Liste) für Mobile/Desktop-Clients.
- `FRIDAY_API_PORT` / `FRIDAY_API_HOST` werden optional vom Desktop-Launcher genutzt.

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
- `GET /api/calendar`, `GET /api/calendar/{message_id}/slots`
- `GET /api/contacts`
- `GET /api/privacy`
