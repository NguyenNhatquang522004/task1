"""
Configuration settings for cross-document relationship analysis
"""

import os
import random
from typing import Dict, Any, List

class CrossDocumentConfig:
    """Configuration class for cross-document analysis"""
    
    # Analysis settings
    DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("CROSS_DOC_SIMILARITY_THRESHOLD", "0.75"))
    DEFAULT_CONFIDENCE_THRESHOLD = float(os.getenv("CROSS_DOC_CONFIDENCE_THRESHOLD", "0.6"))
    DEFAULT_BATCH_SIZE = int(os.getenv("CROSS_DOC_BATCH_SIZE", "50"))
    DEFAULT_MAX_PAIRS = int(os.getenv("CROSS_DOC_MAX_PAIRS", "1000"))
    
    # Gemini 2.0 Flash settings
    LLM_MODEL = os.getenv("CROSS_DOC_LLM_MODEL", "gemini-2.0-flash")
    LLM_TEMPERATURE = float(os.getenv("CROSS_DOC_LLM_TEMPERATURE", "0.1"))
    LLM_MAX_TOKENS = int(os.getenv("CROSS_DOC_LLM_MAX_TOKENS", "2048"))
    
    # Multiple Gemini API Keys for rotation
    GEMINI_API_KEYS = [
        key.strip() for key in os.getenv("GEMINI_API_KEYS", "").split(",") 
        if key.strip()
    ]
    
    # Fallback to single key if multiple keys not provided
    if not GEMINI_API_KEYS:
        single_key = os.getenv("GEMINI_API_KEY", "")
        if single_key:
            GEMINI_API_KEYS = [single_key]
    
    # API retry settings
    MAX_RETRIES = int(os.getenv("CROSS_DOC_MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("CROSS_DOC_RETRY_DELAY", "1.0"))
    
    # Gemini-specific settings
    GEMINI_SAFETY_SETTINGS = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    
    # Processing settings
    MAX_CONTEXT_LENGTH = int(os.getenv("CROSS_DOC_MAX_CONTEXT_LENGTH", "500"))
    ENABLE_PARALLEL_PROCESSING = os.getenv("CROSS_DOC_PARALLEL_PROCESSING", "true").lower() == "true"
    
    # Logging settings
    LOG_LEVEL = os.getenv("CROSS_DOC_LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("CROSS_DOC_LOG_FILE", "cross_document_analysis.log")
    
    # Analysis version for tracking
    ANALYSIS_VERSION = os.getenv("CROSS_DOC_ANALYSIS_VERSION", "1.0")
    
    @classmethod
    def get_random_api_key(cls) -> str:
        """Get a random API key from the available keys"""
        if not cls.GEMINI_API_KEYS:
            raise ValueError("No Gemini API keys configured")
        return random.choice(cls.GEMINI_API_KEYS)
    
    @classmethod
    def get_gemini_config(cls) -> Dict[str, Any]:
        """Get Gemini-specific configuration"""
        return {
            "model": cls.LLM_MODEL,
            "temperature": cls.LLM_TEMPERATURE,
            "max_output_tokens": cls.LLM_MAX_TOKENS,
            "safety_settings": cls.GEMINI_SAFETY_SETTINGS,
            "api_keys": cls.GEMINI_API_KEYS,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY
        }
    
    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get LLM configuration dictionary (legacy compatibility)"""
        return cls.get_gemini_config()
    
    @classmethod
    def get_analysis_config(cls) -> Dict[str, Any]:
        """Get analysis configuration dictionary"""
        return {
            "similarity_threshold": cls.DEFAULT_SIMILARITY_THRESHOLD,
            "confidence_threshold": cls.DEFAULT_CONFIDENCE_THRESHOLD,
            "batch_size": cls.DEFAULT_BATCH_SIZE,
            "max_pairs": cls.DEFAULT_MAX_PAIRS,
            "max_context_length": cls.MAX_CONTEXT_LENGTH,
            "parallel_processing": cls.ENABLE_PARALLEL_PROCESSING,
            "analysis_version": cls.ANALYSIS_VERSION
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration values"""
        try:
            # Check threshold ranges
            if not (0.0 <= cls.DEFAULT_SIMILARITY_THRESHOLD <= 1.0):
                raise ValueError(f"Invalid similarity threshold: {cls.DEFAULT_SIMILARITY_THRESHOLD}")
                
            if not (0.0 <= cls.DEFAULT_CONFIDENCE_THRESHOLD <= 1.0):
                raise ValueError(f"Invalid confidence threshold: {cls.DEFAULT_CONFIDENCE_THRESHOLD}")
                
            # Check positive integers
            if cls.DEFAULT_BATCH_SIZE <= 0:
                raise ValueError(f"Invalid batch size: {cls.DEFAULT_BATCH_SIZE}")
                
            if cls.DEFAULT_MAX_PAIRS <= 0:
                raise ValueError(f"Invalid max pairs: {cls.DEFAULT_MAX_PAIRS}")
                
            if cls.MAX_CONTEXT_LENGTH <= 0:
                raise ValueError(f"Invalid max context length: {cls.MAX_CONTEXT_LENGTH}")
                
            # Check LLM settings
            if cls.LLM_TEMPERATURE < 0.0 or cls.LLM_TEMPERATURE > 2.0:
                raise ValueError(f"Invalid LLM temperature: {cls.LLM_TEMPERATURE}")
                
            if cls.LLM_MAX_TOKENS <= 0:
                raise ValueError(f"Invalid LLM max tokens: {cls.LLM_MAX_TOKENS}")
                
            return True
            
        except ValueError as e:
            print(f"Configuration validation error: {e}")
            return False

# Global config instance
config = CrossDocumentConfig()

# Validate configuration on import
if not config.validate_config():
    raise ValueError("Invalid cross-document analysis configuration")
