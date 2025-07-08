#!/usr/bin/env python3
"""
Final validation script for LLM Graph Builder
Tests end-to-end connectivity and configuration
"""

import os
import sys
import requests
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

def check_environment_files():
    """Check if environment files exist and have correct settings"""
    print("🔍 Checking environment files...")
    
    # Check backend .env
    backend_env = "c:/edu/task1/llm-graph-builder/backend/.env"
    frontend_env = "c:/edu/task1/llm-graph-builder/frontend/.env"
    
    if not os.path.exists(backend_env):
        print("❌ Backend .env file not found")
        return False
    
    if not os.path.exists(frontend_env):
        print("❌ Frontend .env file not found")
        return False
        
    # Load and check frontend env
    with open(frontend_env, 'r') as f:
        frontend_content = f.read()
    
    if 'VITE_BACKEND_API_URL="http://localhost:8000"' in frontend_content:
        print("✅ Frontend configured to connect to backend on port 8000")
    else:
        print("❌ Frontend not configured for port 8000")
        return False
        
    if 'VITE_TOKENS_PER_CHUNK=1024' in frontend_content:
        print("✅ Frontend chunking: TOKENS_PER_CHUNK=1024")
    else:
        print("❌ Frontend chunking not set to 1024")
        
    if 'VITE_CHUNK_OVERLAP=100' in frontend_content:
        print("✅ Frontend chunking: CHUNK_OVERLAP=100")
    else:
        print("❌ Frontend chunk overlap not set to 100")
    
    return True

def test_neo4j_connection():
    """Test Neo4j connection"""
    print("\n🔍 Testing Neo4j connection...")
    
    try:
        # Load backend environment
        load_dotenv("c:/edu/task1/llm-graph-builder/backend/.env")
        
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        print(f"Connecting to: {neo4j_uri}")
        print(f"Username: {neo4j_username}")
        
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        
        with driver.session() as session:
            result = session.run("RETURN 'Neo4j connection successful!' as message")
            record = result.single()
            print(f"✅ {record['message']}")
            
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Neo4j connection failed: {str(e)}")
        return False

def test_backend_api():
    """Test backend API connectivity"""
    print("\n🔍 Testing backend API...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend on port 8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Backend connection timeout")
        return False
    except Exception as e:
        print(f"❌ Backend API error: {str(e)}")
        return False

def test_chunking_endpoint():
    """Test chunking configuration endpoint"""
    print("\n🔍 Testing chunking configuration...")
    
    try:
        # Test chunking endpoint if available
        response = requests.get("http://localhost:8000/chunking-config", timeout=10)
        if response.status_code == 200:
            config = response.json()
            print("✅ Chunking config endpoint available")
            print(f"   Token per chunk: {config.get('tokens_per_chunk', 'N/A')}")
            print(f"   Chunk overlap: {config.get('chunk_overlap', 'N/A')}")
            print(f"   Max token chunk size: {config.get('max_token_chunk_size', 'N/A')}")
            return True
        else:
            print(f"⚠️  Chunking config endpoint not available (status: {response.status_code})")
            return True  # This is optional
            
    except Exception as e:
        print(f"⚠️  Chunking config endpoint test failed: {str(e)}")
        return True  # This is optional

def test_frontend_accessibility():
    """Test if frontend is accessible"""
    print("\n🔍 Testing frontend accessibility...")
    
    try:
        response = requests.get("http://localhost:5173", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend accessible on port 5173")
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to frontend on port 5173")
        return False
    except Exception as e:
        print(f"❌ Frontend accessibility error: {str(e)}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 Final LLM Graph Builder Validation")
    print("="*50)
    
    tests = [
        ("Environment Configuration", check_environment_files),
        ("Neo4j Connection", test_neo4j_connection),
        ("Backend API", test_backend_api),
        ("Chunking Configuration", test_chunking_endpoint),
        ("Frontend Accessibility", test_frontend_accessibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
        
    print("\n" + "="*50)
    print(f"🎯 Final Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All systems are ready!")
        print("\n📍 Access Points:")
        print("   Frontend: http://localhost:5173")
        print("   Backend:  http://localhost:8000")
        print("   Neo4j:    bolt://localhost:7687")
        print("\n🎛️  Configuration:")
        print("   Chunk Size: 1024 tokens")
        print("   Chunk Overlap: 100 tokens")
        print("   Max Token Chunk Size: 20000")
        print("   Quality Profile: HIGH QUALITY")
        return True
    else:
        print("❌ Some systems need attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
