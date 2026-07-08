@echo off
setlocal
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0go_live_friday_mobile.ps1" %*
set "EXITCODE=%ERRORLEVEL%"
if /i not "%*"=="--no-pause" pause
exit /b %EXITCODE%
