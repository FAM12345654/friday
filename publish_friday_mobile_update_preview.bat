@echo off
chcp 65001 >nul
cd /d "%~dp0friday-mobile"
call npm run release:check
if %errorlevel% neq 0 exit /b 1
call npx eas-cli@latest update --channel preview --message "Friday preview update"
exit /b %errorlevel%
