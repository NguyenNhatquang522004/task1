#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script để kiểm tra auto-detect schema/triplet/instructions cho tất cả folder_name
"""

import requests
import json

def test_upload_with_different_folders():
    """Test upload với các folder_name khác nhau"""
    
    # Test cases với các folder_name khác nhau
    test_cases = [
        {
            'folder_name': 'đề cương',
            'expected_schema': 'decuong'
        },
        {
            'folder_name': 'giáo trình chính thức', 
            'expected_schema': 'giaotrinh'
        },
        {
            'folder_name': 'tham khảo ngoại bộ',
            'expected_schema': 'ebook'
        },
        {
            'folder_name': 'unknown_folder',
            'expected_schema': 'default'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: folder_name = '{test_case['folder_name']}'")
        print(f"📋 Expected schema: {test_case['expected_schema']}")
        
        # Create test content
        test_content = f"Test content for {test_case['folder_name']}"
        test_filename = f"test_{i}_{test_case['folder_name'].replace(' ', '_')}.txt"
        
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
            "folder_name": test_case['folder_name']
        }
        
        # Create file object
        files = {
            "file": (test_filename, test_content.encode('utf-8'), "text/plain")
        }
        
        try:
            print(f"📡 Uploading file with folder_name: {test_case['folder_name']}")
            response = requests.post(
                "http://localhost:8000/upload",
                data=upload_data,
                files=files,
                timeout=30
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Upload Success!")
                print(f"📄 Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"❌ Upload Failed!")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Auto-detect Schema/Triplet/Instructions for different folder_name")
    print("=" * 80)
    
    test_upload_with_different_folders()
    
    print("\n" + "=" * 80)
    print("✅ Test completed! Check backend logs for auto-detection details.")
