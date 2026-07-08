@echo off
cd /d "%~dp0"
echo ========================================
echo Friday Shortcut Repair
echo ========================================
echo.
echo Creating Friday desktop shortcuts...
powershell -ExecutionPolicy Bypass -File "%~dp0create_friday_shortcut.ps1"
echo.
echo If you still do not see the shortcuts, run:
echo verify_friday_shortcuts.bat
echo.
pause
