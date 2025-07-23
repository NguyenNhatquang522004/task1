#!/usr/bin/env python3
"""
Test script for folder selection functionality
"""
import requests
import json
import urllib.parse

def test_folders_api():
    """Test the folders API endpoint"""
    
    print("🧪 Testing Folders API...")
    
    # API endpoint
    base_url = "http://localhost:8000"
    
    # Connection parameters (from your .env)
    params = {
        "uri": "neo4j+s://013fb011.databases.neo4j.io",
        "userName": "neo4j",
        "password": "NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4",
        "database": "neo4j"
    }
    
    try:
        # Test folders endpoint
        print(f"📡 Calling GET {base_url}/folders")
        response = requests.get(f"{base_url}/folders", params=params, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if 'data' in data:
                folders = data['data']
                print(f"\n📁 Available Folders ({len(folders)}):")
                for i, folder in enumerate(folders, 1):
                    print(f"  {i}. {folder}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

def test_upload_with_folder():
    """Test upload with folder selection"""
    
    print(f"\n🧪 Testing Upload with Folder Selection...")
    
    # Create a simple test file
    test_content = "Đây là nội dung test cho file upload với folder_name."
    test_filename = "test_folder_upload.txt"
    
    # Upload parameters
    upload_data = {
        "chunkNumber": "1",
        "totalChunks": "1", 
        "originalname": test_filename,
        "model": "gemini_2.0_flash",
        "uri": "neo4j+s://013fb011.databases.neo4j.io",
        "userName": "neo4j",
        "password": "NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4",
        "database": "neo4j",
        "course_code": "CMP177",
        "folder_name": "đề cương"  # Test với folder name có dấu
    }
    
    # Create file object
    files = {
        "file": (test_filename, test_content.encode('utf-8'), "text/plain")
    }
    
    try:
        print(f"📡 Calling POST http://localhost:8000/upload")
        print(f"📋 Upload data: {upload_data}")
        
        response = requests.post(
            "http://localhost:8000/upload",
            data=upload_data,
            files=files,
            timeout=30
        )
        
        print(f"📊 Upload Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload Success!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Upload Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    test_folders_api()
    test_upload_with_folder()
