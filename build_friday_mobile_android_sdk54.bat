@echo off
setlocal
cd /d "%~dp0friday-mobile"
echo Starte Android SDK-54 APK Build fuer Friday...
npx eas-cli@latest build --platform android --profile preview
exit /b %ERRORLEVEL%
