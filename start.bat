@echo off
REM ============================================================
REM  Aurora Grand Hotel — Booking Chatbot launcher (Windows)
REM  - Creates a .venv if missing
REM  - Installs Flask the first time
REM  - Starts the Flask server and opens the browser
REM ============================================================

setlocal EnableExtensions
cd /d "%~dp0"

echo.
echo   Aurora Grand Hotel -- Booking Chatbot
echo   --------------------------------------
echo.

REM --- 1. Make sure Python is on PATH ---
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python was not found on PATH.
    echo         Install Python 3.10+ from https://www.python.org/downloads/
    echo         and tick "Add Python to PATH" during setup.
    pause
    exit /b 1
)

REM --- 2. Create a virtual environment on first run ---
if not exist ".venv\Scripts\python.exe" (
    echo [SETUP] Creating virtual environment in .venv ...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create the virtual environment.
        pause
        exit /b 1
    )
)

REM --- 3. Install dependencies if Flask is missing ---
".venv\Scripts\python.exe" -c "import flask" 1>nul 2>nul
if errorlevel 1 (
    echo [SETUP] Installing dependencies ...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        pause
        exit /b 1
    )
)

REM --- 4. Launch the browser after a short delay ---
start "" /b cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

REM --- 5. Start the Flask server (blocks; Ctrl+C to quit) ---
echo.
echo   Starting server at http://127.0.0.1:5000
echo   Press Ctrl+C in this window to stop.
echo.
cd src
"..\.venv\Scripts\python.exe" app.py

endlocal
