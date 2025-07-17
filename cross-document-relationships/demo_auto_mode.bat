@echo off
echo ================================================================
echo           Cross-Document Auto Mode Demo
echo ================================================================
echo.
echo Demo: Server tu dong tim va gan moi quan he khi khoi dong
echo.

cd /d "%~dp0"

echo Creating .env for auto mode...
(
echo # Auto mode configuration
echo AUTO_START_ANALYSIS=true
echo AUTO_MAX_PAIRS=50
echo AUTO_BATCH_SIZE=5
echo AUTO_SIMILARITY_THRESHOLD=0.75
echo.
echo # Neo4j connection
echo NEO4J_URI=neo4j://localhost:7687
echo NEO4J_USERNAME=neo4j
echo NEO4J_PASSWORD=password
echo.
echo # Gemini API keys ^(replace with your keys^)
echo GEMINI_API_KEYS=your_key_1,your_key_2,your_key_3
) > .env.auto

echo.
echo ================================================================
echo   .env.auto file created with AUTO_START_ANALYSIS=true
echo   Please update with your actual Neo4j and Gemini credentials
echo ================================================================
echo.
echo To run in auto mode:
echo   1. Update .env.auto with your credentials
echo   2. copy .env.auto .env
echo   3. python standalone_server.py
echo.
echo Server will automatically start analyzing cross-document relationships!
echo.
pause
