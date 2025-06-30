@echo off
REM -------------------------------
REM Universal BAT file for Python project startup
REM - Checks for virtual environment and requirements.txt
REM - Creates venv if needed
REM - Installs/updates dependencies
REM - Launches the project (specify the entry file or command below)
REM - Opens the browser at the desired address
REM -------------------------------

setlocal

REM === Settings ===
set VENV_DIR=.venv
set REQUIREMENTS=requirements.txt
set ENTRYPOINT=run.py
set HOST=127.0.0.1
set PORT=5000
set BROWSER_URL=http://%HOST%:%PORT%/

REM === Check for Python ===
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found! Please add Python to your PATH.
    pause
    exit /b
)

REM === Check for venv ===
if not exist "%VENV_DIR%\" (
    echo [INFO] Virtual environment not found. Creating...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b
    )
)

REM === Install dependencies ===
if exist "%REQUIREMENTS%" (
    echo [INFO] Installing dependencies from %REQUIREMENTS%...
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r "%REQUIREMENTS%"
) else (
    echo [WARNING] File %REQUIREMENTS% not found. Skipping dependencies installation.
)

REM === Run the application ===
echo [INFO] Launching the application...
start "" "%VENV_DIR%\Scripts\python.exe" %ENTRYPOINT%

REM === Open browser ===
timeout /t 3 >nul
start "" "%BROWSER_URL%"

endlocal
pause