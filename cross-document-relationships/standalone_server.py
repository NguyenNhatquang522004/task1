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
import time
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

# Pydantic models
from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    mode: str  # "automatic" or "manual"
    similarity_threshold: float = 0.75
    max_pairs: Optional[int] = 500
    batch_size: Optional[int] = 10
    entity_pairs: Optional[List[Dict[str, Any]]] = None

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

def create_api_response(status: str, message: str, data: Any = None):
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
            analyzer = CrossDocumentAnalyzer(
                neo4j_driver=neo4j_driver,
                use_gemini=True,
                similarity_threshold=0.75
            )
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
        
        # Auto-start cross-document analysis if enabled
        auto_start = os.getenv('AUTO_START_ANALYSIS', 'false').lower() == 'true'
        if auto_start and neo4j_driver:
            print("\n🤖 AUTO_START_ANALYSIS enabled - Starting automatic relationship assignment...")
            asyncio.create_task(auto_analyze_relationships())
        else:
            print("\n📋 Manual mode: Call POST /analyze to start relationship assignment")
            print("💡 Set AUTO_START_ANALYSIS=true in .env for automatic startup analysis")
        
    except Exception as e:
        print(f"💥 Startup failed: {e}")
        logger.exception("Startup error")

async def auto_analyze_relationships():
    """Automatically analyze cross-document relationships on startup"""
    global analyzer, neo4j_driver
    
    try:
        # Wait a bit for server to fully start
        await asyncio.sleep(5)
        
        print("\n🔍 Starting automatic cross-document relationship analysis...")
        
        # Import relationship assigner
        from cross_document_relationship_assigner import CrossDocumentRelationshipAssigner
        
        # Default parameters for auto analysis
        max_pairs = int(os.getenv('AUTO_MAX_PAIRS', '1000'))
        batch_size = int(os.getenv('AUTO_BATCH_SIZE', '10'))
        similarity_threshold = float(os.getenv('AUTO_SIMILARITY_THRESHOLD', '0.75'))
        
        print(f"⚙️  Auto analysis parameters:")
        print(f"   - Max pairs: {max_pairs}")
        print(f"   - Batch size: {batch_size}")
        print(f"   - Similarity threshold: {similarity_threshold}")
        
        # Create relationship assigner
        assigner = CrossDocumentRelationshipAssigner(
            neo4j_driver=neo4j_driver,
            llm_client=analyzer.llm_client,
            similarity_threshold=similarity_threshold
        )
        
        # Run analysis
        results = await assigner.process_cross_document_relationships(
            max_pairs=max_pairs,
            batch_size=batch_size
        )
        
        # Get final statistics
        stats = await assigner.get_cross_document_statistics()
        
        print(f"\n✅ Automatic analysis completed!")
        print(f"🔗 Created relationships: {results.get('created_relationships', 0)}")
        print(f"📊 Processed pairs: {results.get('processed_pairs', 0)}")
        print(f"📈 Success rate: {results.get('success_rate', 0):.1%}")
        print(f"📋 Total cross-document relationships: {stats.get('cross_document_relationships', 0)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Auto analysis failed: {e}")
        logger.exception("Auto analysis error")

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "service": "Cross-Document Relationships API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "analyze": "POST /analyze",
            "similar_entities": "GET /similar-entities",
            "status": "GET /status",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global analyzer, neo4j_driver
    
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

@app.get("/similar-entities")
async def get_similar_entities(
    limit: int = 100,
    threshold: Optional[float] = None
):
    """Get similar entity pairs from different documents"""
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    if not neo4j_driver:
        raise HTTPException(status_code=503, detail="Neo4j not connected")
    
    try:
        # Update threshold if provided
        if threshold:
            analyzer.similarity_threshold = threshold
        
        # Find similar entities
        similar_entities = await analyzer.find_similar_entities(limit=limit)
        
        return create_api_response(
            "success",
            f"Found {len(similar_entities)} similar entity pairs",
            {
                "entity_pairs": similar_entities,
                "count": len(similar_entities),
                "threshold_used": analyzer.similarity_threshold
            }
        )
        
    except Exception as e:
        logger.exception("Error finding similar entities")
        raise HTTPException(status_code=500, detail=f"Error finding similar entities: {str(e)}")

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

@app.post("/reset-llm-keys")
async def reset_llm_keys():
    """Reset failed LLM API keys"""
    global analyzer
    
    if not analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    try:
        analyzer.reset_llm_failed_keys()
        return create_api_response("success", "LLM keys reset successfully")
        
    except Exception as e:
        logger.exception("Error resetting LLM keys")
        raise HTTPException(status_code=500, detail=f"Error resetting LLM keys: {str(e)}")

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
        pairs = await assigner.find_cross_document_entity_pairs()
        
        # Giới hạn kết quả
        limited_pairs = pairs[:limit]
        
        return create_api_response(
            "success",
            f"Found {len(pairs)} potential entity pairs",
            {
                "entity_pairs": limited_pairs,
                "total_found": len(pairs),
                "similarity_threshold": similarity_threshold
            }
        )
        
    except Exception as e:
        logger.exception("Error finding entity pairs")
        raise HTTPException(status_code=500, detail=f"Failed to find pairs: {str(e)}")

@app.post("/analyze")
async def run_cross_document_analysis(request: AnalysisRequest):
    """
    Chạy phân tích cross-document relationships
    
    Mode options:
    - "automatic": Tự động tìm và phân tích tất cả entity pairs có similarity cao
    - "manual": Phân tích specific entity pairs được cung cấp
    """
    global neo4j_driver, analyzer
    
    if not neo4j_driver:
        raise HTTPException(status_code=503, detail="Neo4j not connected")
    
    if not analyzer or not analyzer.llm_client:
        raise HTTPException(status_code=503, detail="LLM not configured")
    
    try:
        # Import relationship assigner
        sys.path.insert(0, os.path.dirname(__file__))
        from cross_document_relationship_assigner import CrossDocumentRelationshipAssigner
        
        # Tạo relationship assigner
        assigner = CrossDocumentRelationshipAssigner(
            neo4j_driver=neo4j_driver,
            llm_client=analyzer.llm_client,
            similarity_threshold=request.similarity_threshold
        )
        
        start_time = time.time()
        
        if request.mode == "automatic":
            # Automatic mode: tự tìm và phân tích
            logger.info("Running automatic cross-document analysis...")
            
            # Tìm entity pairs
            pairs = await assigner.find_cross_document_entity_pairs()
            
            # Giới hạn số lượng nếu cần
            if request.max_pairs:
                pairs = pairs[:request.max_pairs]
            
            # Phân tích relationships
            results = await assigner.analyze_and_create_relationships(
                entity_pairs=pairs,
                batch_size=request.batch_size or 10
            )
            
            analysis_info = {
                "mode": "automatic",
                "pairs_found": len(pairs),
                "pairs_analyzed": len(results.get('analyzed_pairs', [])),
                "relationships_created": results.get('relationships_created', 0),
                "processing_time": round(time.time() - start_time, 2)
            }
            
        elif request.mode == "manual":
            # Manual mode: phân tích entity pairs được chỉ định
            if not request.entity_pairs:
                raise HTTPException(
                    status_code=400, 
                    detail="Manual mode requires entity_pairs to be specified"
                )
            
            logger.info(f"Running manual analysis on {len(request.entity_pairs)} pairs...")
            
            # Phân tích relationships cho pairs được chỉ định
            results = await assigner.analyze_and_create_relationships(
                entity_pairs=request.entity_pairs,
                batch_size=request.batch_size or 10
            )
            
            analysis_info = {
                "mode": "manual",
                "pairs_specified": len(request.entity_pairs),
                "pairs_analyzed": len(results.get('analyzed_pairs', [])),
                "relationships_created": results.get('relationships_created', 0),
                "processing_time": round(time.time() - start_time, 2)
            }
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid mode. Use 'automatic' or 'manual'"
            )
        
        logger.info(f"Cross-document analysis completed: {analysis_info}")
        
        return create_api_response(
            "success",
            f"Cross-document analysis completed in {analysis_info['processing_time']} seconds",
            {
                "analysis_summary": analysis_info,
                "detailed_results": results
            }
        )
        
    except Exception as e:
        logger.exception("Error during cross-document analysis")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
    print("📍 Server will run on: http://localhost:8002")
    print("📚 API Documentation: http://localhost:8002/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,  # Different port from main backend
        log_level="info",
        reload=False
    )
