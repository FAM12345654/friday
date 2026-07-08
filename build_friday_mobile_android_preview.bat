@echo off
chcp 65001 >nul
cd /d "%~dp0friday-mobile"
call npm run release:check
if %errorlevel% neq 0 exit /b 1
call npx eas-cli@latest build --platform android --profile preview
exit /b %errorlevel%
