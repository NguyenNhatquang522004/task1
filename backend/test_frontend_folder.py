#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script để kiểm tra tính năng folder selection trong frontend
"""

import requests
import time

def test_frontend_folder_api():
    """Test gọi API folders từ frontend"""
    
    print("🧪 Testing Frontend Folder Selection Feature")
    print("=" * 60)
    
    # Test backend API trước
    print("1. Testing Backend API...")
    try:
        # Test GET /folders
        backend_url = "http://localhost:8000/folders"
        params = {
            "uri": "neo4j+s://013fb011.databases.neo4j.io",
            "userName": "neo4j", 
            "password": "NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4",
            "database": "neo4j"
        }
        
        response = requests.get(backend_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend API Status: {response.status_code}")
            print(f"📋 Available folders: {data.get('data', [])}")
        else:
            print(f"❌ Backend API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend API error: {e}")
        return False
    
    # Test frontend
    print("\n2. Testing Frontend...")
    try:
        frontend_url = "http://localhost:5174"
        response = requests.get(frontend_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Frontend Status: {response.status_code}")
            print(f"🌐 Frontend available at: {frontend_url}")
            print("\n📝 Instructions to test:")
            print("  1. Open browser at http://localhost:5174")
            print("  2. Connect to Neo4j database")
            print("  3. Go to 'Local Files' section")
            print("  4. Try to upload a file (PDF/TXT/DOCX)")
            print("  5. Check if folder selection modal appears")
            print("  6. Select folder and course code")
            print("  7. Verify file uploads with correct metadata")
            
        else:
            print(f"❌ Frontend failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Frontend and Backend are ready for testing!")
    return True

def check_services():
    """Kiểm tra trạng thái các services"""
    
    services = [
        ("Backend", "http://localhost:8000/health"),
        ("Frontend", "http://localhost:5174")
    ]
    
    print("🔍 Checking services status...")
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Running")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Not responding ({e})")
    
    print()

if __name__ == "__main__":
    print("🚀 Frontend Folder Selection Test")
    print("=" * 60)
    
    # Wait for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(3)
    
    check_services()
    test_frontend_folder_api()
    
    print("\n🎯 Next Steps:")
    print("1. Open http://localhost:5174 in browser")
    print("2. Connect to Neo4j")
    print("3. Upload a file and test folder selection!")
    print("4. Check backend logs for auto-detection details")
