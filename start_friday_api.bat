@echo off
cd /d "%~dp0\friday-api"
python -m pip install -r requirements.txt
echo.
echo Starte Friday API auf 0.0.0.0:8000
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
