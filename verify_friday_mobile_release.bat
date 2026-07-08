@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0verify_friday_mobile_release.ps1"
exit /b %errorlevel%
