"""
Core analyzer for cross-document entity relationships
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import asyncio

from ..constants import (
    CROSS_DOC_RELATIONSHIP_PROMPT,
    CROSS_DOC_ENTITIES_QUERY,
    CREATE_CROSS_DOC_RELATIONSHIP_QUERY,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_ANALYSIS_VERSION,
    RELATIONSHIP_TYPES
)
from ..utils.gemini_client import GeminiLLMClient

logger = logging.getLogger(__name__)

class CrossDocumentAnalyzer:
    """Analyzes relationships between entities across different documents"""
    
    def __init__(self, llm_client=None, neo4j_driver=None, similarity_threshold=DEFAULT_SIMILARITY_THRESHOLD, use_gemini=True):
        """
        Initialize the cross-document analyzer
        
        Args:
            llm_client: LLM client for relationship analysis (optional if use_gemini=True)
            neo4j_driver: Neo4j database driver
            similarity_threshold: Minimum similarity score for entity pairs
            use_gemini: Whether to use Gemini 2.0 Flash client with key rotation
        """
        # Initialize LLM client
        if use_gemini:
            try:
                self.llm_client = GeminiLLMClient()
                logger.info("Initialized Gemini 2.0 Flash client with API key rotation")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
                if llm_client:
                    self.llm_client = llm_client
                    logger.info("Falling back to provided LLM client")
                else:
                    raise Exception(f"Failed to initialize any LLM client: {str(e)}")
        else:
            if not llm_client:
                raise ValueError("llm_client must be provided when use_gemini=False")
            self.llm_client = llm_client
            
        self.neo4j_driver = neo4j_driver
        self.similarity_threshold = similarity_threshold
        self.use_gemini = use_gemini
        
    async def find_similar_entities(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Find entities from different documents with high similarity scores
        
        Args:
            limit: Maximum number of entity pairs to return
            
        Returns:
            List of entity pairs with similarity scores
        """
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(
                    CROSS_DOC_ENTITIES_QUERY,
                    similarity_threshold=self.similarity_threshold,
                    limit=limit
                )
                
                entity_pairs = []
                for record in result:
                    entity_pairs.append({
                        "entity1_id": record["entity1_id"],
                        "entity1_name": record["entity1_name"],
                        "entity2_id": record["entity2_id"], 
                        "entity2_name": record["entity2_name"],
                        "document1": record["document1"],
                        "document2": record["document2"],
                        "similarity": record["similarity"]
                    })
                    
                logger.info(f"Found {len(entity_pairs)} similar entity pairs")
                return entity_pairs
                
        except Exception as e:
            logger.error(f"Error finding similar entities: {str(e)}")
            raise
            
    async def get_entity_context(self, entity_id: str) -> Optional[str]:
        """
        Get context information for an entity
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Context string or None if not found
        """
        try:
            query = """
            MATCH (e:Entity {id: $entity_id})
            OPTIONAL MATCH (e)-[:HAS_CHUNK]->(c:Chunk)
            RETURN e.description as description, 
                   collect(c.text)[0..3] as chunk_texts
            """
            
            with self.neo4j_driver.session() as session:
                result = session.run(query, entity_id=entity_id)
                record = result.single()
                
                if not record:
                    return None
                    
                context_parts = []
                if record["description"]:
                    context_parts.append(f"Description: {record['description']}")
                    
                if record["chunk_texts"]:
                    chunk_text = " ".join(record["chunk_texts"])  # Limit context length
                    context_parts.append(f"Context: {chunk_text}")
                    
                return " | ".join(context_parts) if context_parts else None
                
        except Exception as e:
            logger.error(f"Error getting entity context for {entity_id}: {str(e)}")
            return None
            
    async def analyze_relationship(self, entity_pair: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze the relationship between two entities using LLM
        
        Args:
            entity_pair: Dictionary containing entity pair information
            
        Returns:
            Relationship analysis result or None if analysis fails
        """
        try:
            # Get context for both entities
            entity1_context = await self.get_entity_context(entity_pair["entity1_id"])
            entity2_context = await self.get_entity_context(entity_pair["entity2_id"])
            
            if not entity1_context or not entity2_context:
                logger.warning(f"Missing context for entity pair: {entity_pair['entity1_name']} - {entity_pair['entity2_name']}")
                return None
                
            # Prepare LLM prompt
            prompt = CROSS_DOC_RELATIONSHIP_PROMPT.format(
                entity1_name=entity_pair["entity1_name"],
                entity1_context=entity1_context,
                document1_name=entity_pair["document1"],
                entity2_name=entity_pair["entity2_name"],
                entity2_context=entity2_context,
                document2_name=entity_pair["document2"]
            )
            
            # Get LLM analysis
            response = await self.llm_client.generate_response(prompt)
            
            # Parse JSON response
            try:
                analysis = json.loads(response)
                
                # Validate response format
                required_fields = ["relationship_type", "confidence", "explanation"]
                if not all(field in analysis for field in required_fields):
                    logger.error(f"Invalid LLM response format: {analysis}")
                    return None
                    
                # Validate relationship type
                if analysis["relationship_type"] not in RELATIONSHIP_TYPES:
                    logger.error(f"Invalid relationship type: {analysis['relationship_type']}")
                    return None
                    
                # Add original entity pair info
                analysis.update({
                    "entity1_id": entity_pair["entity1_id"],
                    "entity2_id": entity_pair["entity2_id"],
                    "entity1_name": entity_pair["entity1_name"],
                    "entity2_name": entity_pair["entity2_name"],
                    "document1": entity_pair["document1"],
                    "document2": entity_pair["document2"],
                    "similarity_score": entity_pair["similarity"]
                })
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing relationship: {str(e)}")
            return None
            
    async def create_relationship(self, analysis: Dict[str, Any]) -> bool:
        """
        Create cross-document relationship in Neo4j
        
        Args:
            analysis: Relationship analysis result
            
        Returns:
            True if relationship created successfully, False otherwise
        """
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(
                    CREATE_CROSS_DOC_RELATIONSHIP_QUERY,
                    entity1_id=analysis["entity1_id"],
                    entity2_id=analysis["entity2_id"],
                    relationship_type=analysis["relationship_type"],
                    confidence=float(analysis["confidence"]),
                    explanation=analysis["explanation"],
                    direction=analysis.get("direction", "entity1_to_entity2"),
                    analysis_version=DEFAULT_ANALYSIS_VERSION
                )
                
                relationship = result.single()
                if relationship:
                    logger.info(f"Created relationship: {analysis['entity1_name']} -> {analysis['entity2_name']} ({analysis['relationship_type']})")
                    return True
                else:
                    logger.error(f"Failed to create relationship in database")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating relationship: {str(e)}")
            return False
            
    async def process_batch(self, entity_pairs: List[Dict[str, Any]], 
                          confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> Dict[str, int]:
        """
        Process a batch of entity pairs for relationship analysis
        
        Args:
            entity_pairs: List of entity pairs to analyze
            confidence_threshold: Minimum confidence for creating relationships
            
        Returns:
            Statistics about processed relationships
        """
        stats = {
            "total_pairs": len(entity_pairs),
            "analyzed": 0,
            "created": 0,
            "skipped_low_confidence": 0,
            "failed": 0
        }
        
        for entity_pair in entity_pairs:
            try:
                # Use enhanced retry logic for Gemini
                if self.use_gemini:
                    analysis = await self.analyze_relationship_with_retry(entity_pair, max_retries=3)
                else:
                    analysis = await self.analyze_relationship(entity_pair)
                
                if not analysis:
                    stats["failed"] += 1
                    continue
                    
                stats["analyzed"] += 1
                
                # Check confidence threshold
                if float(analysis["confidence"]) < confidence_threshold:
                    stats["skipped_low_confidence"] += 1
                    logger.info(f"Skipping low confidence relationship: {analysis['entity1_name']} - {analysis['entity2_name']} (confidence: {analysis['confidence']})")
                    continue
                    
                # Create relationship
                if await self.create_relationship(analysis):
                    stats["created"] += 1
                else:
                    stats["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Error processing entity pair: {str(e)}")
                stats["failed"] += 1
                
        return stats
        
    async def analyze_all_relationships(self, 
                                     batch_size: int = DEFAULT_BATCH_SIZE,
                                     confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
                                     max_pairs: int = 1000) -> Dict[str, Any]:
        """
        Analyze relationships for all similar entity pairs
        
        Args:
            batch_size: Size of processing batches
            confidence_threshold: Minimum confidence for creating relationships
            max_pairs: Maximum number of entity pairs to process
            
        Returns:
            Overall processing statistics
        """
        start_time = datetime.now()
        logger.info(f"Starting cross-document relationship analysis with similarity threshold: {self.similarity_threshold}")
        
        try:
            # Find similar entities
            entity_pairs = await self.find_similar_entities(limit=max_pairs)
            
            if not entity_pairs:
                logger.info("No similar entity pairs found")
                return {
                    "success": True,
                    "total_pairs": 0,
                    "total_analyzed": 0,
                    "total_created": 0,
                    "total_skipped": 0,
                    "total_failed": 0,
                    "processing_time": 0
                }
                
            # Process in batches
            overall_stats = {
                "total_pairs": len(entity_pairs),
                "total_analyzed": 0,
                "total_created": 0,
                "total_skipped": 0,
                "total_failed": 0
            }
            
            for i in range(0, len(entity_pairs), batch_size):
                batch = entity_pairs[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} pairs)")
                
                batch_stats = await self.process_batch(batch, confidence_threshold)
                
                overall_stats["total_analyzed"] += batch_stats["analyzed"]
                overall_stats["total_created"] += batch_stats["created"]
                overall_stats["total_skipped"] += batch_stats["skipped_low_confidence"]
                overall_stats["total_failed"] += batch_stats["failed"]
                
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            overall_stats.update({
                "success": True,
                "processing_time": processing_time,
                "similarity_threshold": self.similarity_threshold,
                "confidence_threshold": confidence_threshold
            })
            
            logger.info(f"Cross-document analysis completed in {processing_time:.2f} seconds")
            logger.info(f"Results: {overall_stats['total_created']} relationships created from {overall_stats['total_pairs']} entity pairs")
            
            return overall_stats
            
        except Exception as e:
            logger.error(f"Error in analyze_all_relationships: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
        
    async def analyze_relationship_with_retry(self, entity_pair: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Analyze relationship with enhanced error handling and retry logic
        
        Args:
            entity_pair: Dictionary containing entity pair information
            max_retries: Maximum number of retry attempts
            
        Returns:
            Relationship analysis result or None if analysis fails
        """
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                result = await self.analyze_relationship(entity_pair)
                if result:
                    return result
                    
                # If result is None but no exception, it's a validation issue
                logger.warning(f"Analysis returned None for attempt {attempt + 1}: {entity_pair['entity1_name']} - {entity_pair['entity2_name']}")
                
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Log the error
                logger.warning(f"Analysis attempt {attempt + 1} failed: {str(e)}")
                
                # Check if it's a retryable error
                if any(keyword in error_msg for keyword in ['rate', 'quota', 'timeout', 'network', 'connection']):
                    if attempt < max_retries - 1:
                        # Wait before retry with exponential backoff
                        wait_time = (2 ** attempt) * 1.0
                        logger.info(f"Retrying analysis in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        continue
                
                # For non-retryable errors, break immediately
                if any(keyword in error_msg for keyword in ['auth', 'invalid', 'key']):
                    logger.error(f"Authentication error, aborting retries: {str(e)}")
                    break
        
        # All retries failed
        if last_exception:
            logger.error(f"All retry attempts failed for {entity_pair['entity1_name']} - {entity_pair['entity2_name']}: {str(last_exception)}")
        
        return None
    
    def get_llm_status(self) -> Dict[str, Any]:
        """Get LLM client status information"""
        if hasattr(self.llm_client, 'get_status'):
            return self.llm_client.get_status()
        else:
            return {"status": "unknown", "client_type": "generic"}
    
    def reset_llm_failed_keys(self):
        """Reset failed API keys if using Gemini client"""
        if hasattr(self.llm_client, 'reset_failed_keys'):
            self.llm_client.reset_failed_keys()
            logger.info("Reset failed API keys")
        else:
            logger.warning("LLM client does not support key reset")
