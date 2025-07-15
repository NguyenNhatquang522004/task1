# Cross-Document Entity Relationships Implementation Guide

## 📋 Tổng quan

Tài liệu này mô tả cách triển khai hệ thống tạo mối quan hệ giữa các entities từ các documents khác nhau trong LLM Graph Builder, bao gồm các loại quan hệ: Tiên quyết (Prerequisite), Đồng nhất (Equivalent), Liên quan (Related), Bao quát (Contains), và Không liên quan (Unrelated).

## 🏗️ Kiến trúc hiện tại

### Cấu trúc dữ liệu hiện có:
```
Document A → Chunk A1 → Entity A1
           → Chunk A2 → Entity A2
           
Document B → Chunk B1 → Entity B1  
           → Chunk B2 → Entity B2
```

### Mục tiêu:
```
Entity A1 ←--[PREREQUISITE]--→ Entity B1
Entity A2 ←--[EQUIVALENT]---→ Entity B2
Entity A3 ←--[RELATED]------→ Entity B3
Entity A4 ←--[CONTAINS]-----→ Entity B4
Entity A5 ←--[UNRELATED]----→ Entity B5
```

## 🔧 Thành phần triển khai

### 1. Định nghĩa Constants (constants.py)

Thêm vào file `src/shared/constants.py`:

```python
# Cross-Document Entity Relationship Types
CROSS_DOC_RELATIONSHIP_TYPES = {
    "PREREQUISITE": "Mối quan hệ tiên quyết - Entity A cần thiết trước khi học Entity B",
    "EQUIVALENT": "Mối quan hệ đồng nhất - Entity A và B có ý nghĩa tương tự",
    "RELATED": "Mối quan hệ liên quan - Entity A và B có mối liên hệ thông thường",
    "CONTAINS": "Mối quan hệ bao quát - Entity A bao gồm Entity B",
    "UNRELATED": "Mối quan hệ không liên quan - Entity A và B không có mối liên hệ"
}

# Cross-Document Analysis Prompts
CROSS_DOC_RELATIONSHIP_PROMPT = """
You are an AI expert in analyzing relationships between educational entities across different documents.

Given two entities from different documents, analyze their relationship and classify it into one of these categories:

1. **PREREQUISITE**: Entity A is a prerequisite for Entity B (or vice versa)
   - Example: "Basic Math" → "Calculus"
   
2. **EQUIVALENT**: Entities are essentially the same concept with different names
   - Example: "Machine Learning" ≡ "ML"
   
3. **RELATED**: Entities are related but not prerequisite or equivalent
   - Example: "Database" ↔ "SQL"
   
4. **CONTAINS**: One entity contains or encompasses the other
   - Example: "Computer Science" ⊃ "Programming"
   
5. **UNRELATED**: No meaningful relationship exists
   - Example: "Cooking" ≠ "Mathematics"

Analyze the entities based on:
- Entity names and descriptions
- Context from their source documents
- Semantic similarity
- Educational/topical relationships

Return ONLY the relationship type: PREREQUISITE, EQUIVALENT, RELATED, CONTAINS, or UNRELATED.

Entity A: {entity_a_name} - {entity_a_description}
Entity B: {entity_b_name} - {entity_b_description}

Context A: {context_a}
Context B: {context_b}

Relationship Type:"""

# Cross-Document Entity Query Templates
CROSS_DOC_ENTITIES_QUERY = """
MATCH (d1:Document)-[:FIRST_CHUNK]->(c1:Chunk)-[:HAS_ENTITY]->(e1:__Entity__)
MATCH (d2:Document)-[:FIRST_CHUNK]->(c2:Chunk)-[:HAS_ENTITY]->(e2:__Entity__)
WHERE d1.fileName <> d2.fileName
AND e1.embedding IS NOT NULL 
AND e2.embedding IS NOT NULL
AND vector.similarity.cosine(e1.embedding, e2.embedding) > $similarity_threshold
RETURN 
    e1.id as entity_a_id,
    e1.description as entity_a_desc,
    e2.id as entity_b_id, 
    e2.description as entity_b_desc,
    d1.fileName as doc_a,
    d2.fileName as doc_b,
    c1.text as context_a,
    c2.text as context_b,
    elementId(e1) as entity_a_element_id,
    elementId(e2) as entity_b_element_id,
    vector.similarity.cosine(e1.embedding, e2.embedding) as similarity_score
ORDER BY similarity_score DESC
LIMIT $batch_size
"""

CREATE_CROSS_DOC_RELATIONSHIP_QUERY = """
MATCH (e1:__Entity__), (e2:__Entity__)
WHERE elementId(e1) = $entity_a_id AND elementId(e2) = $entity_b_id
MERGE (e1)-[r:{relationship_type}]->(e2)
SET r.confidence = $confidence,
    r.created_at = datetime(),
    r.analysis_method = 'llm_cross_document'
RETURN r
"""

# Configuration
CROSS_DOC_SIMILARITY_THRESHOLD = 0.7
CROSS_DOC_BATCH_SIZE = 50
CROSS_DOC_MIN_CONFIDENCE = 0.6
```

### 2. Core Implementation (cross_document_relationships.py)

Tạo file `src/cross_document_relationships.py`:

```python
#!/usr/bin/env python3
"""
Cross-Document Entity Relationship Analysis

Tạo mối quan hệ giữa các entities từ các documents khác nhau
"""

import logging
import asyncio
from typing import List, Dict, Tuple, Optional
from langchain.schema import HumanMessage
from langchain_core.output_parsers import StrOutputParser

from src.shared.constants import (
    CROSS_DOC_RELATIONSHIP_PROMPT,
    CROSS_DOC_ENTITIES_QUERY,
    CREATE_CROSS_DOC_RELATIONSHIP_QUERY,
    CROSS_DOC_RELATIONSHIP_TYPES,
    CROSS_DOC_SIMILARITY_THRESHOLD,
    CROSS_DOC_BATCH_SIZE,
    CROSS_DOC_MIN_CONFIDENCE
)
from src.llm import get_llm
from src.shared.common_fn import execute_graph_query

logger = logging.getLogger(__name__)


class CrossDocumentRelationshipAnalyzer:
    """Phân tích và tạo mối quan hệ giữa entities từ các documents khác nhau"""
    
    def __init__(self, graph, model_name: str = "gemini_1.5_pro"):
        self.graph = graph
        self.llm, _ = get_llm(model_name)
        self.parser = StrOutputParser()
        
    async def analyze_cross_document_relationships(self, similarity_threshold: float = None, batch_size: int = None):
        """
        Phân tích và tạo mối quan hệ giữa entities từ các documents khác nhau
        
        Args:
            similarity_threshold: Ngưỡng similarity để lọc entity pairs
            batch_size: Số lượng entity pairs xử lý mỗi batch
        """
        if similarity_threshold is None:
            similarity_threshold = CROSS_DOC_SIMILARITY_THRESHOLD
        if batch_size is None:
            batch_size = CROSS_DOC_BATCH_SIZE
            
        logger.info("Starting cross-document relationship analysis...")
        
        # Lấy entity pairs có similarity cao
        entity_pairs = self._get_similar_entity_pairs(similarity_threshold, batch_size)
        logger.info(f"Found {len(entity_pairs)} similar entity pairs")
        
        if not entity_pairs:
            logger.info("No similar entity pairs found")
            return {"processed": 0, "relationships_created": 0}
        
        # Phân tích từng batch
        total_processed = 0
        total_relationships = 0
        
        for i in range(0, len(entity_pairs), 10):  # Process in smaller batches
            batch = entity_pairs[i:i+10]
            batch_results = await self._process_entity_batch(batch)
            
            total_processed += len(batch)
            total_relationships += batch_results["relationships_created"]
            
            logger.info(f"Processed batch {i//10 + 1}: {batch_results}")
            
        logger.info(f"Analysis complete. Processed: {total_processed}, Relationships created: {total_relationships}")
        return {"processed": total_processed, "relationships_created": total_relationships}
    
    def _get_similar_entity_pairs(self, similarity_threshold: float, batch_size: int) -> List[Dict]:
        """Lấy các cặp entities có similarity cao từ các documents khác nhau"""
        
        params = {
            "similarity_threshold": similarity_threshold,
            "batch_size": batch_size
        }
        
        try:
            results = execute_graph_query(self.graph, CROSS_DOC_ENTITIES_QUERY, params)
            return results
        except Exception as e:
            logger.error(f"Error getting similar entity pairs: {e}")
            return []
    
    async def _process_entity_batch(self, entity_pairs: List[Dict]) -> Dict:
        """Xử lý một batch các entity pairs"""
        
        relationships_created = 0
        
        for pair in entity_pairs:
            try:
                # Phân tích relationship type bằng LLM
                relationship_type, confidence = await self._analyze_relationship_type(pair)
                
                if relationship_type != "UNRELATED" and confidence >= CROSS_DOC_MIN_CONFIDENCE:
                    # Tạo relationship trong Neo4j
                    success = self._create_relationship(pair, relationship_type, confidence)
                    if success:
                        relationships_created += 1
                        logger.info(f"Created {relationship_type} relationship: {pair['entity_a_id']} → {pair['entity_b_id']}")
                        
            except Exception as e:
                logger.error(f"Error processing entity pair {pair['entity_a_id']} - {pair['entity_b_id']}: {e}")
                continue
        
        return {"relationships_created": relationships_created}
    
    async def _analyze_relationship_type(self, entity_pair: Dict) -> Tuple[str, float]:
        """
        Sử dụng LLM để phân tích loại mối quan hệ giữa hai entities
        
        Returns:
            Tuple[relationship_type, confidence_score]
        """
        try:
            # Chuẩn bị prompt
            prompt = CROSS_DOC_RELATIONSHIP_PROMPT.format(
                entity_a_name=entity_pair["entity_a_id"],
                entity_a_description=entity_pair.get("entity_a_desc", ""),
                entity_b_name=entity_pair["entity_b_id"], 
                entity_b_description=entity_pair.get("entity_b_desc", ""),
                context_a=entity_pair.get("context_a", "")[:500],  # Limit context length
                context_b=entity_pair.get("context_b", "")[:500]
            )
            
            # Gọi LLM
            chain = self.llm | self.parser
            response = await chain.ainvoke([HumanMessage(content=prompt)])
            
            # Parse response
            relationship_type = response.strip().upper()
            
            # Validate relationship type
            if relationship_type not in CROSS_DOC_RELATIONSHIP_TYPES:
                logger.warning(f"Invalid relationship type returned: {relationship_type}")
                return "UNRELATED", 0.0
            
            # Calculate confidence based on similarity score and response clarity
            similarity_score = entity_pair.get("similarity_score", 0.0)
            confidence = min(0.9, similarity_score + 0.1)  # Simple confidence calculation
            
            return relationship_type, confidence
            
        except Exception as e:
            logger.error(f"Error analyzing relationship type: {e}")
            return "UNRELATED", 0.0
    
    def _create_relationship(self, entity_pair: Dict, relationship_type: str, confidence: float) -> bool:
        """Tạo relationship trong Neo4j database"""
        
        try:
            query = CREATE_CROSS_DOC_RELATIONSHIP_QUERY.format(relationship_type=relationship_type)
            
            params = {
                "entity_a_id": entity_pair["entity_a_element_id"],
                "entity_b_id": entity_pair["entity_b_element_id"],
                "confidence": confidence
            }
            
            result = execute_graph_query(self.graph, query, params)
            return len(result) > 0
            
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False


# Utility functions
async def analyze_cross_document_relationships(graph, model_name: str = "gemini_1.5_pro", **kwargs):
    """
    Main function để phân tích cross-document relationships
    
    Usage:
        await analyze_cross_document_relationships(graph, model_name="gemini_1.5_pro")
    """
    analyzer = CrossDocumentRelationshipAnalyzer(graph, model_name)
    return await analyzer.analyze_cross_document_relationships(**kwargs)


def get_cross_document_statistics(graph) -> Dict:
    """Lấy thống kê về cross-document relationships"""
    
    query = """
    MATCH (e1:__Entity__)-[r]->(e2:__Entity__)
    WHERE r.analysis_method = 'llm_cross_document'
    WITH type(r) as relationship_type, count(r) as count
    RETURN relationship_type, count
    ORDER BY count DESC
    """
    
    try:
        results = execute_graph_query(graph, query)
        return {result["relationship_type"]: result["count"] for result in results}
    except Exception as e:
        logger.error(f"Error getting cross-document statistics: {e}")
        return {}


def delete_cross_document_relationships(graph, relationship_types: List[str] = None):
    """Xóa cross-document relationships"""
    
    if relationship_types:
        type_filter = "AND type(r) IN $relationship_types"
        params = {"relationship_types": relationship_types}
    else:
        type_filter = ""
        params = {}
    
    query = f"""
    MATCH (e1:__Entity__)-[r]->(e2:__Entity__)
    WHERE r.analysis_method = 'llm_cross_document' {type_filter}
    DELETE r
    RETURN count(r) as deleted_count
    """
    
    try:
        results = execute_graph_query(graph, query, params)
        return results[0]["deleted_count"] if results else 0
    except Exception as e:
        logger.error(f"Error deleting cross-document relationships: {e}")
        return 0
```

### 3. API Endpoints (score.py)

Thêm vào file `score.py`:

```python
from src.cross_document_relationships import (
    analyze_cross_document_relationships,
    get_cross_document_statistics,
    delete_cross_document_relationships
)

@app.post("/analyze_cross_document_relationships")
async def analyze_cross_document_relationships_endpoint(
    uri=Form(None),
    userName=Form(None), 
    password=Form(None),
    database=Form(None),
    model=Form("gemini_1.5_pro"),
    similarity_threshold=Form(0.7),
    batch_size=Form(50),
    email=Form(None)
):
    """
    Phân tích và tạo mối quan hệ giữa entities từ các documents khác nhau
    """
    try:
        start = time.time()
        graph = create_graph_database_connection(uri, userName, password, database)
        
        result = await analyze_cross_document_relationships(
            graph=graph,
            model_name=model,
            similarity_threshold=float(similarity_threshold),
            batch_size=int(batch_size)
        )
        
        end = time.time()
        elapsed_time = end - start
        
        json_obj = {
            'api_name': 'analyze_cross_document_relationships',
            'db_url': uri,
            'userName': userName,
            'database': database,
            'model': model,
            'similarity_threshold': similarity_threshold,
            'batch_size': batch_size,
            'logging_time': formatted_time(datetime.now(timezone.utc)),
            'elapsed_api_time': f'{elapsed_time:.2f}',
            'email': email
        }
        logger.log_struct(json_obj, "INFO")
        
        return create_api_response('Success', data=result, message=f"Analysis completed in {elapsed_time:.2f}s")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f'Error in cross-document relationship analysis: {error_message}')
        return create_api_response('Failed', message="Unable to analyze cross-document relationships", error=error_message)

@app.post("/cross_document_relationships_stats")
async def get_cross_document_relationships_stats(
    uri=Form(None),
    userName=Form(None),
    password=Form(None), 
    database=Form(None),
    email=Form(None)
):
    """
    Lấy thống kê về cross-document relationships
    """
    try:
        start = time.time()
        graph = create_graph_database_connection(uri, userName, password, database)
        
        stats = get_cross_document_statistics(graph)
        
        end = time.time()
        elapsed_time = end - start
        
        json_obj = {
            'api_name': 'cross_document_relationships_stats',
            'db_url': uri,
            'userName': userName, 
            'database': database,
            'logging_time': formatted_time(datetime.now(timezone.utc)),
            'elapsed_api_time': f'{elapsed_time:.2f}',
            'email': email
        }
        logger.log_struct(json_obj, "INFO")
        
        return create_api_response('Success', data=stats, message=f"Statistics retrieved in {elapsed_time:.2f}s")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f'Error getting cross-document relationship statistics: {error_message}')
        return create_api_response('Failed', message="Unable to get statistics", error=error_message)

@app.post("/delete_cross_document_relationships")
async def delete_cross_document_relationships_endpoint(
    uri=Form(None),
    userName=Form(None),
    password=Form(None),
    database=Form(None), 
    relationship_types=Form(None),
    email=Form(None)
):
    """
    Xóa cross-document relationships
    """
    try:
        start = time.time()
        graph = create_graph_database_connection(uri, userName, password, database)
        
        types_list = None
        if relationship_types:
            types_list = [t.strip() for t in relationship_types.split(',')]
        
        deleted_count = delete_cross_document_relationships(graph, types_list)
        
        end = time.time()
        elapsed_time = end - start
        
        json_obj = {
            'api_name': 'delete_cross_document_relationships',
            'db_url': uri,
            'userName': userName,
            'database': database,
            'relationship_types': relationship_types,
            'deleted_count': deleted_count,
            'logging_time': formatted_time(datetime.now(timezone.utc)),
            'elapsed_api_time': f'{elapsed_time:.2f}',
            'email': email
        }
        logger.log_struct(json_obj, "INFO")
        
        return create_api_response('Success', data={'deleted_count': deleted_count}, message=f"Deleted {deleted_count} relationships in {elapsed_time:.2f}s")
        
    except Exception as e:
        error_message = str(e)
        logger.error(f'Error deleting cross-document relationships: {error_message}')
        return create_api_response('Failed', message="Unable to delete relationships", error=error_message)
```

### 4. Post Processing Integration

Thêm vào `post_processing.py`:

```python
from src.cross_document_relationships import analyze_cross_document_relationships

# Thêm vào hàm post_processing trong score.py
if "analyze_cross_document_relationships" in tasks:
    await asyncio.to_thread(
        analyze_cross_document_relationships,
        graph,
        model_name=os.getenv('CROSS_DOC_MODEL', 'gemini_1.5_pro')
    )
    api_name = 'post_processing/analyze_cross_document_relationships'
    logging.info('Cross-document relationships analyzed')
```

## 📊 Workflow chi tiết

### Bước 1: Chuẩn bị dữ liệu
1. Đảm bảo tất cả entities đã có embeddings
2. Kiểm tra cấu trúc Document → Chunk → Entity

### Bước 2: Tìm entity pairs tương tự
```cypher
MATCH (d1:Document)-[:FIRST_CHUNK]->(c1:Chunk)-[:HAS_ENTITY]->(e1:__Entity__)
MATCH (d2:Document)-[:FIRST_CHUNK]->(c2:Chunk)-[:HAS_ENTITY]->(e2:__Entity__)
WHERE d1.fileName <> d2.fileName
AND vector.similarity.cosine(e1.embedding, e2.embedding) > 0.7
```

### Bước 3: Phân tích bằng LLM
- Gửi entity pairs cùng context cho LLM
- LLM phân tích và trả về relationship type
- Tính confidence score

### Bước 4: Tạo relationships
```cypher
MERGE (e1)-[r:PREREQUISITE]->(e2)
SET r.confidence = 0.85,
    r.analysis_method = 'llm_cross_document'
```

## 🎯 Các loại mối quan hệ

### 1. PREREQUISITE (Tiên quyết)
```
Entity A --[PREREQUISITE]--> Entity B
```
- A là kiến thức cần thiết trước B
- Ví dụ: "Toán cơ bản" → "Giải tích"

### 2. EQUIVALENT (Đồng nhất)  
```
Entity A <--[EQUIVALENT]--> Entity B
```
- A và B là cùng một khái niệm
- Ví dụ: "Machine Learning" ≡ "Học máy"

### 3. RELATED (Liên quan)
```
Entity A <--[RELATED]--> Entity B  
```
- A và B có mối liên hệ chung
- Ví dụ: "Database" ↔ "SQL"

### 4. CONTAINS (Bao quát)
```
Entity A --[CONTAINS]--> Entity B
```
- A bao gồm hoặc chứa B
- Ví dụ: "Khoa học máy tính" ⊃ "Lập trình"

### 5. UNRELATED (Không liên quan)
```
Entity A     Entity B
```
- Không có mối quan hệ có ý nghĩa
- Ví dụ: "Nấu ăn" ≠ "Toán học"

## 🚀 Cách sử dụng

### 1. API Call
```bash
curl -X POST "http://localhost:8000/analyze_cross_document_relationships" \
  -F "uri=bolt://localhost:7687" \
  -F "userName=neo4j" \
  -F "password=password" \
  -F "database=neo4j" \
  -F "model=gemini_1.5_pro" \
  -F "similarity_threshold=0.7" \
  -F "batch_size=50"
```

### 2. Post Processing
```bash
curl -X POST "http://localhost:8000/post_processing" \
  -F "uri=bolt://localhost:7687" \
  -F "userName=neo4j" \
  -F "password=password" \
  -F "database=neo4j" \
  -F "tasks=[\"analyze_cross_document_relationships\"]"
```

### 3. Python Code
```python
from src.cross_document_relationships import analyze_cross_document_relationships

# Phân tích relationships
result = await analyze_cross_document_relationships(
    graph=graph,
    model_name="gemini_1.5_pro",
    similarity_threshold=0.7,
    batch_size=50
)

print(f"Processed: {result['processed']}")
print(f"Relationships created: {result['relationships_created']}")
```

## 📈 Monitoring và Optimization

### 1. Performance Metrics
- Similarity threshold: 0.7 (có thể điều chỉnh)
- Batch size: 50 entities/batch
- LLM model: gemini_1.5_pro (tối ưu cho analysis)

### 2. Quality Control
- Confidence threshold: 0.6
- Manual review cho high-impact relationships
- A/B testing với different prompts

### 3. Scaling Considerations
- Background processing cho large datasets
- Incremental analysis cho new documents
- Caching để tránh re-analysis

## 🔍 Queries hữu ích

### Xem tất cả cross-document relationships:
```cypher
MATCH (e1:__Entity__)-[r]->(e2:__Entity__)
WHERE r.analysis_method = 'llm_cross_document'
RETURN e1.id, type(r), e2.id, r.confidence
ORDER BY r.confidence DESC
```

### Tìm prerequisites chains:
```cypher
MATCH path = (start:__Entity__)-[:PREREQUISITE*]->(end:__Entity__)
WHERE length(path) > 1
RETURN start.id, [n in nodes(path) | n.id] as prerequisite_chain
```

### Phân tích entity clusters:
```cypher
MATCH (e:__Entity__)-[:EQUIVALENT|RELATED]-(related:__Entity__)
WITH e, collect(related.id) as related_entities
WHERE size(related_entities) > 2
RETURN e.id, related_entities
```

## ⚠️ Lưu ý quan trọng

1. **Performance**: Chạy trong background cho datasets lớn
2. **Cost**: LLM calls có thể tốn kém, cân nhắc batch size
3. **Quality**: Review manual cho critical relationships
4. **Incremental**: Chỉ chạy cho documents mới để tránh duplicate
5. **Backup**: Backup database trước khi chạy large-scale analysis

## 🔧 Troubleshooting

### Lỗi thường gặp:
1. **Out of memory**: Giảm batch_size
2. **LLM timeout**: Tăng timeout hoặc đổi model
3. **Embedding missing**: Chạy entity embedding trước
4. **Relationship duplicates**: Check existing relationships

### Debug commands:
```python
# Check entity embeddings
stats = get_cross_document_statistics(graph)
print(f"Current relationships: {stats}")

# Test với sample data
result = await analyze_cross_document_relationships(
    graph, batch_size=5, similarity_threshold=0.8
)
```

---

## Kết luận

Hệ thống Cross-Document Entity Relationships này sẽ tạo ra một knowledge graph phong phú với các mối quan hệ có ý nghĩa giữa các entities từ nhiều documents khác nhau, hỗ trợ tốt cho việc học tập và khám phá kiến thức.
