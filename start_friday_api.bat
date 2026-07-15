@echo off
cd /d "%~dp0\friday-api"
if "%FRIDAY_API_HOST%"=="" set "FRIDAY_API_HOST=127.0.0.1"
if "%FRIDAY_API_PORT%"=="" set "FRIDAY_API_PORT=8000"
if /I not "%FRIDAY_API_HOST%"=="127.0.0.1" if /I not "%FRIDAY_API_HOST%"=="localhost" if "%FRIDAY_API_TOKEN:~31,1%"=="" (
  echo FEHLER: FRIDAY_API_TOKEN muss fuer LAN- oder Tunnel-Zugriff mindestens 32 Zeichen haben.
  exit /b 1
)
python -m pip install -r requirements.txt
echo.
echo Starte Friday API auf %FRIDAY_API_HOST%:%FRIDAY_API_PORT%
uvicorn main:app --host "%FRIDAY_API_HOST%" --port "%FRIDAY_API_PORT%"
