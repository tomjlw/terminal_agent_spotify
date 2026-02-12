@echo off
echo ========================================
echo  Spotify Smart Agent - Terminal Mode
echo ========================================
echo.
echo Starting Terminal Mode...
echo Make sure Spotify is running!
echo.

REM Check if Python is installed (try py launcher first, then python)
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not found
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)

REM Check if rich is installed
%PYTHON_CMD% -c "import rich" >nul 2>&1
if errorlevel 1 (
    echo Installing terminal UI library (rich)...
    %PYTHON_CMD% -m pip install rich
    echo.
)

REM Run the terminal agent
%PYTHON_CMD% spotify_agent_terminal.py

pause
