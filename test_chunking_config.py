#!/usr/bin/env python3
"""
Test chunking configuration với backend và frontend
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

def test_chunking_config():
    print("🧪 TESTING CHUNKING CONFIGURATION")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    load_dotenv("backend/.env")
    load_dotenv("frontend/.env")
    
    # Backend configuration
    backend_config = {
        'TOKENS_PER_CHUNK': os.getenv('TOKENS_PER_CHUNK', '1024'),
        'CHUNK_OVERLAP': os.getenv('CHUNK_OVERLAP', '100'), 
        'MAX_TOKEN_CHUNK_SIZE': os.getenv('MAX_TOKEN_CHUNK_SIZE', '10000'),
        'NUMBER_OF_CHUNKS_TO_COMBINE': os.getenv('NUMBER_OF_CHUNKS_TO_COMBINE', '6')
    }
    
    # Frontend configuration
    frontend_config = {
        'VITE_TOKENS_PER_CHUNK': os.getenv('VITE_TOKENS_PER_CHUNK', '100'),
        'VITE_CHUNK_OVERLAP': os.getenv('VITE_CHUNK_OVERLAP', '20'),
        'VITE_CHUNK_TO_COMBINE': os.getenv('VITE_CHUNK_TO_COMBINE', '1')
    }
    
    print("📊 BACKEND CONFIGURATION:")
    for key, value in backend_config.items():
        print(f"   {key}: {value}")
    
    print("\n📊 FRONTEND CONFIGURATION:")
    for key, value in frontend_config.items():
        print(f"   {key}: {value}")
    
    # Check if values match
    print("\n🔍 VALIDATION:")
    
    # Check tokens per chunk
    if backend_config['TOKENS_PER_CHUNK'] == frontend_config['VITE_TOKENS_PER_CHUNK']:
        print(f"   ✅ TOKENS_PER_CHUNK matches: {backend_config['TOKENS_PER_CHUNK']}")
    else:
        print(f"   ❌ TOKENS_PER_CHUNK mismatch: Backend={backend_config['TOKENS_PER_CHUNK']}, Frontend={frontend_config['VITE_TOKENS_PER_CHUNK']}")
    
    # Check chunk overlap
    if backend_config['CHUNK_OVERLAP'] == frontend_config['VITE_CHUNK_OVERLAP']:
        print(f"   ✅ CHUNK_OVERLAP matches: {backend_config['CHUNK_OVERLAP']}")
    else:
        print(f"   ❌ CHUNK_OVERLAP mismatch: Backend={backend_config['CHUNK_OVERLAP']}, Frontend={frontend_config['VITE_CHUNK_OVERLAP']}")
    
    # Check chunks to combine
    if backend_config['NUMBER_OF_CHUNKS_TO_COMBINE'] == frontend_config['VITE_CHUNK_TO_COMBINE']:
        print(f"   ✅ CHUNKS_TO_COMBINE matches: {backend_config['NUMBER_OF_CHUNKS_TO_COMBINE']}")
    else:
        print(f"   ❌ CHUNKS_TO_COMBINE mismatch: Backend={backend_config['NUMBER_OF_CHUNKS_TO_COMBINE']}, Frontend={frontend_config['VITE_CHUNK_TO_COMBINE']}")
    
    # Calculate derived values
    print("\n📈 DERIVED VALUES:")
    
    tokens_per_chunk = int(backend_config['TOKENS_PER_CHUNK'])
    chunk_overlap = int(backend_config['CHUNK_OVERLAP'])
    max_token_chunk_size = int(backend_config['MAX_TOKEN_CHUNK_SIZE'])
    
    # Calculate max chunks
    max_chunks = max_token_chunk_size // tokens_per_chunk
    print(f"   Max chunks allowed: {max_chunks}")
    
    # Calculate overlap ratio
    overlap_ratio = (chunk_overlap / tokens_per_chunk) * 100
    print(f"   Overlap ratio: {overlap_ratio:.1f}%")
    
    # Check if overlap ratio is in recommended range
    if 5 <= overlap_ratio <= 25:
        print(f"   ✅ Overlap ratio is in recommended range (5-25%)")
    else:
        print(f"   ⚠️  Overlap ratio is outside recommended range (5-25%)")
    
    # Check backend health
    print("\n🏥 BACKEND HEALTH CHECK:")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
            
            # Test with default parameters
            print("\n🧪 TESTING DEFAULT PARAMETERS:")
            test_data = {
                'token_chunk_size': None,  # Should use env default
                'chunk_overlap': None,     # Should use env default
                'chunks_to_combine': None  # Should use env default
            }
            
            print(f"   Testing with default parameters (None values)")
            print(f"   Expected to use: tokens={tokens_per_chunk}, overlap={chunk_overlap}")
            
        else:
            print(f"   ❌ Backend health check failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot reach backend: {e}")
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURATION TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_chunking_config()
