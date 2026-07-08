@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "PS_ARGS="
set "NO_PAUSE=0"
set "SHOW_USAGE=0"
set "UNKNOWN_ARGS="

for %%A in (%*) do (
    if /I "%%A"=="--no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="/no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="-nopause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="--ci" (
        set "NO_PAUSE=1"
        set "PS_ARGS=!PS_ARGS! -SummaryOnly"
    ) else if /I "%%A"=="--summary-only" (
        set "PS_ARGS=!PS_ARGS! -SummaryOnly"
    ) else if /I "%%A"=="--json" (
        set "PS_ARGS=!PS_ARGS! -AsJson"
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

echo [INFO] Running Friday service verification...
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0verify_friday_services.ps1" !PS_ARGS!
set "SERVICE_EXIT=!errorlevel!"
if !SERVICE_EXIT! neq 0 (
    echo.
    echo [FAIL] Friday service verification failed. See details above.
) else (
    echo.
    echo [OK] Friday service verification completed.
)

if "%NO_PAUSE%"=="0" pause
exit /b !SERVICE_EXIT!

:Usage
echo.
echo Friday Service Verification
echo.
echo Usage:
echo   verify_friday_services.bat [--ci] [--summary-only] [--json] [--no-pause]
echo.
echo Options:
echo   --ci            Run in summary-only mode (suppresses detailed logs)
echo   --summary-only  Only summary output, keep checks
echo   --json          Include JSON output from script
echo   --no-pause      Do not pause at end
echo   --help, -h, /h, /?  Show this help
if not "!UNKNOWN_ARGS!"=="" (
    exit /b 1
)
exit /b 0
