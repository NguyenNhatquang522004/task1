"""
FastAPI routes for cross-document entity relationships
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from ..core.analyzer import CrossDocumentAnalyzer
from ..constants import (
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_BATCH_SIZE,
    RESPONSE_CODES,
    GET_EXISTING_RELATIONSHIPS_QUERY,
    DELETE_CROSS_DOC_RELATIONSHIPS_QUERY
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cross-document", tags=["cross-document-relationships"])

# Pydantic models
class AnalysisRequest(BaseModel):
    similarity_threshold: float = Field(default=DEFAULT_SIMILARITY_THRESHOLD, ge=0.0, le=1.0)
    confidence_threshold: float = Field(default=DEFAULT_CONFIDENCE_THRESHOLD, ge=0.0, le=1.0)
    batch_size: int = Field(default=DEFAULT_BATCH_SIZE, ge=1, le=1000)
    max_pairs: int = Field(default=1000, ge=1, le=10000)

class RelationshipFilter(BaseModel):
    document1: Optional[str] = None
    document2: Optional[str] = None
    relationship_type: Optional[str] = None

class DeleteRequest(BaseModel):
    document1: Optional[str] = None
    document2: Optional[str] = None

class RelationshipResponse(BaseModel):
    entity1_name: str
    entity2_name: str
    document1: str
    document2: str
    relationship_type: str
    confidence: float
    explanation: str
    direction: Optional[str]
    created_at: str

class AnalysisStatus(BaseModel):
    success: bool
    total_pairs: int
    total_analyzed: int
    total_created: int
    total_skipped: int
    total_failed: int
    processing_time: float
    similarity_threshold: Optional[float] = None
    confidence_threshold: Optional[float] = None
    error: Optional[str] = None

# Dependency injection placeholders - these will be set during integration
def get_analyzer() -> CrossDocumentAnalyzer:
    """Dependency to get the analyzer instance"""
    # This will be implemented during integration with the main app
    raise NotImplementedError("Analyzer dependency not configured")

def get_neo4j_driver():
    """Dependency to get Neo4j driver"""
    # This will be implemented during integration with the main app
    raise NotImplementedError("Neo4j driver dependency not configured")

@router.post("/analyze", response_model=AnalysisStatus)
async def analyze_relationships(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    analyzer: CrossDocumentAnalyzer = Depends(get_analyzer)
):
    """
    Start cross-document relationship analysis
    
    This endpoint initiates the analysis of relationships between entities
    from different documents. The analysis runs in the background.
    """
    try:
        logger.info(f"Starting cross-document analysis with parameters: {request.dict()}")
        
        # Update analyzer similarity threshold
        analyzer.similarity_threshold = request.similarity_threshold
        
        # Run analysis
        result = await analyzer.analyze_all_relationships(
            batch_size=request.batch_size,
            confidence_threshold=request.confidence_threshold,
            max_pairs=request.max_pairs
        )
        
        return AnalysisStatus(**result)
        
    except Exception as e:
        logger.error(f"Error in analyze_relationships: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/relationships", response_model=List[RelationshipResponse])
async def get_relationships(
    filter_params: RelationshipFilter = Depends(),
    neo4j_driver = Depends(get_neo4j_driver)
):
    """
    Get existing cross-document relationships with optional filtering
    """
    try:
        with neo4j_driver.session() as session:
            result = session.run(
                GET_EXISTING_RELATIONSHIPS_QUERY,
                document1=filter_params.document1,
                document2=filter_params.document2,
                relationship_type=filter_params.relationship_type
            )
            
            relationships = []
            for record in result:
                relationships.append(RelationshipResponse(
                    entity1_name=record["entity1_name"],
                    entity2_name=record["entity2_name"],
                    document1=record["document1"],
                    document2=record["document2"],
                    relationship_type=record["relationship_type"],
                    confidence=record["confidence"],
                    explanation=record["explanation"],
                    direction=record["direction"],
                    created_at=str(record["created_at"])
                ))
                
        logger.info(f"Retrieved {len(relationships)} relationships")
        return relationships
        
    except Exception as e:
        logger.error(f"Error retrieving relationships: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Failed to retrieve relationships: {str(e)}"
        )

@router.get("/similar-entities")
async def get_similar_entities(
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    limit: int = 100,
    analyzer: CrossDocumentAnalyzer = Depends(get_analyzer)
):
    """
    Get similar entity pairs across documents without analyzing relationships
    """
    try:
        # Update analyzer threshold
        analyzer.similarity_threshold = similarity_threshold
        
        entity_pairs = await analyzer.find_similar_entities(limit=limit)
        
        return {
            "success": True,
            "entity_pairs": entity_pairs,
            "count": len(entity_pairs),
            "similarity_threshold": similarity_threshold
        }
        
    except Exception as e:
        logger.error(f"Error finding similar entities: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Failed to find similar entities: {str(e)}"
        )

@router.delete("/relationships")
async def delete_relationships(
    request: DeleteRequest,
    neo4j_driver = Depends(get_neo4j_driver)
):
    """
    Delete cross-document relationships with optional filtering by document
    """
    try:
        with neo4j_driver.session() as session:
            result = session.run(
                DELETE_CROSS_DOC_RELATIONSHIPS_QUERY,
                document1=request.document1,
                document2=request.document2
            )
            
            record = result.single()
            deleted_count = record["deleted_count"] if record else 0
            
        logger.info(f"Deleted {deleted_count} cross-document relationships")
        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Successfully deleted {deleted_count} relationships"
        }
        
    except Exception as e:
        logger.error(f"Error deleting relationships: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Failed to delete relationships: {str(e)}"
        )

@router.get("/stats")
async def get_relationship_stats(neo4j_driver = Depends(get_neo4j_driver)):
    """
    Get statistics about cross-document relationships
    """
    try:
        stats_query = """
        MATCH ()-[r:CROSS_DOC_RELATIONSHIP]->()
        WITH r.type as type, count(*) as count, avg(r.confidence) as avg_confidence
        RETURN type, count, avg_confidence
        ORDER BY count DESC
        """
        
        total_query = """
        MATCH ()-[r:CROSS_DOC_RELATIONSHIP]->()
        RETURN count(r) as total_relationships
        """
        
        with neo4j_driver.session() as session:
            # Get type statistics
            type_stats = []
            result = session.run(stats_query)
            for record in result:
                type_stats.append({
                    "relationship_type": record["type"],
                    "count": record["count"],
                    "average_confidence": round(record["avg_confidence"], 3)
                })
            
            # Get total count
            total_result = session.run(total_query)
            total_record = total_result.single()
            total_relationships = total_record["total_relationships"] if total_record else 0
            
        return {
            "success": True,
            "total_relationships": total_relationships,
            "relationship_types": type_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting relationship stats: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Failed to get relationship statistics: {str(e)}"
        )

@router.get("/documents")
async def get_documents_with_relationships(neo4j_driver = Depends(get_neo4j_driver)):
    """
    Get list of documents that have cross-document relationships
    """
    try:
        query = """
        MATCH (e1:Entity)-[r:CROSS_DOC_RELATIONSHIP]->(e2:Entity)
        MATCH (e1)-[:PART_OF]->(d1:Document)
        MATCH (e2)-[:PART_OF]->(d2:Document)
        WITH d1.fileName as doc1, d2.fileName as doc2, count(r) as relationship_count
        RETURN doc1, doc2, relationship_count
        ORDER BY relationship_count DESC
        """
        
        with neo4j_driver.session() as session:
            result = session.run(query)
            
            document_pairs = []
            all_documents = set()
            
            for record in result:
                doc1, doc2 = record["doc1"], record["doc2"]
                document_pairs.append({
                    "document1": doc1,
                    "document2": doc2,
                    "relationship_count": record["relationship_count"]
                })
                all_documents.add(doc1)
                all_documents.add(doc2)
                
        return {
            "success": True,
            "document_pairs": document_pairs,
            "all_documents": sorted(list(all_documents)),
            "total_pairs": len(document_pairs)
        }
        
    except Exception as e:
        logger.error(f"Error getting documents with relationships: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Failed to get documents: {str(e)}"
        )

@router.get("/llm-status")
async def get_llm_status(analyzer: CrossDocumentAnalyzer = Depends(get_analyzer)):
    """
    Get LLM client status (especially useful for Gemini key rotation monitoring)
    """
    try:
        status = analyzer.get_llm_status()
        return {
            "success": True,
            "llm_status": status,
            "using_gemini": analyzer.use_gemini if hasattr(analyzer, 'use_gemini') else False
        }
    except Exception as e:
        logger.error(f"Error getting LLM status: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Failed to get LLM status: {str(e)}"
        )

@router.post("/reset-failed-keys")
async def reset_failed_keys(analyzer: CrossDocumentAnalyzer = Depends(get_analyzer)):
    """
    Reset failed API keys (useful when keys become available again)
    """
    try:
        analyzer.reset_llm_failed_keys()
        status = analyzer.get_llm_status()
        
        return {
            "success": True,
            "message": "Failed API keys have been reset",
            "current_status": status
        }
    except Exception as e:
        logger.error(f"Error resetting failed keys: {str(e)}")
        raise HTTPException(
            status_code=RESPONSE_CODES["INTERNAL_ERROR"],
            detail=f"Failed to reset keys: {str(e)}"
        )
