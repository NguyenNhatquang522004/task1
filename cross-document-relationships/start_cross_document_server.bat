@echo off
echo ================================================================
echo           Cross-Document Relationships Standalone Server
echo ================================================================
echo.
echo Starting server tach biet hoan toan voi backend...
echo Focus: Gan moi quan he cho entities o document khac nhau
echo Port: 8001 (khac voi backend port 8000)
echo.

cd /d "%~dp0"

echo Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements_standalone.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Starting Cross-Document Relationships Server...
echo API Documentation: http://localhost:8001/docs
echo Health Check: http://localhost:8001/health
echo.

python standalone_server.py

echo.
echo Server stopped.
pause
