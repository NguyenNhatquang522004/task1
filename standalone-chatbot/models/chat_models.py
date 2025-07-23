"""
Chat LLM Models Integration
"""
import os
import logging
from typing import Tuple, Any
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages different LLM models"""
    
    def __init__(self):
        self.models = {
            # OpenAI Models
            "openai_gpt_3.5": self._create_openai_gpt35,
            "openai_gpt_4o": self._create_openai_gpt4o,
            "openai_gpt_4o_mini": self._create_openai_gpt4o_mini,
            
            # Google Gemini Models
            "gemini_1.5_pro": self._create_gemini_15_pro,
            "gemini_1.5_flash": self._create_gemini_15_flash,
            "gemini_2.0_flash": self._create_gemini_20_flash,
            
            # Groq Models
            "groq_llama3_70b": self._create_groq_llama3_70b,
            
            # Anthropic Models
            "anthropic_claude_3_5_sonnet": self._create_anthropic_claude_35_sonnet,
            
            # Ollama Models
            "ollama_llama3": self._create_ollama_llama3,
        }
    
    def get_llm(self, model: str) -> Tuple[Any, str]:
        """Get LLM instance and model name"""
        try:
            if model not in self.models:
                logger.warning(f"Model {model} not found, using default gemini_2.0_flash")
                model = "gemini_2.0_flash"
            
            llm_instance = self.models[model]()
            logger.info(f"Successfully created LLM instance for model: {model}")
            return llm_instance, model
            
        except Exception as e:
            logger.error(f"Error creating LLM for model {model}: {e}")
            # Fallback to a simple model
            logger.info("Falling back to gemini_2.0_flash")
            return self._create_gemini_20_flash(), "gemini_2.0_flash"
    
    def _create_openai_gpt35(self):
        """Create OpenAI GPT-3.5 model"""
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_openai_gpt4o(self):
        """Create OpenAI GPT-4o model"""
        return ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_openai_gpt4o_mini(self):
        """Create OpenAI GPT-4o mini model"""
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_gemini_15_pro(self):
        """Create Gemini 1.5 Pro model"""
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_gemini_15_flash(self):
        """Create Gemini 1.5 Flash model"""
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_gemini_20_flash(self):
        """Create Gemini 2.0 Flash model"""
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_groq_llama3_70b(self):
        """Create Groq Llama3 70B model"""
        return ChatGroq(
            model="llama3-70b-8192",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_anthropic_claude_35_sonnet(self):
        """Create Anthropic Claude 3.5 Sonnet model"""
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0,
            max_tokens=1000
        )
    
    def _create_ollama_llama3(self):
        """Create Ollama Llama3 model"""
        return ChatOllama(
            model="llama3",
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0
        )

# Global LLM manager instance
llm_manager = LLMManager()

def get_llm(model: str) -> Tuple[Any, str]:
    """Get LLM instance and model name"""
    return llm_manager.get_llm(model)
