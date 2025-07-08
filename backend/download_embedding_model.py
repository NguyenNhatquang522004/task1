#!/usr/bin/env python3
"""
Download and cache embedding model for offline use
Run this script when you have internet connection to pre-download the model
"""

import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_embedding_model():
    """Download and cache the embedding model"""
    try:
        logger.info("🔄 Downloading embedding model...")
        
        # Import here to avoid circular imports
        from sentence_transformers import SentenceTransformer
        
        # Create cache directory
        cache_dir = Path(__file__).parent / "embedding_cache"
        cache_dir.mkdir(exist_ok=True)
        
        # Download and cache the model
        model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder=str(cache_dir)
        )
        
        # Test the model
        test_embedding = model.encode("This is a test sentence.")
        logger.info(f"✅ Model downloaded successfully! Embedding dimension: {len(test_embedding)}")
        
        # Save model info
        info_file = cache_dir / "model_info.txt"
        with open(info_file, 'w') as f:
            f.write(f"Model: all-MiniLM-L6-v2\n")
            f.write(f"Dimension: {len(test_embedding)}\n")
            f.write(f"Cache directory: {cache_dir}\n")
        
        logger.info(f"📁 Model cached in: {cache_dir}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to download model: {e}")
        return False

def test_offline_mode():
    """Test if model works in offline mode"""
    try:
        logger.info("🔍 Testing offline mode...")
        
        # Set offline mode
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["HF_HUB_OFFLINE"] = "1"
        
        from langchain_huggingface import HuggingFaceEmbeddings
        
        cache_dir = Path(__file__).parent / "embedding_cache"
        
        embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder=str(cache_dir),
            model_kwargs={'local_files_only': True}
        )
        
        # Test embedding
        test_text = "This is a test sentence for offline mode."
        embedding = embeddings.embed_query(test_text)
        
        logger.info(f"✅ Offline mode test successful! Embedding dimension: {len(embedding)}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Offline mode test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Embedding Model Download Script")
    print("=" * 50)
    
    # Download model
    success = download_embedding_model()
    
    if success:
        # Test offline mode
        test_offline_mode()
        
        print("\n✅ Setup complete!")
        print("💡 The backend should now work offline with cached embeddings.")
    else:
        print("\n❌ Setup failed!")
        print("💡 Backend will use fallback embeddings.")
