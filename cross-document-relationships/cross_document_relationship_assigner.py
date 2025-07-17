"""
Cross-Document Entity Relationship Assignment
===========================================

Mục đích: Tự động tìm và gán mối quan hệ giữa các entity từ các document khác nhau

Problem Statement:
- Document A có entity "Python Programming"
- Document B có entity "Machine Learning" 
- System cần tự động phát hiện và gán relationship: Python Programming -> RELATED -> Machine Learning

Workflow:
1. Phân tích entities từ tất cả documents
2. Tìm các entity pairs có similarity cao từ các documents khác nhau
3. Sử dụng LLM để phân tích semantic relationship
4. Gán relationship phù hợp vào Neo4j graph
5. Tạo cross-document connections

Example Output:
(Document_A:Entity)-[:RELATED]->(Document_B:Entity)
(Document_A:Entity)-[:PREREQUISITE]->(Document_B:Entity)
(Document_A:Entity)-[:EQUIVALENT]->(Document_B:Entity)
"""

import asyncio
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class CrossDocumentRelationshipAssigner:
    """
    Core class để gán mối quan hệ giữa entities từ các documents khác nhau
    """
    
    def __init__(self, neo4j_driver, llm_client, similarity_threshold=0.75):
        self.neo4j_driver = neo4j_driver
        self.llm_client = llm_client
        self.similarity_threshold = similarity_threshold
        
        # Các loại mối quan hệ có thể gán
        self.relationship_types = [
            "RELATED",           # Liên quan chung
            "PREREQUISITE",      # Điều kiện tiên quyết
            "EQUIVALENT",        # Tương đương
            "CONTAINS",          # Chứa đựng
            "SIMILAR_TO",        # Tương tự
            "DEPENDS_ON",        # Phụ thuộc vào
            "ENABLES",           # Cho phép/kích hoạt
            "EXTENDS"            # Mở rộng
        ]
        
    async def find_cross_document_entity_pairs(self) -> List[Dict]:
        """
        Tìm các cặp entity từ documents khác nhau có thể có mối quan hệ
        """
        query = """
        // Tìm entities từ các documents khác nhau có thể có mối quan hệ
        MATCH (e1:Entity)-[:PART_OF]->(d1:Document)
        MATCH (e2:Entity)-[:PART_OF]->(d2:Document) 
        WHERE d1.fileName <> d2.fileName
        AND e1.name IS NOT NULL
        AND e2.name IS NOT NULL
        AND e1.type IS NOT NULL
        AND e2.type IS NOT NULL
        
        // Tạm thời không dùng embedding similarity, chỉ lọc theo type similarity
        WITH e1, e2, d1, d2,
             CASE 
                WHEN e1.type = e2.type THEN 0.9
                WHEN e1.type IN ['PERSON'] AND e2.type IN ['PERSON', 'ORGANIZATION'] THEN 0.7
                WHEN e1.type IN ['ORGANIZATION'] AND e2.type IN ['ORGANIZATION', 'PERSON'] THEN 0.7
                WHEN e1.type IN ['LOCATION'] AND e2.type IN ['LOCATION'] THEN 0.8
                WHEN e1.type IN ['CONCEPT'] AND e2.type IN ['CONCEPT', 'TOPIC'] THEN 0.6
                ELSE 0.3
             END AS similarity
        WHERE similarity >= $threshold
        
        RETURN e1.id as entity1_id,
               e1.name as entity1_name,
               e1.type as entity1_type,
               e1.description as entity1_context,
               d1.fileName as document1,
               
               e2.id as entity2_id, 
               e2.name as entity2_name,
               e2.type as entity2_type,
               e2.description as entity2_context,
               d2.fileName as document2,
               
               similarity
        ORDER BY similarity DESC
        LIMIT 1000
        """
        
        with self.neo4j_driver.session() as session:
            result = session.run(query, threshold=self.similarity_threshold)
            
            entity_pairs = []
            for record in result:
                entity_pairs.append({
                    "entity1": {
                        "id": record["entity1_id"],
                        "name": record["entity1_name"], 
                        "type": record["entity1_type"],
                        "context": record["entity1_context"],
                        "document": record["document1"]
                    },
                    "entity2": {
                        "id": record["entity2_id"],
                        "name": record["entity2_name"],
                        "type": record["entity2_type"], 
                        "context": record["entity2_context"],
                        "document": record["document2"]
                    },
                    "similarity": record["similarity"]
                })
                
        logger.info(f"Found {len(entity_pairs)} potential cross-document entity pairs")
        return entity_pairs
    
    async def analyze_relationship(self, entity1: Dict, entity2: Dict) -> Dict:
        """
        Sử dụng LLM để phân tích mối quan hệ giữa 2 entities
        """
        prompt = f"""
        Phân tích mối quan hệ giữa hai entities từ các documents khác nhau:

        ENTITY 1:
        - Tên: {entity1['name']}
        - Loại: {entity1['type']}
        - Bối cảnh: {entity1['context']}
        - Document: {entity1['document']}

        ENTITY 2:
        - Tên: {entity2['name']}
        - Loại: {entity2['type']}
        - Bối cảnh: {entity2['context']}
        - Document: {entity2['document']}

        Xác định mối quan hệ phù hợp nhất từ các loại sau:
        - RELATED: Liên quan chung
        - PREREQUISITE: Entity1 là điều kiện tiên quyết cho Entity2
        - EQUIVALENT: Hai entities tương đương nhau
        - CONTAINS: Entity1 chứa đựng Entity2
        - SIMILAR_TO: Hai entities tương tự nhau
        - DEPENDS_ON: Entity1 phụ thuộc vào Entity2
        - ENABLES: Entity1 cho phép/kích hoạt Entity2
        - EXTENDS: Entity1 mở rộng Entity2
        - UNRELATED: Không có mối quan hệ có ý nghĩa

        Trả về JSON format:
        {{
            "relationship_type": "...",
            "confidence": 0.8,
            "direction": "entity1_to_entity2" hoặc "entity2_to_entity1" hoặc "bidirectional",
            "explanation": "Giải thích ngắn gọn"
        }}
        """
        
        try:
            response = await self.llm_client.generate_text(prompt, temperature=0.1)
            # Parse JSON response
            import json
            analysis = json.loads(response)
            
            return {
                "relationship_type": analysis.get("relationship_type", "UNRELATED"),
                "confidence": float(analysis.get("confidence", 0.0)),
                "direction": analysis.get("direction", "entity1_to_entity2"),
                "explanation": analysis.get("explanation", "")
            }
            
        except Exception as e:
            logger.error(f"Error analyzing relationship: {e}")
            return {
                "relationship_type": "UNRELATED",
                "confidence": 0.0,
                "direction": "entity1_to_entity2", 
                "explanation": f"Analysis failed: {str(e)}"
            }
    
    async def create_relationship_in_graph(self, entity1: Dict, entity2: Dict, relationship: Dict) -> bool:
        """
        Tạo mối quan hệ trong Neo4j graph
        """
        if relationship["relationship_type"] == "UNRELATED" or relationship["confidence"] < 0.5:
            return False
            
        try:
            # Xác định hướng của relationship
            if relationship["direction"] == "entity2_to_entity1":
                source_id, target_id = entity2["id"], entity1["id"]
                source_name, target_name = entity2["name"], entity1["name"]
            else:
                source_id, target_id = entity1["id"], entity2["id"]
                source_name, target_name = entity1["name"], entity2["name"]
            
            # Tạo relationship trong Neo4j
            query = f"""
            MATCH (e1:Entity {{id: $source_id}})
            MATCH (e2:Entity {{id: $target_id}})
            
            // Kiểm tra relationship đã tồn tại chưa
            WHERE NOT exists((e1)-[:{relationship["relationship_type"]}]->(e2))
            
            CREATE (e1)-[r:{relationship["relationship_type"]}]->(e2)
            SET r.confidence = $confidence,
                r.explanation = $explanation,
                r.created_by = "cross_document_analyzer",
                r.created_at = datetime(),
                r.analysis_version = "1.0"
                
            RETURN r
            """
            
            with self.neo4j_driver.session() as session:
                result = session.run(query, 
                    source_id=source_id,
                    target_id=target_id, 
                    confidence=relationship["confidence"],
                    explanation=relationship["explanation"]
                )
                
                created = len(list(result)) > 0
                
                if created:
                    logger.info(f"Created relationship: {source_name} -[{relationship['relationship_type']}]-> {target_name}")
                    
                    # Nếu là bidirectional, tạo relationship ngược lại
                    if relationship["direction"] == "bidirectional":
                        reverse_query = f"""
                        MATCH (e1:Entity {{id: $target_id}})
                        MATCH (e2:Entity {{id: $source_id}})
                        WHERE NOT exists((e1)-[:{relationship["relationship_type"]}]->(e2))
                        CREATE (e1)-[r:{relationship["relationship_type"]}]->(e2)
                        SET r.confidence = $confidence,
                            r.explanation = $explanation,
                            r.created_by = "cross_document_analyzer",
                            r.created_at = datetime(),
                            r.analysis_version = "1.0"
                        RETURN r
                        """
                        session.run(reverse_query,
                            source_id=source_id,
                            target_id=target_id,
                            confidence=relationship["confidence"],
                            explanation=relationship["explanation"]
                        )
                        logger.info(f"Created bidirectional relationship: {target_name} -[{relationship['relationship_type']}]-> {source_name}")
                
                return created
                
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")
            return False
    
    async def process_cross_document_relationships(self, max_pairs: int = 1000, batch_size: int = 10) -> Dict:
        """
        Main method: Xử lý tất cả cross-document relationships
        """
        start_time = datetime.now()
        
        logger.info("Starting cross-document relationship analysis...")
        
        # 1. Tìm entity pairs từ các documents khác nhau
        entity_pairs = await self.find_cross_document_entity_pairs()
        
        if not entity_pairs:
            return {
                "processed_pairs": 0,
                "created_relationships": 0,
                "processing_time": "0s",
                "message": "No cross-document entity pairs found"
            }
        
        # Limit số lượng pairs để xử lý
        entity_pairs = entity_pairs[:max_pairs]
        
        # 2. Phân tích và tạo relationships theo batch
        created_count = 0
        processed_count = 0
        
        for i in range(0, len(entity_pairs), batch_size):
            batch = entity_pairs[i:i + batch_size]
            
            # Xử lý batch
            batch_results = await asyncio.gather(*[
                self._process_entity_pair(pair) 
                for pair in batch
            ], return_exceptions=True)
            
            # Đếm kết quả
            for result in batch_results:
                if isinstance(result, bool) and result:
                    created_count += 1
                processed_count += 1
            
            logger.info(f"Processed batch {i//batch_size + 1}, created {sum(1 for r in batch_results if r is True)} relationships")
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        result = {
            "processed_pairs": processed_count,
            "created_relationships": created_count,
            "processing_time": f"{processing_time:.2f}s",
            "success_rate": f"{(created_count/processed_count*100):.1f}%" if processed_count > 0 else "0%",
            "message": f"Successfully created {created_count} cross-document relationships"
        }
        
        logger.info(f"Cross-document relationship analysis completed: {result}")
        return result
    
    async def _process_entity_pair(self, pair: Dict) -> bool:
        """
        Xử lý một cặp entity: phân tích và tạo relationship
        """
        try:
            # Phân tích mối quan hệ
            relationship = await self.analyze_relationship(pair["entity1"], pair["entity2"])
            
            # Tạo relationship trong graph nếu có confidence đủ cao
            if relationship["confidence"] >= 0.5:
                return await self.create_relationship_in_graph(
                    pair["entity1"], 
                    pair["entity2"], 
                    relationship
                )
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing entity pair: {e}")
            return False

    async def get_cross_document_statistics(self) -> Dict:
        """
        Lấy thống kê về cross-document relationships
        """
        query = """
        // Đếm relationships giữa entities từ các documents khác nhau
        MATCH (e1:Entity)-[:PART_OF]->(d1:Document)
        MATCH (e2:Entity)-[:PART_OF]->(d2:Document)
        MATCH (e1)-[r]->(e2)
        WHERE d1.fileName <> d2.fileName
        AND r.created_by = "cross_document_analyzer"
        
        RETURN 
            count(r) as total_cross_doc_relationships,
            count(DISTINCT d1.fileName) as source_documents,
            count(DISTINCT d2.fileName) as target_documents,
            count(DISTINCT type(r)) as relationship_types,
            collect(DISTINCT type(r)) as relationship_type_list,
            avg(r.confidence) as avg_confidence
        """
        
        with self.neo4j_driver.session() as session:
            result = session.run(query)
            record = result.single()
            
            if record:
                return {
                    "total_cross_doc_relationships": record["total_cross_doc_relationships"],
                    "source_documents": record["source_documents"],
                    "target_documents": record["target_documents"],
                    "relationship_types": record["relationship_types"], 
                    "relationship_type_list": record["relationship_type_list"],
                    "avg_confidence": round(record["avg_confidence"] or 0, 2)
                }
            else:
                return {
                    "total_cross_doc_relationships": 0,
                    "source_documents": 0,
                    "target_documents": 0,
                    "relationship_types": 0,
                    "relationship_type_list": [],
                    "avg_confidence": 0
                }

# Example usage
async def main():
    """
    Example: Sử dụng CrossDocumentRelationshipAssigner
    """
    # Khởi tạo
    assigner = CrossDocumentRelationshipAssigner(
        neo4j_driver=your_neo4j_driver,
        llm_client=your_llm_client,
        similarity_threshold=0.75
    )
    
    # Chạy phân tích cross-document relationships
    results = await assigner.process_cross_document_relationships(
        max_pairs=500,
        batch_size=10
    )
    
    print("Cross-Document Relationship Assignment Results:")
    print(f"- Processed: {results['processed_pairs']} entity pairs")
    print(f"- Created: {results['created_relationships']} relationships")
    print(f"- Time: {results['processing_time']}")
    print(f"- Success rate: {results['success_rate']}")
    
    # Lấy thống kê
    stats = await assigner.get_cross_document_statistics()
    print(f"\\nCross-Document Statistics:")
    print(f"- Total relationships: {stats['total_cross_doc_relationships']}")
    print(f"- Documents involved: {stats['source_documents']} -> {stats['target_documents']}")
    print(f"- Relationship types: {stats['relationship_type_list']}")
    print(f"- Average confidence: {stats['avg_confidence']}")

if __name__ == "__main__":
    asyncio.run(main())
