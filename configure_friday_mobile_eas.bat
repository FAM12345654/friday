@echo off
chcp 65001 >nul
cd /d "%~dp0friday-mobile"
echo [INFO] Checking Expo account...
call npx eas-cli@latest whoami
if errorlevel 1 (
    echo [INFO] Please log in to Expo.
    call npx eas-cli@latest login
    if errorlevel 1 exit /b 1
)
echo [INFO] Configuring EAS Update for Friday Mobile...
call npx eas-cli@latest update:configure
exit /b %errorlevel%
