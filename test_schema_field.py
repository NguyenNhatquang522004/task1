#!/usr/bin/env python3
"""
Test script to verify schema field functionality
"""
import requests
import json

def test_schema_field():
    """Test the schema field in the /extract endpoint"""
    
    # API endpoint
    url = "http://localhost:8000/extract"
    
    # Test data
    data = {
        "uri": "neo4j://localhost:7687",
        "database": "neo4j", 
        "userName": "neo4j",
        "password": "password",
        "source_type": "local file",
        "model": "gpt-4",
        "allowedNodes": [],
        "allowedRelationship": [],
        "language": "en",
        "schema": "custom_test_schema_v1"  # Testing schema field
    }
    
    # Mock file for testing
    files = {
        "file": ("test.txt", "This is a test document for schema field testing.", "text/plain")
    }
    
    try:
        print("Testing schema field with /extract endpoint...")
        print(f"Schema value being sent: {data['schema']}")
        
        # Make the request
        response = requests.post(url, data=data, files=files)
        
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the backend is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")

if __name__ == "__main__":
    test_schema_field()
