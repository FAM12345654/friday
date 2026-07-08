@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "NO_PAUSE=0"
set "SHOW_USAGE=0"
set "UNKNOWN_ARGS="
set "FAILED=0"

for %%A in (%*) do (
    if /I "%%A"=="--no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="/no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="-nopause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="--ci" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="--help" (
        set "SHOW_USAGE=1"
    ) else if /I "%%A"=="-h" (
        set "SHOW_USAGE=1"
    ) else if /I "%%A"=="/h" (
        set "SHOW_USAGE=1"
    ) else if /I "%%A"=="/?" (
        set "SHOW_USAGE=1"
    ) else (
        set "UNKNOWN_ARGS=!UNKNOWN_ARGS!%%A "
    )
)

if "!SHOW_USAGE!"=="1" goto :Usage
if not "!UNKNOWN_ARGS!"=="" (
    echo [ERROR] Unknown argument^(s^): !UNKNOWN_ARGS!
    goto :Usage
)

echo ========================================
echo Friday Setup
echo ========================================
echo.
echo Installing Python requirements for core app and API...
python -m pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [FAIL] Python core requirements installation failed.
    set /a FAILED+=1 >nul
)
echo.
if exist "friday-api\requirements.txt" (
    echo Installing FastAPI requirements...
    python -m pip install -r friday-api\requirements.txt
    if !errorlevel! neq 0 (
        echo [FAIL] FastAPI requirements installation failed.
        set /a FAILED+=1 >nul
    )
)
echo.
if exist "friday-mobile\package.json" (
    echo Installing Mobile dependencies...
    cd friday-mobile
    call npm install
    set "MOBILE_NPM_EXIT=!errorlevel!"
    if !MOBILE_NPM_EXIT! neq 0 (
        echo [FAIL] Mobile dependencies installation failed.
        set /a FAILED+=1 >nul
    )
    cd ..
)
echo.
if exist "friday-desktop\package.json" (
    echo Installing Desktop dependencies...
    cd friday-desktop
    call npm install
    set "DESKTOP_NPM_EXIT=!errorlevel!"
    if !DESKTOP_NPM_EXIT! neq 0 (
        echo [FAIL] Desktop dependencies installation failed.
        set /a FAILED+=1 >nul
    )
    cd ..
)
echo.
echo Creating Friday desktop shortcut...
powershell -ExecutionPolicy Bypass -File "%~dp0create_friday_shortcut.ps1"
if !errorlevel! neq 0 (
    echo [FAIL] Shortcut creation failed.
    set /a FAILED+=1 >nul
)
echo.
if !FAILED! neq 0 (
    echo Setup finished with !FAILED! failure^(s^).
) else (
    echo Setup finished.
)
echo.
echo You can now start Friday from your Desktop shortcut:
echo Friday
echo.
echo You can also run:
echo setup_friday.bat
echo start_friday_stack.bat
echo start_friday.bat
echo start_friday_api.bat
echo start_friday_mobile.bat
echo start_friday_desktop_skip_api.bat
echo start_friday_desktop.bat
echo run_friday_checklist.bat
echo verify_friday_services.bat
echo verify_friday_services_ci.bat
echo verify_friday_mobile_release.bat
echo configure_friday_mobile_eas.bat
echo build_friday_mobile_android_preview.bat
echo publish_friday_mobile_update_preview.bat
echo.
if "%NO_PAUSE%"=="0" pause
exit /b !FAILED!

:Usage
echo.
echo Friday Setup
echo.
echo Usage:
echo   setup_friday.bat [--ci] [--no-pause]
echo.
echo Options:
echo   --ci          run without pause
echo   --no-pause    do not pause at end
echo   --help, -h, /h, /?  show this help
if not "!UNKNOWN_ARGS!"=="" (
    exit /b 1
)
exit /b 0
