#!/usr/bin/env bash
# Start the Friday API (cross-platform equivalent of start_friday_api.bat).
set -euo pipefail
cd "$(dirname "$0")/../friday-api"

python3 -m pip install -r requirements.txt
echo
echo "Starte Friday API auf 0.0.0.0:8000"
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
