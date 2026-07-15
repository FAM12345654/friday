@echo off
cd /d "%~dp0"
echo ========================================
echo Friday Stack Starter
echo ========================================
echo.
echo Startet API, Mobile und Desktop in eigenen Fenstern.
echo Desktop startet dabei mit deaktiviertem eingebetteten API-Start.
if "%FRIDAY_API_PORT%"=="" set "FRIDAY_API_PORT=8001"
echo Die API läuft nur im separaten API-Fenster auf Port %FRIDAY_API_PORT%.
echo.

start "Friday API (%FRIDAY_API_PORT%)" cmd /k "%~dp0start_friday_api.bat"
timeout /t 2 >nul

start "Friday Mobile" cmd /k "%~dp0start_friday_mobile.bat"
timeout /t 1 >nul

start "Friday Desktop" cmd /k call "%~dp0start_friday_desktop.bat" stack

echo.
echo Alle Dienste wurden gestartet.
echo.
pause
