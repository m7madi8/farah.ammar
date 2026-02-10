@echo off
cd /d "%~dp0"
title Nana's Bites - Dashboard

echo.
echo ==========================================
echo  Nana's Bites - Setup and run dashboard
echo ==========================================
echo.
echo  Folder: %CD%
echo.

if exist .venv\Scripts\activate.bat (
    echo Using existing .venv
    call .venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create venv. Make sure Python is installed.
        pause
        exit /b 1
    )
    call .venv\Scripts\activate.bat
)

echo.
echo Installing packages (Django, DRF, etc.)...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo Pip install failed.
    pause
    exit /b 1
)

echo.
echo Running database migrations...
python manage.py migrate --noinput
if errorlevel 1 (
    echo Migrate failed. You may need to set DB credentials.
    echo For a quick test, you can use SQLite - see README.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo  Server starting...
echo  Open in Chrome:  http://127.0.0.1:8000/admin/
echo  Keep this window open.
echo ==========================================
echo.

python manage.py runserver 127.0.0.1:8000

echo.
echo Server stopped.
pause
