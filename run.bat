@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo   College Event Management System - Local Launcher
echo ========================================================
echo.

:: Step 1: Detect Python executable from venv or system
set "PYTHON_EXE="

if exist "%~dp0venv\Scripts\python.exe" (
    echo [i] Found Python virtual environment in venv.
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    echo [i] Found Python virtual environment in .venv.
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
) else (
    echo [i] Checking system Python...
    where python >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_EXE=python"
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python was not found in venv or system PATH.
    echo Please install Python 3.10+ and ensure it is added to your PATH.
    echo.
    pause
    exit /b 1
)

:: Step 2: Verify Python works
"%PYTHON_EXE%" --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to execute Python using: %PYTHON_EXE%
    echo.
    pause
    exit /b 1
)

:: Step 3: Check configuration file
if not exist ".env" (
    if exist ".env.example" (
        echo [!] Warning: No .env configuration file found.
        echo [i] Creating .env from .env.example...
        copy ".env.example" ".env" >nul
    ) else (
        echo [!] Warning: .env file not found.
    )
)

:: Step 4: Display startup information and launch Flask
echo.
echo ========================================================
echo   Starting Flask Server...
echo   Application URL : http://127.0.0.1:5000
echo   Admin Login URL : http://127.0.0.1:5000/admin/login
echo.
echo   Press CTRL+C to stop the server anytime.
echo ========================================================
echo.

"%PYTHON_EXE%" app.py

if errorlevel 1 (
    echo.
    echo ========================================================
    echo [ERROR] Application stopped unexpectedly.
    echo.
    echo Troubleshooting Steps:
    echo  1. Have you initialized the MySQL database? Run:
    echo     "%PYTHON_EXE%" init_db.py --seed
    echo  2. Is the MySQL80 service running?
    echo  3. Check database credentials in .env file.
    echo ========================================================
    echo.
    pause
)
