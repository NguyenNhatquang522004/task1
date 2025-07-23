"""
QA Request/Response Models
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Chat request model"""
    question: str = Field(..., description="User question")
    model: str = Field(default="gemini_2.0_flash", description="LLM model to use")
    mode: str = Field(default="vector", description="Chat mode (vector, graph, entity+vector, fulltext+vector)")
    document_names: Optional[List[str]] = Field(default=None, description="List of document names to filter")
    session_id: str = Field(default="default", description="Session ID for chat history")
    
class ChatInfo(BaseModel):
    """Chat response info"""
    sources: List[str] = Field(default_factory=list, description="Source documents used")
    model: str = Field(..., description="Model used for generation")
    nodedetails: Dict[str, Any] = Field(default_factory=dict, description="Node details from search")
    total_tokens: int = Field(default=0, description="Total tokens used")
    response_time: float = Field(default=0.0, description="Response time in seconds")
    mode: str = Field(..., description="Chat mode used")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Entities extracted")
    cypher_query: Optional[str] = Field(default=None, description="Cypher query used (graph mode)")
    context: Optional[str] = Field(default=None, description="Context used (graph mode)")
    error: Optional[str] = Field(default=None, description="Error message if any")

class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str = Field(..., description="Session ID")
    message: str = Field(..., description="AI response message")
    info: ChatInfo = Field(..., description="Additional information")
    user: str = Field(default="chatbot", description="Response user type")

class ClearChatRequest(BaseModel):
    """Clear chat request model"""
    session_id: str = Field(..., description="Session ID to clear")

class ClearChatResponse(BaseModel):
    """Clear chat response model"""
    session_id: str = Field(..., description="Session ID that was cleared")
    message: str = Field(..., description="Confirmation message")
    user: str = Field(default="chatbot", description="Response user type")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")

class ModelsResponse(BaseModel):
    """Available models response"""
    models: List[str] = Field(..., description="List of available models")
    default_model: str = Field(..., description="Default model")

class APIResponse(BaseModel):
    """Generic API response wrapper"""
    status: str = Field(..., description="Response status (Success/Failed)")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")
