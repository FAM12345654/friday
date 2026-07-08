@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0verify_friday_services.ps1" -SummaryOnly -AsJson %*
if %errorlevel% neq 0 (
    echo [FAIL] Friday service verification failed.
    exit /b 1
) else (
    echo [OK] Friday service verification completed.
    exit /b 0
)
