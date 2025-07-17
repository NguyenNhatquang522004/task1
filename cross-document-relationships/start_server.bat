@echo off
REM Standalone Cross-Document Relationships Server Launcher
REM This script runs the server completely independent of the main backend

echo =========================================================
echo  Cross-Document Relationships Standalone Server
echo =========================================================
echo.

REM Check if we're in the right directory
if not exist "standalone_server.py" (
    echo ERROR: standalone_server.py not found!
    echo Please run this from the cross-document-relationships directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Creating .env from .env.example...
    if exist ".env.example" (
        copy ".env.example" ".env"
        echo .env file created. Please edit it with your settings.
    ) else (
        echo ERROR: .env.example not found!
        pause
        exit /b 1
    )
)

REM Check if virtual environment exists
if not exist "..\venv\Scripts\activate.bat" (
    if not exist "..\.venv\Scripts\activate.bat" (
        echo WARNING: Virtual environment not found!
        echo Please create a virtual environment or install dependencies manually
        echo.
        echo To create virtual environment:
        echo   cd ..
        echo   python -m venv venv
        echo   venv\Scripts\activate
        echo   pip install -r cross-document-relationships\requirements_standalone.txt
        echo.
        pause
    )
)

echo Checking Python environment...
python --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo.
echo Installing/checking dependencies...
pip install -r requirements_standalone.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo =========================================================
echo  Starting Cross-Document Relationships Server
echo =========================================================
echo  Server URL: http://localhost:8001
echo  API Docs:   http://localhost:8001/docs
echo  Health:     http://localhost:8001/health
echo =========================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python standalone_server.py

echo.
echo Server stopped.
pause
