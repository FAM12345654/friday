@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "NO_PAUSE=0"
for %%A in (%*) do (
    if /I "%%A"=="--ci" set "NO_PAUSE=1"
    if /I "%%A"=="--no-pause" set "NO_PAUSE=1"
)

echo ========================================
echo Friday Tests
echo ========================================
echo.

echo Checking Python test requirements...
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo Pytest is missing. Installing test requirements...
    python -m pip install -r requirements-test.txt
    if errorlevel 1 (
        echo.
        echo [FAIL] Test requirements installation failed.
        echo Please run:
        echo python -m pip install -r requirements-test.txt
        echo.
        if "%NO_PAUSE%"=="0" pause
        exit /b 1
    )
    echo.
)

echo Running Friday tests...
python -m pytest friday/tests friday-api/tests
set "TEST_EXIT=%errorlevel%"
echo.

if "%TEST_EXIT%"=="0" (
    echo Tests finished successfully.
) else (
    echo Tests failed with exit code %TEST_EXIT%.
)
echo.

if "%NO_PAUSE%"=="0" pause
exit /b %TEST_EXIT%
