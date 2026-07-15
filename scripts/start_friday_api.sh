#!/usr/bin/env bash
# Start the Friday API (cross-platform equivalent of start_friday_api.bat).
set -euo pipefail
cd "$(dirname "$0")/../friday-api"

python3 -m pip install -r requirements.txt
FRIDAY_API_HOST="${FRIDAY_API_HOST:-127.0.0.1}"
FRIDAY_API_PORT="${FRIDAY_API_PORT:-8001}"
FRIDAY_API_TOKEN="${FRIDAY_API_TOKEN:-}"
if [[ "$FRIDAY_API_HOST" != "127.0.0.1" && "$FRIDAY_API_HOST" != "localhost" && ${#FRIDAY_API_TOKEN} -lt 32 ]]; then
  echo "FEHLER: FRIDAY_API_TOKEN muss fuer LAN- oder Tunnel-Zugriff mindestens 32 Zeichen haben." >&2
  exit 1
fi
echo
echo "Starte Friday API auf ${FRIDAY_API_HOST}:${FRIDAY_API_PORT}"
exec python3 -m uvicorn main:app --host "$FRIDAY_API_HOST" --port "$FRIDAY_API_PORT"
