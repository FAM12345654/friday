#!/usr/bin/env bash
# Start the local WhatsApp bridge (cross-platform equivalent of start_whatsapp_bridge.bat).
set -euo pipefail
cd "$(dirname "$0")/../friday-whatsapp-bridge"

if [ ! -d node_modules ]; then
    echo "Installing WhatsApp bridge dependencies..."
    npm install
fi

exec npm start
