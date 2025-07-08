#!/usr/bin/env python3
"""
Quick Start Script for LLM Graph Builder Backend
Starts backend on port 8000 for fast development
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

if __name__ == "__main__":
    print("🚀 Starting LLM Graph Builder Backend (Quick Start)")
    print("📝 Note: API keys tested only when used")
    print("🌐 Server will be available at: http://localhost:8000")
    print("=" * 60)
    
    # Import and run the app
    from score import app
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
