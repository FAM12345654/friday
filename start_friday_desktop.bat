@echo off
cd /d "%~dp0\friday-desktop"
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
