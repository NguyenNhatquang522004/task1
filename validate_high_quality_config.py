#!/usr/bin/env python3
"""
Script validate cấu hình chunking mới (High Quality)
Kiểm tra tất cả tham số chunking trong frontend/.env và backend/.env
"""

import os
from dotenv import load_dotenv


def validate_chunking_config():
    """Validate chunking configuration sau khi cập nhật"""
    
    print("🔍 VALIDATING CHUNKING CONFIGURATION - HIGH QUALITY")
    print("=" * 60)
    
    # Load frontend .env
    frontend_env_path = r"c:\edu\task1\llm-graph-builder\frontend\.env"
    backend_env_path = r"c:\edu\task1\llm-graph-builder\backend\.env"
    
    # Validate frontend config
    print("\n📂 FRONTEND CONFIGURATION:")
    print("-" * 30)
    
    if not os.path.exists(frontend_env_path):
        print(f"❌ Frontend .env file not found: {frontend_env_path}")
        return False
    
    # Load frontend environment
    load_dotenv(frontend_env_path, override=True)
    
    frontend_tokens_per_chunk = os.getenv('VITE_TOKENS_PER_CHUNK', 'NOT_SET')
    frontend_chunk_overlap = os.getenv('VITE_CHUNK_OVERLAP', 'NOT_SET')
    frontend_chunk_to_combine = os.getenv('VITE_CHUNK_TO_COMBINE', 'NOT_SET')
    frontend_chunk_size = os.getenv('VITE_CHUNK_SIZE', 'NOT_SET')
    
    print(f"VITE_TOKENS_PER_CHUNK: {frontend_tokens_per_chunk}")
    print(f"VITE_CHUNK_OVERLAP: {frontend_chunk_overlap}")
    print(f"VITE_CHUNK_TO_COMBINE: {frontend_chunk_to_combine}")
    print(f"VITE_CHUNK_SIZE: {frontend_chunk_size}")
    
    # Validate backend config
    print("\n🔧 BACKEND CONFIGURATION:")
    print("-" * 30)
    
    if not os.path.exists(backend_env_path):
        print(f"❌ Backend .env file not found: {backend_env_path}")
        return False
    
    # Load backend environment (override previous)
    load_dotenv(backend_env_path, override=True)
    
    backend_tokens_per_chunk = os.getenv('TOKENS_PER_CHUNK', 'NOT_SET')
    backend_chunk_overlap = os.getenv('CHUNK_OVERLAP', 'NOT_SET')
    backend_chunks_to_combine = os.getenv('NUMBER_OF_CHUNKS_TO_COMBINE', 'NOT_SET')
    backend_max_token_chunk = os.getenv('MAX_TOKEN_CHUNK_SIZE', 'NOT_SET')
    
    print(f"TOKENS_PER_CHUNK: {backend_tokens_per_chunk}")
    print(f"CHUNK_OVERLAP: {backend_chunk_overlap}")
    print(f"NUMBER_OF_CHUNKS_TO_COMBINE: {backend_chunks_to_combine}")
    print(f"MAX_TOKEN_CHUNK_SIZE: {backend_max_token_chunk}")
    
    # Validate High Quality Configuration
    print("\n🎯 HIGH QUALITY VALIDATION:")
    print("-" * 30)
    
    expected_config = {
        'TOKENS_PER_CHUNK': '1024',
        'CHUNK_OVERLAP': '100',
        'CHUNKS_TO_COMBINE': '6',
        'MAX_TOKEN_CHUNK_SIZE': '20000'
    }
    
    errors = []
    
    # Check frontend values
    if frontend_tokens_per_chunk != expected_config['TOKENS_PER_CHUNK']:
        errors.append(f"❌ Frontend VITE_TOKENS_PER_CHUNK: Expected {expected_config['TOKENS_PER_CHUNK']}, got {frontend_tokens_per_chunk}")
    else:
        print(f"✅ Frontend VITE_TOKENS_PER_CHUNK: {frontend_tokens_per_chunk}")
    
    if frontend_chunk_overlap != expected_config['CHUNK_OVERLAP']:
        errors.append(f"❌ Frontend VITE_CHUNK_OVERLAP: Expected {expected_config['CHUNK_OVERLAP']}, got {frontend_chunk_overlap}")
    else:
        print(f"✅ Frontend VITE_CHUNK_OVERLAP: {frontend_chunk_overlap}")
    
    if frontend_chunk_to_combine.strip() != expected_config['CHUNKS_TO_COMBINE']:
        errors.append(f"❌ Frontend VITE_CHUNK_TO_COMBINE: Expected {expected_config['CHUNKS_TO_COMBINE']}, got {frontend_chunk_to_combine}")
    else:
        print(f"✅ Frontend VITE_CHUNK_TO_COMBINE: {frontend_chunk_to_combine}")
    
    # Check backend values
    if backend_tokens_per_chunk != expected_config['TOKENS_PER_CHUNK']:
        errors.append(f"❌ Backend TOKENS_PER_CHUNK: Expected {expected_config['TOKENS_PER_CHUNK']}, got {backend_tokens_per_chunk}")
    else:
        print(f"✅ Backend TOKENS_PER_CHUNK: {backend_tokens_per_chunk}")
    
    if backend_chunk_overlap != expected_config['CHUNK_OVERLAP']:
        errors.append(f"❌ Backend CHUNK_OVERLAP: Expected {expected_config['CHUNK_OVERLAP']}, got {backend_chunk_overlap}")
    else:
        print(f"✅ Backend CHUNK_OVERLAP: {backend_chunk_overlap}")
    
    if backend_chunks_to_combine.strip() != expected_config['CHUNKS_TO_COMBINE']:
        errors.append(f"❌ Backend NUMBER_OF_CHUNKS_TO_COMBINE: Expected {expected_config['CHUNKS_TO_COMBINE']}, got {backend_chunks_to_combine}")
    else:
        print(f"✅ Backend NUMBER_OF_CHUNKS_TO_COMBINE: {backend_chunks_to_combine}")
    
    if backend_max_token_chunk != expected_config['MAX_TOKEN_CHUNK_SIZE']:
        errors.append(f"❌ Backend MAX_TOKEN_CHUNK_SIZE: Expected {expected_config['MAX_TOKEN_CHUNK_SIZE']}, got {backend_max_token_chunk}")
    else:
        print(f"✅ Backend MAX_TOKEN_CHUNK_SIZE: {backend_max_token_chunk}")
    
    # Validate chunk_overlap < tokens_per_chunk
    print("\n🔍 LOGICAL VALIDATION:")
    print("-" * 30)
    
    try:
        tokens_per_chunk = int(frontend_tokens_per_chunk)
        chunk_overlap = int(frontend_chunk_overlap)
        
        if chunk_overlap >= tokens_per_chunk:
            errors.append(f"❌ CHUNK_OVERLAP ({chunk_overlap}) >= TOKENS_PER_CHUNK ({tokens_per_chunk})")
        else:
            print(f"✅ CHUNK_OVERLAP ({chunk_overlap}) < TOKENS_PER_CHUNK ({tokens_per_chunk})")
            
    except ValueError as e:
        errors.append(f"❌ Invalid numeric values: {e}")
    
    # Check configuration profile
    print("\n📊 CONFIGURATION PROFILE:")
    print("-" * 30)
    
    if (frontend_tokens_per_chunk == '1024' and 
        frontend_chunk_overlap == '100' and 
        backend_max_token_chunk == '20000'):
        print("🎯 HIGH QUALITY PROFILE ✅")
        print("   - Tokens per chunk: 1024 (Good balance)")
        print("   - Chunk overlap: 100 (~10% overlap)")
        print("   - Max token chunk size: 20000 (Large context)")
    else:
        print("⚠️  CUSTOM PROFILE")
    
    # Final result
    print("\n" + "=" * 60)
    
    if errors:
        print("❌ VALIDATION FAILED:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print("✅ VALIDATION PASSED: All chunking parameters are correctly configured for High Quality mode")
        return True


if __name__ == "__main__":
    try:
        success = validate_chunking_config()
        if success:
            print("\n✅ Configuration is ready for High Quality chunking!")
            print("🚀 You can now restart the backend and frontend to apply the new settings.")
        else:
            print("\n❌ Please fix the configuration errors and run this script again.")
            
    except Exception as e:
        print(f"\n❌ Error during validation: {e}")
        import traceback
        traceback.print_exc()
