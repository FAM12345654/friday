@echo off
cd /d "%~dp0"
echo ========================================
echo Friday WhatsApp Read-Bridge
echo ========================================
echo.

python -c "from friday import config; raise SystemExit(0 if getattr(config, 'ENABLE_WHATSAPP_BRIDGE_READ', False) else 1)"
if errorlevel 1 (
    echo WhatsApp Read-Bridge ist deaktiviert.
    echo Aktiviere sie zuerst im Friday Konten-Menue mit WHATSAPP BRIDGE AKTIVIEREN.
    echo.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo Friday API ist unter http://127.0.0.1:8000 nicht erreichbar.
    echo Starte zuerst start_friday_api.bat.
    echo.
    pause
    exit /b 1
)

cd friday-whatsapp-bridge
if not exist node_modules (
    echo Node-Abhaengigkeiten fehlen.
    echo Fuehre einmal aus:
    echo npm install
    echo.
    pause
    exit /b 1
)

echo Starte Bridge im Nur-Lesen-Modus.
echo Senden bleibt ausgeschlossen.
echo.
npm start
pause
