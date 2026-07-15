@echo off
setlocal
cd /d "%~dp0"
if "%FRIDAY_API_PORT%"=="" set "FRIDAY_API_PORT=8001"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Start-Friday-API-Autostart.ps1" -Port %FRIDAY_API_PORT% -MaxRestarts 3 -RestartDelaySeconds 10
exit /b %ERRORLEVEL%
