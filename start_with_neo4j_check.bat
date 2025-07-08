@echo off
cd /d "c:\edu\task1\llm-graph-builder"

echo ============================================================
echo LLM GRAPH BUILDER - AUTO STARTUP WITH NEO4J CHECK
echo ============================================================

echo [1/4] Testing Neo4j Connection...
python test_neo4j_connection.py
if errorlevel 1 (
    echo ❌ Neo4j connection failed! Please check credentials.
    pause
    exit /b 1
)

echo.
echo [2/4] Validating Chunking Configuration...
python validate_chunking.py
if errorlevel 1 (
    echo ❌ Chunking validation failed! Please check parameters.
    pause
    exit /b 1
)

echo.
echo [3/4] Starting Backend Server...
start "Backend" cmd /k "cd /d c:\edu\task1\llm-graph-builder\backend && uvicorn score:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo [4/4] Starting Frontend...
start "Frontend" cmd /k "cd /d c:\edu\task1\llm-graph-builder\frontend && npm run dev"

echo.
echo ============================================================
echo 🚀 PROJECT STARTED SUCCESSFULLY!
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:5173
echo    Neo4j: Connected and Ready
echo ============================================================
echo.
echo Press any key to exit this window...
pause > nul
