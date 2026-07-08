@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "RUN_REPAIR=0"
set "NO_OPEN=0"
set "NO_PAUSE=0"
set "HAS_REPAIR_ATTEMPT=0"
set "SHOW_USAGE=0"
set "UNKNOWN_ARGS="

for %%A in (%*) do (
    if /I "%%A"=="--repair" (
        set "RUN_REPAIR=1"
    ) else if /I "%%A"=="--no-open" (
        set "NO_OPEN=1"
    ) else if /I "%%A"=="/no-open" (
        set "NO_OPEN=1"
    ) else if /I "%%A"=="-nopause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="--no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="/no-pause" (
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="--ci" (
        set "NO_OPEN=1"
        set "NO_PAUSE=1"
    ) else if /I "%%A"=="--help" (
        set "SHOW_USAGE=1"
    ) else if /I "%%A"=="/h" (
        set "SHOW_USAGE=1"
    ) else if /I "%%A"=="/?" (
        set "SHOW_USAGE=1"
    ) else if /I "%%A"=="-h" (
        set "SHOW_USAGE=1"
    ) else (
        set "UNKNOWN_ARGS=!UNKNOWN_ARGS!%%A "
    )
)

if "%SHOW_USAGE%"=="1" goto :Usage
if not "%UNKNOWN_ARGS%"=="" (
    echo [ERROR] Unknown argument^(s^): !UNKNOWN_ARGS!
    goto :Usage
)

goto :RunChecks

:RunChecks
echo ========================================
echo Friday Shortcut Verification
echo ========================================
echo.
echo Project folder:
echo %~dp0
echo.
echo Checking project files...
set "CHECK_FAILED=0"

call :CheckFile "%~dp0start_friday.bat" "start_friday.bat"
call :CheckFile "%~dp0start_friday_stack.bat" "start_friday_stack.bat"
call :CheckFile "%~dp0start_friday_desktop_skip_api.bat" "start_friday_desktop_skip_api.bat"
call :CheckFile "%~dp0run_tests.bat" "run_tests.bat"
call :CheckFile "%~dp0setup_friday.bat" "setup_friday.bat"
call :CheckFile "%~dp0verify_friday_services.bat" "verify_friday_services.bat"
call :CheckFile "%~dp0verify_friday_services_ci.bat" "verify_friday_services_ci.bat"
echo.
echo Checking desktop shortcuts...
call :CheckShortcut "%USERPROFILE%\Desktop\Friday Verify.lnk" "Desktop shortcut: Friday Verify.lnk"
call :CheckShortcut "%USERPROFILE%\Desktop\Friday Checklist.lnk" "Desktop shortcut: Friday Checklist.lnk"
call :CheckShortcut "%USERPROFILE%\Desktop\Friday Mobile Release Check.lnk" "Desktop shortcut: Friday Mobile Release Check.lnk"

if defined OneDrive (
    if exist "%OneDrive%\Desktop\" (
        call :CheckShortcut "%OneDrive%\Desktop\Friday Verify.lnk" "OneDrive shortcut: Friday Verify.lnk"
        call :CheckShortcut "%OneDrive%\Desktop\Friday Checklist.lnk" "OneDrive shortcut: Friday Checklist.lnk"
        call :CheckShortcut "%OneDrive%\Desktop\Friday Mobile Release Check.lnk" "OneDrive shortcut: Friday Mobile Release Check.lnk"
    ) else (
        echo [SKIP] OneDrive shortcut: OneDrive Desktop folder not found
    )
) else (
    echo [SKIP] OneDrive shortcut: OneDrive env var not set
)

if !CHECK_FAILED! gtr 0 (
    echo.
    echo [FAIL] VERIFY_SHORTCUTS_FAILED
    if "%RUN_REPAIR%"=="1" if "!HAS_REPAIR_ATTEMPT!"=="0" (
        echo [INFO] Attempting automatic shortcut repair...
        powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0create_friday_shortcut.ps1"
        set "REPAIR_EXIT=!errorlevel!"
        if !REPAIR_EXIT! neq 0 (
            echo [FAIL] Shortcut creation script failed.
            exit /b 1
        )
        set "HAS_REPAIR_ATTEMPT=1"
        echo [INFO] Re-checking shortcut files...
        call "%~f0" --ci --no-open --no-pause
        exit /b !errorlevel!
    )
    exit /b 1
)

echo.
echo [OK] VERIFY_SHORTCUTS_PASSED

if "%NO_OPEN%"=="0" (
    echo.
    echo Opening project folder...
    start "" "%~dp0"
    echo.
    echo Opening detected Desktop folder...
    powershell -ExecutionPolicy Bypass -Command "Start-Process ([Environment]::GetFolderPath('Desktop'))"
)

if "%NO_PAUSE%"=="0" (
    echo.
    pause
)

exit /b 0

:Usage
echo.
echo Friday Shortcut Verification
echo.
echo Usage:
echo   verify_friday_shortcuts.bat [--repair] [--ci] [--no-open] [--no-pause]
echo.
echo Options:
echo   --repair      create missing shortcuts (create_friday_shortcut.ps1) and recheck
echo   --ci          equivalent to --no-open and --no-pause
echo   --no-open     do not open project/desktop folders
echo   --no-pause    do not pause at end
echo   --help, -h, /h, /?  show this help
if not "%UNKNOWN_ARGS%"=="" (
    exit /b 1
)
exit /b 0

:CheckFile
set "PathToCheck=%~1"
set "Name=%~2"
if exist "%PathToCheck%" (
    echo [OK] %Name%
) else (
    echo [MISSING] %Name%
    set /a CHECK_FAILED+=1
)
goto :eof

:CheckShortcut
set "PathToCheck=%~1"
set "Name=%~2"
if exist "%PathToCheck%" (
    echo [OK] %Name%
) else (
    echo [MISSING] %Name%
    set /a CHECK_FAILED+=1
)
goto :eof
