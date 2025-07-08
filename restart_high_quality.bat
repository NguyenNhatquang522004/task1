@echo off
echo ====================================================
echo RESTARTING LLM GRAPH BUILDER WITH HIGH QUALITY CONFIG
echo ====================================================

echo.
echo 🔍 Validating High Quality configuration...
python validate_high_quality_config.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Configuration validation failed!
    pause
    exit /b 1
)

echo.
echo ✅ Configuration validated successfully!
echo.

echo 🔄 Stopping any existing services...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 3 /nobreak >nul

echo.
echo 🚀 Starting Backend with High Quality chunking...
start "Backend - High Quality" cmd /k "cd backend && python score.py"

echo ⏳ Waiting for backend to start...
timeout /t 10 /nobreak >nul

echo.
echo 🌐 Starting Frontend...
start "Frontend - High Quality" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ Both services are starting with High Quality configuration:
echo    - Tokens per chunk: 1024
echo    - Chunk overlap: 100 
echo    - Max token chunk size: 20000
echo.
echo 📍 Access points:
echo    - Frontend: http://localhost:5173
echo    - Backend API: http://localhost:8000
echo    - API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
