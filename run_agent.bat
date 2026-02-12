@echo off
echo ========================================
echo  Spotify Smart Agent
echo ========================================
echo.
echo Starting Spotify Smart Agent...
echo Make sure Spotify is running!
echo.

REM Check if Python is installed (try py launcher first, then python)
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not found
        echo Please install Python 3.8+ from python.org
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)

echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check if dependencies are installed
%PYTHON_CMD% -c "import spotipy" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
)

REM Run the agent
echo Launching Spotify Smart Agent...
echo.
%PYTHON_CMD% spotify_agent_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start agent
    echo Check the error message above
)

pause
