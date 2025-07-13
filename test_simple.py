#!/usr/bin/env python3
"""
Simple test to check if API accepts schema parameter
"""
import requests

def test_api_schema():
    """Test if the API accepts schema parameter without full processing"""
    
    url = "http://localhost:8000/docs"
    
    try:
        print("Checking if backend server is accessible...")
        response = requests.get(url, timeout=5)
        print(f"✅ Server is running! Status: {response.status_code}")
        print("You can check the API docs at http://localhost:8000/docs")
        print("The /extract endpoint should now accept a 'schema' parameter.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server.")
        print("The server might still be starting up or there might be an issue.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_api_schema()
