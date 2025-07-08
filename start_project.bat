@echo off
echo ================================================================
echo       LLM GRAPH BUILDER - AUTO STARTUP WITH NEO4J
echo ================================================================

echo.
echo 🔍 Step 1: Testing Neo4j Connection...
python neo4j_auto_connect.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Neo4j connection failed! Please fix before starting servers.
    echo 💡 Check your credentials in .env files
    echo 🌐 Verify your instance at https://console.neo4j.io
    pause
    exit /b 1
)

echo.
echo ✅ Neo4j connection successful!
echo.
echo 🚀 Step 2: Starting Backend Server...
cd backend
start "LLM Graph Builder Backend" cmd /k "python -m uvicorn score:app --reload --host 0.0.0.0 --port 8000"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo 🎨 Step 3: Starting Frontend Server...
cd ..\frontend
start "LLM Graph Builder Frontend" cmd /k "npm run dev"

echo.
echo ================================================================
echo 🎉 LLM GRAPH BUILDER STARTED SUCCESSFULLY!
echo ================================================================
echo.
echo 📊 Services Running:
echo    🔙 Backend:  http://localhost:8000
echo    🎨 Frontend: http://localhost:5173 (or next available port)
echo    🗄️  Neo4j:    %NEO4J_URI%
echo.
echo 📖 API Documentation: http://localhost:8000/docs
echo 🔧 Neo4j Console: https://console.neo4j.io
echo.
echo Press any key to open the application in browser...
pause > nul

start http://localhost:5173

echo.
echo 🎯 Application opened in browser!
echo 📝 To stop servers: Close the terminal windows
echo ================================================================
