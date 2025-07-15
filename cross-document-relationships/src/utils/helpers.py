"""
Utility functions for cross-document relationship analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration for cross-document analysis
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('cross_document_analysis.log')
        ]
    )

def validate_relationship_type(relationship_type: str) -> bool:
    """
    Validate if relationship type is supported
    
    Args:
        relationship_type: Type to validate
        
    Returns:
        True if valid, False otherwise
    """
    from ..constants import RELATIONSHIP_TYPES
    return relationship_type in RELATIONSHIP_TYPES.keys()

def format_analysis_result(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format analysis result for consistent output
    
    Args:
        analysis: Raw analysis result
        
    Returns:
        Formatted analysis result
    """
    if not analysis:
        return {}
        
    return {
        "entity_pair": {
            "entity1": {
                "id": analysis.get("entity1_id"),
                "name": analysis.get("entity1_name"),
                "document": analysis.get("document1")
            },
            "entity2": {
                "id": analysis.get("entity2_id"),
                "name": analysis.get("entity2_name"),
                "document": analysis.get("document2")
            }
        },
        "relationship": {
            "type": analysis.get("relationship_type"),
            "confidence": analysis.get("confidence"),
            "explanation": analysis.get("explanation"),
            "direction": analysis.get("direction"),
            "similarity_score": analysis.get("similarity_score")
        },
        "timestamp": datetime.now().isoformat()
    }

def calculate_processing_stats(start_time: datetime, end_time: datetime, 
                             total_pairs: int, created: int) -> Dict[str, Any]:
    """
    Calculate processing statistics
    
    Args:
        start_time: Processing start time
        end_time: Processing end time
        total_pairs: Total entity pairs processed
        created: Number of relationships created
        
    Returns:
        Processing statistics
    """
    processing_time = (end_time - start_time).total_seconds()
    
    stats = {
        "processing_time_seconds": round(processing_time, 2),
        "total_pairs": total_pairs,
        "relationships_created": created,
        "success_rate": round((created / total_pairs * 100), 2) if total_pairs > 0 else 0,
        "pairs_per_second": round(total_pairs / processing_time, 2) if processing_time > 0 else 0
    }
    
    return stats

def batch_list(items: List[Any], batch_size: int) -> List[List[Any]]:
    """
    Split a list into batches of specified size
    
    Args:
        items: List to batch
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    batches = []
    for i in range(0, len(items), batch_size):
        batches.append(items[i:i + batch_size])
    return batches

def sanitize_entity_name(name: str) -> str:
    """
    Sanitize entity name for safe processing
    
    Args:
        name: Raw entity name
        
    Returns:
        Sanitized name
    """
    if not name:
        return ""
        
    # Remove excessive whitespace and control characters
    sanitized = " ".join(name.strip().split())
    
    # Limit length to prevent excessive context
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."
        
    return sanitized

def extract_confidence_score(llm_response: str) -> Optional[float]:
    """
    Extract confidence score from LLM response
    
    Args:
        llm_response: Raw LLM response
        
    Returns:
        Confidence score or None if not found
    """
    try:
        # Try to parse as JSON first
        data = json.loads(llm_response)
        if "confidence" in data:
            return float(data["confidence"])
    except (json.JSONDecodeError, ValueError, KeyError):
        pass
    
    # Fallback: look for confidence patterns in text
    import re
    patterns = [
        r'confidence["\s]*:[\s]*([0-9]*\.?[0-9]+)',
        r'confidence[\s]*=[\s]*([0-9]*\.?[0-9]+)',
        r'score["\s]*:[\s]*([0-9]*\.?[0-9]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, llm_response, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
                
    return None

def create_processing_report(stats: Dict[str, Any], 
                           similarity_threshold: float,
                           confidence_threshold: float) -> str:
    """
    Create a human-readable processing report
    
    Args:
        stats: Processing statistics
        similarity_threshold: Similarity threshold used
        confidence_threshold: Confidence threshold used
        
    Returns:
        Formatted report string
    """
    report = f"""
Cross-Document Relationship Analysis Report
==========================================

Processing Parameters:
- Similarity Threshold: {similarity_threshold}
- Confidence Threshold: {confidence_threshold}

Results:
- Total Entity Pairs: {stats.get('total_pairs', 0)}
- Pairs Analyzed: {stats.get('total_analyzed', 0)}
- Relationships Created: {stats.get('total_created', 0)}
- Low Confidence Skipped: {stats.get('total_skipped', 0)}
- Failed Analyses: {stats.get('total_failed', 0)}

Performance:
- Processing Time: {stats.get('processing_time', 0):.2f} seconds
- Success Rate: {(stats.get('total_created', 0) / max(stats.get('total_pairs', 1), 1) * 100):.1f}%

Status: {'✓ Completed Successfully' if stats.get('success', False) else '✗ Failed'}
"""
    
    if stats.get('error'):
        report += f"\nError: {stats['error']}"
        
    return report.strip()

def validate_neo4j_connection(driver) -> bool:
    """
    Validate Neo4j database connection
    
    Args:
        driver: Neo4j driver instance
        
    Returns:
        True if connection is valid, False otherwise
    """
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            return record is not None and record["test"] == 1
    except Exception as e:
        logger.error(f"Neo4j connection validation failed: {str(e)}")
        return False

def get_document_entity_count(driver, document_name: str) -> int:
    """
    Get the number of entities in a specific document
    
    Args:
        driver: Neo4j driver instance
        document_name: Name of the document
        
    Returns:
        Number of entities in the document
    """
    try:
        query = """
        MATCH (e:Entity)-[:PART_OF]->(d:Document {fileName: $document_name})
        RETURN count(e) as entity_count
        """
        
        with driver.session() as session:
            result = session.run(query, document_name=document_name)
            record = result.single()
            return record["entity_count"] if record else 0
            
    except Exception as e:
        logger.error(f"Error getting entity count for document {document_name}: {str(e)}")
        return 0
