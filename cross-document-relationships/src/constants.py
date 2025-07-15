"""
Constants for cross-document entity relationships analysis
"""

# Relationship types
RELATIONSHIP_TYPES = {
    "PREREQUISITE": "prerequisite",
    "EQUIVALENT": "equivalent", 
    "RELATED": "related",
    "CONTAINS": "contains",
    "UNRELATED": "unrelated"
}

# LLM Prompt for relationship analysis
CROSS_DOC_RELATIONSHIP_PROMPT = """
You are an expert knowledge analyst. Analyze the relationship between two entities from different documents.

IMPORTANT INSTRUCTIONS:
- ONLY use the information explicitly provided below
- Do NOT make assumptions beyond the given context
- If the relationship is unclear from the provided information, choose UNRELATED
- Base your analysis STRICTLY on the entity names and their contexts

Entity 1: {entity1_name}
Context 1: {entity1_context}
Document 1: {document1_name}

Entity 2: {entity2_name}
Context 2: {entity2_context}
Document 2: {document2_name}

RELATIONSHIP TYPES (choose exactly ONE):

1. PREREQUISITE - Entity1 is a foundation/requirement for Entity2 OR Entity2 requires Entity1
   Examples: "Basic Math" → "Calculus", "HTTP" → "REST API"

2. EQUIVALENT - Entities are the same concept with different names/terminology
   Examples: "ML" ≡ "Machine Learning", "AI" ≡ "Artificial Intelligence"

3. RELATED - Entities are conceptually connected but distinct concepts
   Examples: "Database" ↔ "SQL", "Programming" ↔ "Software Engineering"

4. CONTAINS - One entity encompasses/includes the other as a sub-component
   Examples: "Computer Science" ⊃ "Programming", "Web Development" ⊃ "HTML"

5. UNRELATED - No meaningful relationship based on provided information
   Examples: "Cooking" ≠ "Mathematics", "Sports" ≠ "Database Design"

CONFIDENCE SCORING GUIDELINES:
- 0.9-1.0: Very clear relationship from context
- 0.7-0.8: Clear relationship with some evidence
- 0.5-0.6: Possible relationship but limited evidence
- 0.3-0.4: Weak relationship, mostly uncertain
- 0.0-0.2: No clear relationship

ANALYSIS PROCESS:
1. Compare entity names for exact/similar terminology
2. Analyze contexts for relationship indicators
3. Check for hierarchical or dependency patterns
4. If uncertain or insufficient information → choose UNRELATED

Provide your analysis in this EXACT JSON format:
{
    "relationship_type": "one of: PREREQUISITE, EQUIVALENT, RELATED, CONTAINS, UNRELATED",
    "confidence": "decimal from 0.0 to 1.0",
    "explanation": "concise explanation based ONLY on provided information",
    "direction": "if applicable: entity1_to_entity2 or entity2_to_entity1 or bidirectional or none"
}

Analysis:
"""

# Neo4j Queries
CROSS_DOC_ENTITIES_QUERY = """
MATCH (e1:Entity)-[:PART_OF]->(d1:Document)
MATCH (e2:Entity)-[:PART_OF]->(d2:Document)
WHERE d1.fileName <> d2.fileName
AND e1.embedding IS NOT NULL 
AND e2.embedding IS NOT NULL
WITH e1, e2, d1, d2,
     gds.similarity.cosine(e1.embedding, e2.embedding) AS similarity
WHERE similarity >= $similarity_threshold
RETURN e1.id as entity1_id, e1.name as entity1_name, 
       e2.id as entity2_id, e2.name as entity2_name,
       d1.fileName as document1, d2.fileName as document2,
       similarity
ORDER BY similarity DESC
LIMIT $limit
"""

CREATE_CROSS_DOC_RELATIONSHIP_QUERY = """
MATCH (e1:Entity {id: $entity1_id})
MATCH (e2:Entity {id: $entity2_id})
MERGE (e1)-[r:CROSS_DOC_RELATIONSHIP]->(e2)
SET r.type = $relationship_type,
    r.confidence = $confidence,
    r.explanation = $explanation,
    r.direction = $direction,
    r.created_at = datetime(),
    r.analysis_version = $analysis_version
RETURN r
"""

GET_EXISTING_RELATIONSHIPS_QUERY = """
MATCH (e1:Entity)-[r:CROSS_DOC_RELATIONSHIP]->(e2:Entity)
MATCH (e1)-[:PART_OF]->(d1:Document)
MATCH (e2)-[:PART_OF]->(d2:Document)
WHERE ($document1 IS NULL OR d1.fileName = $document1)
AND ($document2 IS NULL OR d2.fileName = $document2)
AND ($relationship_type IS NULL OR r.type = $relationship_type)
RETURN e1.name as entity1_name, e2.name as entity2_name,
       d1.fileName as document1, d2.fileName as document2,
       r.type as relationship_type, r.confidence as confidence,
       r.explanation as explanation, r.direction as direction,
       r.created_at as created_at
ORDER BY r.confidence DESC
"""

DELETE_CROSS_DOC_RELATIONSHIPS_QUERY = """
MATCH ()-[r:CROSS_DOC_RELATIONSHIP]->()
WHERE ($document1 IS NULL OR 
       EXISTS {
           MATCH (e1)-[:PART_OF]->(d1:Document)
           WHERE (e1)-[r]-() AND d1.fileName = $document1
       })
AND ($document2 IS NULL OR 
     EXISTS {
         MATCH (e2)-[:PART_OF]->(d2:Document) 
         WHERE ()-[r]-(e2) AND d2.fileName = $document2
     })
DELETE r
RETURN count(r) as deleted_count
"""

# Configuration defaults
DEFAULT_SIMILARITY_THRESHOLD = 0.75
DEFAULT_BATCH_SIZE = 50
DEFAULT_CONFIDENCE_THRESHOLD = 0.6
DEFAULT_ANALYSIS_VERSION = "1.0"

# API response codes
RESPONSE_CODES = {
    "SUCCESS": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "NOT_FOUND": 404,
    "INTERNAL_ERROR": 500
}
