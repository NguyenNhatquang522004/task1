#!/usr/bin/env python3
"""
Cross-Document Relationships Standalone Server
==============================================

Server hoàn toàn độc lập để phân tích và gán mối quan hệ cross-document.
Chạy trên port 8001, hoàn toàn tách biệt với backend chính.

Core functionality:
- Tìm entity pairs từ documents khác nhau
- Phân tích semantic relationships bằng LLM
- Gán relationships vào Neo4j graph
- Cung cấp thống kê và monitoring
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Global variables
analyzer = None
neo4j_driver = None

# Initialize FastAPI app
app = FastAPI(
    title="Cross-Document Relationships API",
    description="Standalone server for cross-document entity relationship analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_api_response(status: str, message: str, data: Any = None) -> Dict:
    """Create standardized API response"""
    response = {
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    if data is not None:
        response["data"] = data
    return response

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global analyzer, neo4j_driver
    
    print("🚀 Initializing Cross-Document Relationships Server...")
    
    try:
        # Add current directory to path for imports
        current_dir = os.path.dirname(__file__)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Initialize Neo4j connection
        try:
            from neo4j import GraphDatabase
            
            neo4j_uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
            neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
            neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
            
            neo4j_driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_username, neo4j_password)
            )
            
            # Test connection
            with neo4j_driver.session() as session:
                session.run("RETURN 1")
            
            print("✅ Neo4j connected successfully")
            
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            neo4j_driver = None
        
        # Initialize analyzer
        try:
            from src.core.analyzer import CrossDocumentAnalyzer
            analyzer = CrossDocumentAnalyzer()
            await analyzer.initialize()
            print("✅ Cross-document analyzer initialized")
            
        except Exception as e:
            print(f"❌ Analyzer initialization failed: {e}")
            analyzer = None
        
        print("🎯 Cross-Document Relationships Server ready!")
        print("📋 Available endpoints:")
        print("   - POST /analyze - Chạy phân tích cross-document relationships")
        print("   - GET /cross-document-stats - Thống kê relationships hiện tại")
        print("   - GET /entity-pairs - Preview entity pairs tiềm năng")
        print("   - GET /health - Health check")
        print("   - GET /status - Detailed system status")
        
    except Exception as e:
        print(f"💥 Startup failed: {e}")
        logger.exception("Startup error")

@app.get("/health")
async def health_check():
    """Basic health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "analyzer": analyzer is not None,
            "neo4j": neo4j_driver is not None
        }
    }
    
    if neo4j_driver:
        try:
            with neo4j_driver.session() as session:
                session.run("RETURN 1")
            health_status["components"]["neo4j_connection"] = True
        except Exception:
            health_status["components"]["neo4j_connection"] = False
            health_status["status"] = "degraded"
    
    return health_status

@app.get("/status")
async def get_status():
    """Get detailed system status"""
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    try:
        # Get LLM status
        llm_status = analyzer.get_llm_status()
        
        # Get Neo4j info
        neo4j_status = {}
        if neo4j_driver:
            try:
                with neo4j_driver.session() as session:
                    node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                    rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                    
                neo4j_status = {
                    "connected": True,
                    "node_count": node_count,
                    "relationship_count": rel_count
                }
            except Exception as e:
                neo4j_status = {"connected": False, "error": str(e)}
        else:
            neo4j_status = {"connected": False, "reason": "No driver configured"}
        
        return create_api_response(
            "success",
            "System status retrieved",
            {
                "llm_status": llm_status,
                "neo4j_status": neo4j_status,
                "similarity_threshold": analyzer.similarity_threshold,
                "server_uptime": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.exception("Error getting status")
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@app.post("/analyze")
async def analyze_cross_document_relationships(
    max_pairs: int = Form(1000),
    batch_size: int = Form(10),
    similarity_threshold: float = Form(0.75),
    confidence_threshold: float = Form(0.6)
):
    """
    Chạy phân tích và gán mối quan hệ giữa entities từ các documents khác nhau
    
    Quy trình:
    1. Tìm entity pairs từ documents khác nhau có similarity cao
    2. Phân tích semantic relationship bằng LLM
    3. Gán relationship phù hợp vào Neo4j graph
    4. Trả về kết quả thống kê
    """
    global analyzer, neo4j_driver
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    if not neo4j_driver:
        raise HTTPException(status_code=503, detail="Neo4j not connected")
    
    try:
        # Import relationship assigner
        sys.path.insert(0, os.path.dirname(__file__))
        from cross_document_relationship_assigner import CrossDocumentRelationshipAssigner
        
        # Tạo relationship assigner
        assigner = CrossDocumentRelationshipAssigner(
            neo4j_driver=neo4j_driver,
            llm_client=analyzer.llm_client,
            similarity_threshold=similarity_threshold
        )
        
        logger.info(f"Starting cross-document relationship assignment...")
        logger.info(f"Parameters: max_pairs={max_pairs}, batch_size={batch_size}, similarity_threshold={similarity_threshold}")
        
        # Chạy phân tích và gán relationships
        results = await assigner.process_cross_document_relationships(
            max_pairs=max_pairs,
            batch_size=batch_size
        )
        
        # Lấy thống kê sau khi gán
        stats = await assigner.get_cross_document_statistics()
        
        return create_api_response(
            "success",
            f"Successfully assigned {results.get('created_relationships', 0)} cross-document relationships",
            {
                "assignment_results": results,
                "current_statistics": stats,
                "parameters_used": {
                    "max_pairs": max_pairs,
                    "batch_size": batch_size,
                    "similarity_threshold": similarity_threshold,
                    "confidence_threshold": confidence_threshold
                }
            }
        )
        
    except Exception as e:
        logger.exception("Error during cross-document relationship assignment")
        raise HTTPException(status_code=500, detail=f"Relationship assignment failed: {str(e)}")

@app.get("/cross-document-stats")
async def get_cross_document_statistics():
    """
    Lấy thống kê về cross-document relationships hiện tại trong graph
    
    Returns:
    - Số entity pairs có relationships
    - Phân bố các loại relationships
    - Số documents có cross-document connections
    - Top entities có nhiều cross-document connections nhất
    """
    global neo4j_driver
    
    if not neo4j_driver:
        raise HTTPException(status_code=503, detail="Neo4j not connected")
    
    try:
        # Import relationship assigner
        sys.path.insert(0, os.path.dirname(__file__))
        from cross_document_relationship_assigner import CrossDocumentRelationshipAssigner
        
        # Tạo relationship assigner
        assigner = CrossDocumentRelationshipAssigner(
            neo4j_driver=neo4j_driver,
            llm_client=analyzer.llm_client if analyzer else None,
            similarity_threshold=0.75
        )
        
        # Lấy thống kê
        stats = await assigner.get_cross_document_statistics()
        
        return create_api_response(
            "success",
            "Retrieved cross-document statistics",
            stats
        )
        
    except Exception as e:
        logger.exception("Error getting cross-document statistics")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/entity-pairs")
async def get_potential_entity_pairs(
    limit: int = 100,
    similarity_threshold: float = 0.75
):
    """
    Tìm entity pairs potentials từ documents khác nhau có similarity cao
    
    Dùng để preview trước khi chạy analysis chính thức
    """
    global neo4j_driver
    
    if not neo4j_driver:
        raise HTTPException(status_code=503, detail="Neo4j not connected")
    
    try:
        # Import relationship assigner
        sys.path.insert(0, os.path.dirname(__file__))
        from cross_document_relationship_assigner import CrossDocumentRelationshipAssigner
        
        # Tạo relationship assigner
        assigner = CrossDocumentRelationshipAssigner(
            neo4j_driver=neo4j_driver,
            llm_client=analyzer.llm_client if analyzer else None,
            similarity_threshold=similarity_threshold
        )
        
        # Tìm entity pairs
        pairs = await assigner.find_cross_document_entity_pairs(max_pairs=limit)
        
        return create_api_response(
            "success",
            f"Found {len(pairs)} potential entity pairs",
            {
                "entity_pairs": pairs[:limit],
                "total_found": len(pairs),
                "similarity_threshold": similarity_threshold
            }
        )
        
    except Exception as e:
        logger.exception("Error finding entity pairs")
        raise HTTPException(status_code=500, detail=f"Failed to find pairs: {str(e)}")

@app.post("/reset-llm-keys")
async def reset_llm_keys():
    """Reset LLM failed keys for retry"""
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    try:
        analyzer.reset_llm_failed_keys()
        return create_api_response("success", "LLM keys reset successfully")
        
    except Exception as e:
        logger.exception("Error resetting LLM keys")
        raise HTTPException(status_code=500, detail=f"Error resetting LLM keys: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global neo4j_driver
    
    print("🛑 Shutting down Cross-Document Relationships Server...")
    
    if neo4j_driver:
        neo4j_driver.close()
        print("✅ Neo4j driver closed")
    
    print("👋 Server shutdown complete")

if __name__ == "__main__":
    print("🚀 Starting Cross-Document Relationships Standalone Server")
    print("📍 Server will run on: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Different port from main backend
        log_level="info",
        reload=False
    )
