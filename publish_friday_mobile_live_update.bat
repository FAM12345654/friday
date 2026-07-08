@echo off
setlocal
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0go_live_friday_mobile.ps1" -Channel preview
exit /b %ERRORLEVEL%
