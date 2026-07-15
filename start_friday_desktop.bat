@echo off
setlocal
cd /d "%~dp0\friday-desktop"
if "%FRIDAY_API_PORT%"=="" set "FRIDAY_API_PORT=8001"
if "%FRIDAY_API_TOKEN%"=="" for /f "usebackq delims=" %%T in (`powershell.exe -NoProfile -Command "[Environment]::GetEnvironmentVariable('FRIDAY_API_TOKEN','User')"`) do set "FRIDAY_API_TOKEN=%%T"
if "%FRIDAY_API_TOKEN:~31,1%"=="" (
    echo FEHLER: FRIDAY_API_TOKEN fehlt oder ist kuerzer als 32 Zeichen.
    exit /b 1
)
if /I "%FRIDAY_SKIP_EMBEDDED_API%"=="1" (
    echo Desktop startet ohne eingebetteten API.
    set "FRIDAY_SKIP_EMBEDDED_API=1"
)
if /I "%FRIDAY_SKIP_EMBEDDED_API%"=="true" (
    echo Desktop startet ohne eingebetteten API.
    set "FRIDAY_SKIP_EMBEDDED_API=true"
)

if /I "%~1"=="stack" (
    echo Desktop startet ohne eingebetteten API (Startet bereits im Stack).
    set "FRIDAY_SKIP_EMBEDDED_API=1"
)

if /I "%~1"=="skipapi" (
    set "FRIDAY_SKIP_EMBEDDED_API=1"
)

npm install
echo.
npm run dev
