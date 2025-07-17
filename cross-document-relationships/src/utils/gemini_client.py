"""
Gemini 2.0 Flash client with API key rotation and error handling
"""

import asyncio
import logging
import random
import time
from typing import Dict, Any, Optional, List
import json

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Fix import path - config is at package root, not in src
try:
    from ...config.settings import config
except ImportError:
    # Fallback for standalone execution
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from config.settings import config

logger = logging.getLogger(__name__)

class GeminiClient:
    """Gemini 2.0 Flash client with multiple API key support and error handling"""
    
    def __init__(self):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not found. Install with: pip install google-generativeai")
            
        self.api_keys = config.GEMINI_API_KEYS.copy()
        self.current_key_index = 0
        self.max_retries = config.MAX_RETRIES
        self.retry_delay = config.RETRY_DELAY
        self.model_name = config.LLM_MODEL
        self.temperature = config.LLM_TEMPERATURE
        self.max_tokens = config.LLM_MAX_TOKENS
        
        # Key failure tracking
        self.failed_keys = set()
        self.key_last_used = {}
        
        if not self.api_keys:
            raise ValueError("No Gemini API keys configured. Set GEMINI_API_KEYS environment variable.")
            
        logger.info(f"Initialized Gemini client with {len(self.api_keys)} API keys")
        
        # Safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    
    def _get_next_api_key(self) -> Optional[str]:
        """Get the next available API key"""
        available_keys = [key for key in self.api_keys if key not in self.failed_keys]
        
        if not available_keys:
            # Reset failed keys if all have failed
            logger.warning("All API keys have failed, resetting failure tracking")
            self.failed_keys.clear()
            available_keys = self.api_keys.copy()
        
        if not available_keys:
            return None
            
        # Round-robin with randomization
        key = available_keys[self.current_key_index % len(available_keys)]
        self.current_key_index = (self.current_key_index + 1) % len(available_keys)
        
        return key
    
    def _mark_key_failed(self, api_key: str):
        """Mark an API key as failed"""
        self.failed_keys.add(api_key)
        logger.warning(f"Marked API key as failed: {api_key[:10]}...")
    
    def _configure_genai(self, api_key: str):
        """Configure genai with the given API key"""
        genai.configure(api_key=api_key)
        self.key_last_used[api_key] = time.time()
    
    async def generate_response(self, prompt: str) -> str:
        """
        Generate response using Gemini with API key rotation
        
        Args:
            prompt: Input prompt for analysis
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If all API keys fail or other critical errors
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            api_key = self._get_next_api_key()
            
            if not api_key:
                raise Exception("No available API keys")
                
            try:
                # Configure with current API key
                self._configure_genai(api_key)
                
                # Create model
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    safety_settings=self.safety_settings
                )
                
                # Generate content
                logger.debug(f"Attempting request with API key: {api_key[:10]}... (attempt {attempt + 1})")
                
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.temperature,
                        max_output_tokens=self.max_tokens,
                        candidate_count=1,
                    )
                )
                
                if response.text:
                    logger.debug(f"Successful response from API key: {api_key[:10]}...")
                    return response.text.strip()
                else:
                    logger.warning(f"Empty response from API key: {api_key[:10]}...")
                    raise Exception("Empty response from Gemini")
                    
            except Exception as e:
                error_msg = str(e).lower()
                last_exception = e
                
                # Check for rate limiting or quota errors
                if any(keyword in error_msg for keyword in ['quota', 'rate', 'limit', 'exceeded']):
                    logger.warning(f"Rate limit/quota error with key {api_key[:10]}...: {str(e)}")
                    self._mark_key_failed(api_key)
                
                # Check for authentication errors
                elif any(keyword in error_msg for keyword in ['auth', 'invalid', 'key', 'unauthorized']):
                    logger.error(f"Authentication error with key {api_key[:10]}...: {str(e)}")
                    self._mark_key_failed(api_key)
                
                # Check for safety/content filtering
                elif any(keyword in error_msg for keyword in ['safety', 'blocked', 'filtered']):
                    logger.warning(f"Content filtered by safety settings: {str(e)}")
                    # Don't mark key as failed for safety filtering
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    else:
                        raise Exception(f"Content consistently blocked by safety filters: {str(e)}")
                
                # Other errors - temporary failure
                else:
                    logger.warning(f"Temporary error with key {api_key[:10]}...: {str(e)}")
                
                # Wait before retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        
        # All attempts failed
        raise Exception(f"All API key attempts failed. Last error: {str(last_exception)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status information"""
        return {
            "total_keys": len(self.api_keys),
            "failed_keys": len(self.failed_keys),
            "available_keys": len(self.api_keys) - len(self.failed_keys),
            "current_model": self.model_name,
            "last_used_times": {
                f"{key[:10]}...": time.time() - last_used 
                for key, last_used in self.key_last_used.items()
            }
        }
    
    def reset_failed_keys(self):
        """Reset all failed key tracking"""
        self.failed_keys.clear()
        logger.info("Reset all failed key tracking")

class GeminiLLMClient:
    """Wrapper class for compatibility with existing analyzer"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response - compatible with existing analyzer interface"""
        return await self.gemini_client.generate_response(prompt)
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return self.gemini_client.get_status()
    
    def reset_failed_keys(self):
        """Reset failed keys"""
        self.gemini_client.reset_failed_keys()
