"""
Embedding Model Utilities
"""
import logging
from typing import Tuple, Any
from langchain_huggingface import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class EmbeddingManager:
    """Manages embedding models"""
    
    def __init__(self):
        self._embedding_function = None
    
    def get_embedding_function(self) -> Tuple[Any, str]:
        """Get embedding function and model name"""
        try:
            if self._embedding_function is None:
                self._embedding_function = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
                logger.info(f"Successfully loaded embedding model: {EMBEDDING_MODEL}")
            
            return self._embedding_function, EMBEDDING_MODEL
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            # Fallback to a simple model
            logger.info("Falling back to all-MiniLM-L6-v2")
            fallback_model = "sentence-transformers/all-MiniLM-L6-v2"
            self._embedding_function = HuggingFaceEmbeddings(
                model_name=fallback_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            return self._embedding_function, fallback_model

# Global embedding manager
embedding_manager = EmbeddingManager()

def get_embedding_function() -> Tuple[Any, str]:
    """Get embedding function and model name"""
    return embedding_manager.get_embedding_function()
