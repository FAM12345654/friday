@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "RUN_REPAIR=0"
set "RUN_INSTALL=0"
set "CHECK_MOBILE_RELEASE=0"
set "START_STACK=0"
set "NO_PAUSE=0"
set "SHOW_USAGE=0"
set "UNKNOWN_ARGS="
set "FAILED=0"

for %%A in (%*) do (
    if /I "%%A"=="--repair" (
        set "RUN_REPAIR=1"
    ) else if /I "%%A"=="--install" (
        set "RUN_INSTALL=1"
    ) else if /I "%%A"=="--mobile-release" (
        set "CHECK_MOBILE_RELEASE=1"
    ) else if /I "%%A"=="--start" (
        set "START_STACK=1"
    ) else if /I "%%A"=="--no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="/no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="-nopause" (
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
echo Friday One-Command Checklist
echo ========================================
echo.
echo This runs the Friday health checks in order:
echo   1) Optional setup install
echo   2) Shortcut and file check
echo   3) Optional stack startup
echo   4) Service/API verification
echo   5) Optional mobile release readiness
echo.

if "!RUN_INSTALL!"=="1" (
    echo [1/4] Running Friday setup install...
    call "%~dp0setup_friday.bat" --no-pause
    if !errorlevel! neq 0 (
        echo [FAIL] Step 1 failed.
        set /a FAILED+=1
    )
) else (
    echo [1/4] Skipping setup install.
)

echo [2/4] Checking shortcut and required files...
if "!RUN_REPAIR!"=="1" (
    call "%~dp0verify_friday_shortcuts.bat" --repair --ci --no-open --no-pause
) else (
    call "%~dp0verify_friday_shortcuts.bat" --ci --no-open --no-pause
)
if !errorlevel! neq 0 (
    echo [FAIL] Step 1 failed.
    set /a FAILED+=1
)

if "!RUN_REPAIR!"=="1" (
    echo.
    echo [2b/4] Repairing local mobile environment defaults...
    call :RepairMobileEnv
    if !errorlevel! neq 0 (
        echo [FAIL] Mobile environment repair failed.
        set /a FAILED+=1
    )
)

if "!START_STACK!"=="1" (
    echo [3/4] Starting Friday stack before service verification...
    start "Friday Stack" cmd /k "%~dp0start_friday_stack.bat"
    echo [INFO] Waiting 8 seconds for API startup...
    timeout /t 8 /nobreak >nul
) else (
    echo [3/4] Skipping stack startup.
)

echo [4/4] Running API/service verification...
call "%~dp0verify_friday_services.bat" --ci --json --no-pause
if !errorlevel! neq 0 (
    echo [FAIL] Step 4 failed.
    set /a FAILED+=1
)

if "!CHECK_MOBILE_RELEASE!"=="1" (
    echo [5/5] Checking mobile release readiness...
    call "%~dp0verify_friday_mobile_release.bat"
    if !errorlevel! neq 0 (
        echo [FAIL] Mobile release readiness failed.
        set /a FAILED+=1
    )
)

echo Final checklist summary...
if "!FAILED!"=="0" (
    echo [OK] Verification passed.
    echo.
    echo Recommended next commands:
    echo   - start_friday_stack.bat      ^(API + Mobile + Desktop^)
    echo   - start_friday_desktop_skip_api.bat   ^(Desktop only, no embedded API^)
    echo   - verify_friday_shortcuts.bat --repair --ci
    echo   - run_friday_checklist.bat --install --repair --start
    echo.
) else (
    echo [WARN] Verification failed. Please fix issues above before starting Friday.
)

if "%NO_PAUSE%"=="0" (
    echo.
    pause
)

exit /b !FAILED!

:Usage
echo.
echo Friday One-Command Checklist
echo.
echo Usage:
echo   run_friday_checklist.bat [--install] [--repair] [--start] [--mobile-release] [--no-pause]
echo.
echo Options:
echo   --install   run setup_friday.bat before validation
echo   --repair    repair shortcuts and create friday-mobile\.env if missing
echo   --start     start Friday stack before service verification
echo   --mobile-release  verify EAS download/update readiness
echo   --no-pause  do not pause at end
echo   --help,-h,/h,/?   show this help
if not "!UNKNOWN_ARGS!"=="" (
    exit /b 1
)
exit /b 0

:RepairMobileEnv
set "MobileEnv=%~dp0friday-mobile\.env"
set "MobileDir=%~dp0friday-mobile"
if not exist "!MobileDir!\" (
    echo [MISSING] friday-mobile directory not found.
    exit /b 1
)
if exist "!MobileEnv!" (
    echo [OK] friday-mobile\.env already exists.
    exit /b 0
)
> "!MobileEnv!" echo EXPO_PUBLIC_FRIDAY_API_URL=http://192.168.178.42:8000
if exist "!MobileEnv!" (
    echo [OK] Created friday-mobile\.env with local API URL.
    exit /b 0
)
echo [FAIL] Could not create friday-mobile\.env.
exit /b 1
