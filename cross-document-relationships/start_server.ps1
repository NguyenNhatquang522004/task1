# Standalone Cross-Document Relationships Server Launcher (PowerShell)
# This script runs the server completely independent of the main backend

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Cross-Document Relationships Standalone Server" -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "standalone_server.py")) {
    Write-Host "ERROR: standalone_server.py not found!" -ForegroundColor Red
    Write-Host "Please run this from the cross-document-relationships directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host ".env file created. Please edit it with your settings." -ForegroundColor Green
    } else {
        Write-Host "ERROR: .env.example not found!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check Python
Write-Host "Checking Python environment..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python not found in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing/checking dependencies..." -ForegroundColor Cyan
try {
    pip install -r requirements_standalone.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Starting Cross-Document Relationships Server" -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Server URL: http://localhost:8001" -ForegroundColor White
Write-Host " API Docs:   http://localhost:8001/docs" -ForegroundColor White
Write-Host " Health:     http://localhost:8001/health" -ForegroundColor White
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
try {
    python standalone_server.py
} catch {
    Write-Host ""
    Write-Host "❌ Server encountered an error" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}
