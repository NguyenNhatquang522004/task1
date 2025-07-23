"""
FastAPI Application - Standalone Chatbot
"""
import os
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from models.qa_models import ChatRequest, ChatResponse, ClearChatRequest, ClearChatResponse
from utils.neo4j_utils import create_graph_connection, close_graph_connection
from services.chat_service import ChatService
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, ALLOWED_LLMS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
graph = None
chat_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global graph, chat_service
    
    # Startup
    try:
        logger.info("Starting up chatbot application...")
        
        # Initialize Neo4j connection
        graph = create_graph_connection(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        
        # Initialize chat service
        chat_service = ChatService(graph)
        
        logger.info("Application startup completed successfully")
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        if graph:
            close_graph_connection(graph)
        logger.info("Application shutdown completed")

# Create FastAPI application
app = FastAPI(
    title="LLM Graph Builder - Standalone Chatbot",
    description="Standalone chatbot service with vector and graph search capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "LLM Graph Builder - Standalone Chatbot API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Neo4j connection
        if graph and chat_service:
            result = graph.query("RETURN 1 as test")
            if result:
                return {
                    "status": "healthy",
                    "message": "All services are running",
                    "neo4j_connected": True
                }
        
        return {
            "status": "unhealthy", 
            "message": "Services not initialized",
            "neo4j_connected": False
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "neo4j_connected": False
        }

@app.get("/models")
async def get_available_models():
    """Get list of available LLM models"""
    try:
        return {
            "models": list(ALLOWED_LLMS.keys()),
            "model_details": ALLOWED_LLMS
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Validate inputs
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        if request.model not in ALLOWED_LLMS:
            raise HTTPException(
                status_code=400, 
                detail=f"Model {request.model} not supported. Available models: {list(ALLOWED_LLMS.keys())}"
            )
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Processing chat request - Session: {session_id}, Model: {request.model}, Mode: {request.mode}")
        
        # Process chat request
        result = chat_service.process_chat(
            question=request.question,
            model=request.model,
            mode=request.mode,
            document_names=request.document_names,
            session_id=session_id
        )
        
        # Convert to response model
        response = ChatResponse(
            session_id=result.get("session_id", session_id),
            message=result.get("message", ""),
            model=result.get("model", request.model),
            sources=result.get("sources", []),
            response_time=result.get("response_time", 0),
            mode=result.get("mode", request.mode),
            nodedetails=result.get("nodedetails", {}),
            entities=result.get("entities", {}),
            total_tokens=result.get("total_tokens", 0)
        )
        
        logger.info(f"Chat processed successfully - Session: {session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/clear_chat", response_model=ClearChatResponse)
async def clear_chat_endpoint(request: ClearChatRequest):
    """Clear chat history endpoint"""
    try:
        if not request.session_id:
            raise HTTPException(status_code=400, detail="Session ID is required")
        
        logger.info(f"Clearing chat history for session: {request.session_id}")
        
        result = chat_service.clear_chat_history(request.session_id)
        
        response = ClearChatResponse(
            session_id=result.get("session_id", request.session_id),
            message=result.get("message", "Chat history cleared"),
            user=result.get("user", "chatbot")
        )
        
        logger.info(f"Chat history cleared for session: {request.session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
