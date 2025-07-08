"""
Script để validate chunking parameters và tránh lỗi chunk overlap > chunk size
"""

import os
from dotenv import load_dotenv

def validate_chunking_parameters():
    """Validate chunking parameters từ environment variables"""
    
    # Load từ cả frontend và backend .env
    load_dotenv("frontend/.env")
    load_dotenv("backend/.env") 
    load_dotenv(".env")  # Root .env
    
    print("🔍 CHUNKING PARAMETERS VALIDATION")
    print("=" * 50)
    
    # Frontend parameters
    chunk_size_bytes = int(os.getenv('VITE_CHUNK_SIZE', 5242880))
    chunk_overlap_frontend = int(os.getenv('VITE_CHUNK_OVERLAP', 20))
    tokens_per_chunk = int(os.getenv('VITE_TOKENS_PER_CHUNK', 512))
    chunks_to_combine = int(os.getenv('VITE_CHUNK_TO_COMBINE', 1))
    
    # Backend parameters  
    max_token_chunk_size = int(os.getenv('MAX_TOKEN_CHUNK_SIZE', 2000))
    number_of_chunks_to_combine = int(os.getenv('NUMBER_OF_CHUNKS_TO_COMBINE', 6))
    
    print("📊 Current Configuration:")
    print(f"   Frontend Chunk Size (bytes): {chunk_size_bytes:,}")
    print(f"   Frontend Tokens per Chunk: {tokens_per_chunk}")
    print(f"   Frontend Chunk Overlap: {chunk_overlap_frontend}")
    print(f"   Frontend Chunks to Combine: {chunks_to_combine}")
    print(f"   Backend Max Token Chunk Size: {max_token_chunk_size}")
    print(f"   Backend Chunks to Combine: {number_of_chunks_to_combine}")
    print()
    
    # Validation 1: Overlap < Chunk Size
    print("✅ VALIDATION 1: Chunk Overlap < Tokens per Chunk")
    if chunk_overlap_frontend < tokens_per_chunk:
        print(f"   ✅ OK: {chunk_overlap_frontend} < {tokens_per_chunk}")
    else:
        print(f"   ❌ ERROR: {chunk_overlap_frontend} >= {tokens_per_chunk}")
        print("   💡 Solution: Reduce VITE_CHUNK_OVERLAP or increase VITE_TOKENS_PER_CHUNK")
        return False
    
    # Validation 2: Reasonable overlap ratio
    overlap_ratio = (chunk_overlap_frontend / tokens_per_chunk) * 100
    print(f"\n📊 VALIDATION 2: Overlap Ratio = {overlap_ratio:.1f}%")
    if 5 <= overlap_ratio <= 25:
        print(f"   ✅ GOOD: {overlap_ratio:.1f}% is in recommended range (5-25%)")
    elif overlap_ratio < 5:
        print(f"   ⚠️  LOW: {overlap_ratio:.1f}% might lose context between chunks")
    else:
        print(f"   ⚠️  HIGH: {overlap_ratio:.1f}% might waste processing resources")
    
    # Validation 3: Max chunks calculation
    max_chunks_allowed = max_token_chunk_size // tokens_per_chunk
    print(f"\n🔢 VALIDATION 3: Max Chunks Allowed = {max_chunks_allowed}")
    print(f"   Calculation: {max_token_chunk_size} ÷ {tokens_per_chunk} = {max_chunks_allowed}")
    if max_chunks_allowed >= 2:
        print(f"   ✅ OK: Can create up to {max_chunks_allowed} chunks")
    else:
        print(f"   ❌ ERROR: Can only create {max_chunks_allowed} chunk(s)")
        print("   💡 Solution: Increase MAX_TOKEN_CHUNK_SIZE or decrease VITE_TOKENS_PER_CHUNK")
        return False
    
    # Validation 4: Chunks to combine
    print(f"\n🔗 VALIDATION 4: Chunks to Combine Settings")
    print(f"   Frontend: {chunks_to_combine}")
    print(f"   Backend: {number_of_chunks_to_combine}")
    if chunks_to_combine != number_of_chunks_to_combine:
        print("   ⚠️  WARNING: Frontend and backend have different values!")
        print("   💡 Recommendation: Sync these values for consistency")
    else:
        print("   ✅ OK: Frontend and backend values match")
    
    print(f"\n🎯 RECOMMENDATIONS:")
    print(f"   • Optimal chunk size: 256-512 tokens")
    print(f"   • Optimal overlap: 10-20% of chunk size")
    print(f"   • Current setup: {tokens_per_chunk} tokens with {chunk_overlap_frontend} overlap ({overlap_ratio:.1f}%)")
    
    if tokens_per_chunk >= 256 and 5 <= overlap_ratio <= 25:
        print(f"   ✅ Your configuration looks good!")
    else:
        print(f"   💡 Consider adjusting parameters for better performance")
    
    return True

def suggest_optimal_settings():
    """Suggest optimal chunking settings"""
    print(f"\n🎛️ OPTIMAL SETTINGS SUGGESTIONS:")
    print(f"=" * 50)
    
    suggestions = [
        {
            "name": "Balanced (Recommended)",
            "tokens_per_chunk": 512,
            "chunk_overlap": 50,
            "max_token_chunk_size": 10000,
            "description": "Good balance of context and performance"
        },
        {
            "name": "High Performance", 
            "tokens_per_chunk": 256,
            "chunk_overlap": 25,
            "max_token_chunk_size": 5000,
            "description": "Faster processing, less context"
        },
        {
            "name": "High Quality",
            "tokens_per_chunk": 1024, 
            "chunk_overlap": 100,
            "max_token_chunk_size": 20000,
            "description": "Better context, slower processing"
        }
    ]
    
    for i, config in enumerate(suggestions, 1):
        overlap_ratio = (config["chunk_overlap"] / config["tokens_per_chunk"]) * 100
        max_chunks = config["max_token_chunk_size"] // config["tokens_per_chunk"]
        
        print(f"\n{i}. {config['name']}:")
        print(f"   VITE_TOKENS_PER_CHUNK={config['tokens_per_chunk']}")
        print(f"   VITE_CHUNK_OVERLAP={config['chunk_overlap']}")
        print(f"   MAX_TOKEN_CHUNK_SIZE={config['max_token_chunk_size']}")
        print(f"   → Overlap ratio: {overlap_ratio:.1f}%")
        print(f"   → Max chunks: {max_chunks}")
        print(f"   → {config['description']}")

if __name__ == "__main__":
    print("🔧 LLM GRAPH BUILDER - CHUNKING PARAMETERS VALIDATOR")
    print("=" * 60)
    
    is_valid = validate_chunking_parameters()
    
    if not is_valid:
        print(f"\n❌ VALIDATION FAILED!")
        print(f"   Please fix the configuration before running the application.")
    
    suggest_optimal_settings()
    
    print("=" * 60)
