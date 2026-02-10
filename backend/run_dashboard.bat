@echo off
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
)
echo.
echo ========================================
echo  Nana's Bites - Admin Dashboard
echo ========================================
echo.
echo  When you see "Starting development server" below,
echo  open Chrome and go to:  http://127.0.0.1:8000/admin/
echo.
echo  Keep this window open while using the dashboard.
echo ========================================
echo.
python manage.py runserver 127.0.0.1:8000
if errorlevel 1 (
    echo.
    echo Server failed. Try: pip install -r requirements.txt
    pause
)
