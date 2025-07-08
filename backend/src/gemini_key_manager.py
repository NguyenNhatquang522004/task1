"""
Gemini API Key Rotation Manager
Manages multiple Gemini API keys with automatic rotation for better rate limiting
"""

import os
import logging
import random
import time
from typing import List, Optional
from threading import Lock
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

class GeminiAPIKeyManager:
    """Manages rotation of multiple Gemini API keys"""
    
    def __init__(self, api_keys: List[str]):
        """
        Initialize with list of API keys
        
        Args:
            api_keys: List of Gemini API keys
        """
        self.api_keys = api_keys.copy()
        self.current_index = 0
        self.failed_keys = set()
        self.lock = Lock()
        self.last_rotation_time = time.time()
        self.rotation_interval = 300  # 5 minutes
        
        if not api_keys:
            raise ValueError("At least one API key must be provided")
            
        logging.info(f"Initialized Gemini API Key Manager with {len(api_keys)} keys")
    
    def get_current_key(self) -> str:
        """Get current active API key"""
        with self.lock:
            return self.api_keys[self.current_index]
    
    def rotate_key(self, mark_current_as_failed: bool = False) -> str:
        """
        Rotate to next available API key
        
        Args:
            mark_current_as_failed: Mark current key as failed before rotating
            
        Returns:
            Next available API key
        """
        with self.lock:
            if mark_current_as_failed:
                current_key = self.api_keys[self.current_index]
                self.failed_keys.add(current_key)
                logging.warning(f"Marked API key as failed: {current_key[:10]}...")
            
            # Find next available key
            for _ in range(len(self.api_keys)):
                self.current_index = (self.current_index + 1) % len(self.api_keys)
                next_key = self.api_keys[self.current_index]
                
                if next_key not in self.failed_keys:
                    logging.info(f"Rotated to API key: {next_key[:10]}...")
                    return next_key
            
            # If all keys failed, reset failed keys and start over
            logging.warning("All API keys marked as failed, resetting...")
            self.failed_keys.clear()
            self.current_index = 0
            return self.api_keys[self.current_index]
    
    def reset_failed_keys(self):
        """Reset all failed keys (give them another chance)"""
        with self.lock:
            self.failed_keys.clear()
            logging.info("Reset all failed API keys")
    
    def get_available_key_count(self) -> int:
        """Get number of available (non-failed) keys"""
        with self.lock:
            return len(self.api_keys) - len(self.failed_keys)
    
    def should_rotate(self) -> bool:
        """Check if it's time for automatic rotation"""
        return time.time() - self.last_rotation_time > self.rotation_interval
    
    def auto_rotate_if_needed(self) -> str:
        """Automatically rotate if interval has passed"""
        if self.should_rotate():
            with self.lock:
                self.last_rotation_time = time.time()
            return self.rotate_key()
        return self.get_current_key()

# Global API key manager
_api_key_manager: Optional[GeminiAPIKeyManager] = None

def initialize_gemini_keys():
    """Initialize Gemini API key manager from environment or default keys"""
    global _api_key_manager
    
    # Default API keys provided by user
    DEFAULT_API_KEYS = [
        "AIzaSyDOFVqDIv5v3HxoyzQ-usbvBGTZaWxh3Rc",
        "AIzaSyA3zxa_7NDyLY3hFzeoJdywUwqByZzelHQ", 
        "AIzaSyCBA1YjwxWhZL2VekhVkLVnEYsJgwGXqSM",
        "AIzaSyCAZhdVckycMoiYxBM_wTzJTLAf9szqC88",
        "AIzaSyBQdl16VKs03zycqRTqk74QAb2fvV90s9U",
        "AIzaSyC-pD5jPvFYRb6RvOWU6yEt1opZgUR7rZQ",
        "AIzaSyDdh_aoKbtYEFAYGAlhEOZckiVhE5EjCdA",
        "AIzaSyCptWmxP3waaG9m2lHIFWqhcsPrQb3VrNQ",
        "AIzaSyCeiFcW1j3xwe7thHvrGWBHRe0-FiNjKp0",
        "AIzaSyByZSt9_Pmi7E8h4fzQbZImpLg2FMSuc6k",
        "AIzaSyC1MkbxKGOC78jDuPeGVtisDC-eeFUTkLw",
        "AIzaSyCChRUlfhu7FGHPvP4c2tSCYANX_Y-K1B0",
        "AIzaSyDdNRekp5gOVl-UjfGY5SFbxwWKTJ7KSFE",
        "AIzaSyBW-wAJLawggMMfWWmNCbsyKI2l3ugXuzM",
        "AIzaSyAYQrH_z4wIFSQBr2qx3s3ZAuNYHMkOCoc",
        "AIzaSyBd1PqATF-pm4X1cAwyebRUSGrbE7kqDXA",
        "AIzaSyD24LAKX7oBgeS8oSYwFmXydzTDvdGWfhw",
        "AIzaSyD0WoyfAFOacuJDe93ZVt7lxjeGxVNqW30",
        "AIzaSyBgixYB4_75RqT8lwsbFJjNY9Avvj9i2co",
        "AIzaSyAPx-sl7Og9zbOx9LNrJsQ2MWSZTLdzRcY",
        "AIzaSyDpKTtGZT1GiOE2DIHnvK906OtCnjQbGpg",
        "AIzaSyDkdn8xEhOc8Jgsr8FGBUnjrxvXqEzQ31M",
        "AIzaSyA8Zuq_hOvS9IzlA7cUDxnjR0YIdTugIW0",
        "AIzaSyAt72ou0_-i6Q2-r_0RfuqHLEisP3K_bTQ",
        "AIzaSyD-H8exPyfNc_c0OhTTPpyUB81tXgvP-Zc",
        "AIzaSyB0EQN8PQtHE6qc-e-I1KCRlU5li6RNz88",
        "AIzaSyAgpUnIFNtWbNvVGTL_pG99mR-cuKTwPTg",
        "AIzaSyCAm2qZj8NzIRoh81ZRffHgqLwvGwcf-tU",
        "AIzaSyC8m0kD65ESwMXSNGrRFGoQnQuHzuhh-oE",
        "AIzaSyCJYvWhet8rIHSiFXaP6-Fyui-b7L37tGc",
        "AIzaSyD0IVLuXXU36I3r3TFVH9QGXQIapAbLolk",
        "AIzaSyBoPepjPC54RhBz3sA-hN0TgdumzOE5EOo"
    ]
    
    # Try to get keys from environment first
    env_keys = os.getenv('GEMINI_API_KEYS')
    if env_keys:
        api_keys = [key.strip() for key in env_keys.split(',') if key.strip()]
        logging.info(f"Loaded {len(api_keys)} Gemini API keys from environment")
    else:
        api_keys = DEFAULT_API_KEYS
        logging.info(f"Using default {len(api_keys)} Gemini API keys")
    
    _api_key_manager = GeminiAPIKeyManager(api_keys)
    return _api_key_manager

def get_gemini_key_manager() -> GeminiAPIKeyManager:
    """Get the global Gemini API key manager"""
    global _api_key_manager
    if _api_key_manager is None:
        initialize_gemini_keys()
    return _api_key_manager

def create_gemini_llm(model_name: str = "gemini-1.5-flash", temperature: float = 0.0):
    """
    Create Gemini LLM with automatic API key rotation
    
    Args:
        model_name: Gemini model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
        temperature: Temperature for generation
        
    Returns:
        ChatGoogleGenerativeAI instance
    """
    key_manager = get_gemini_key_manager()
    
    # Auto-rotate if needed
    current_key = key_manager.auto_rotate_if_needed()
    
    try:
        # Configure genai with current key
        genai.configure(api_key=current_key)
        
        # Create LangChain Gemini instance
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=current_key,
            convert_system_message_to_human=True
        )
        
        logging.info(f"Created Gemini LLM with model: {model_name}, key: {current_key[:10]}...")
        return llm
        
    except Exception as e:
        logging.error(f"Failed to create Gemini LLM with current key: {e}")
        
        # Try rotating to next key
        next_key = key_manager.rotate_key(mark_current_as_failed=True)
        
        try:
            genai.configure(api_key=next_key)
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=next_key,
                convert_system_message_to_human=True
            )
            
            logging.info(f"Successfully created Gemini LLM with rotated key: {next_key[:10]}...")
            return llm
            
        except Exception as e2:
            logging.error(f"Failed to create Gemini LLM with rotated key: {e2}")
            raise Exception(f"Failed to create Gemini LLM with any available key: {e2}")

def test_gemini_key(api_key: str) -> bool:
    """Test if a Gemini API key is working - Only used on demand"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test.")
        return True
    except Exception as e:
        logging.warning(f"API key test failed for {api_key[:10]}...: {e}")
        return False
