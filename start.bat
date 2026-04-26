@echo off

echo Starting TRAE Root Workspace...
echo ================================

REM Change to the directory where this script is located
cd /d %~dp0

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if trae.py exists
if not exist trae.py (
    echo ERROR: trae.py not found
    pause
    exit /b 1
)

REM Run TRAE
python trae.py

REM Pause to see output
if %errorlevel% neq 0 (
    echo TRAE exited with error code: %errorlevel%
    pause
    exit /b %errorlevel%
)

pause