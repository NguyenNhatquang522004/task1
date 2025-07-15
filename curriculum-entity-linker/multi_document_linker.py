"""
Enhanced Curriculum Entity Linker for handling multiple files with same course code

This module extends the curriculum-entity-linker to properly handle cases where
multiple PDF files belong to the same course code (e.g., CMP3025).

Key improvements:
1. Groups files by course code
2. Creates consolidated linking structure
3. Supports multiple document types per course
4. Maintains proper relationships between all files of same course
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class MultiDocumentCurriculumLinker:
    """Enhanced linker for handling multiple documents per course code"""
    
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def extract_course_code(self, filename: str) -> Optional[str]:
        """
        Extract course code from filename
        
        Examples:
        - '[CMP3025] GIÁO TRÌNH THỰC HÀNH LẬP TRÌNH JAVA 2024 - 2005' → 'CMP3025'
        - '[CMP3025] Bài tập thực hành Java' → 'CMP3025'
        - '[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows' → 'CMP170'
        
        Args:
            filename: Document filename
            
        Returns:
            Course code hoặc None nếu không tìm thấy
        """
        # Pattern để tìm course code trong dấu ngoặc vuông
        pattern = r'\[([A-Z]{3}\d{3,4})\]'
        match = re.search(pattern, filename)
        
        if match:
            course_code = match.group(1)
            logger.debug(f"Extracted course code '{course_code}' from '{filename}'")
            return course_code
        
        logger.debug(f"No course code found in '{filename}'")
        return None
    
    def get_documents_grouped_by_course(self) -> Dict[str, List[Dict]]:
        """
        Lấy tất cả documents và group theo course code
        
        Returns:
            Dictionary: {course_code: [list of document info]}
        """
        query = """
        MATCH (d:Document)
        WHERE d.fileName IS NOT NULL
        RETURN d.fileName as filename, d.schema as schema, ID(d) as doc_id
        ORDER BY d.fileName
        """
        
        documents_by_course = defaultdict(list)
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            
            for record in result:
                filename = record['filename']
                schema = record['schema']
                doc_id = record['doc_id']
                
                course_code = self.extract_course_code(filename)
                
                if course_code:
                    doc_info = {
                        'course_code': course_code,
                        'filename': filename,
                        'schema': schema,
                        'doc_id': doc_id
                    }
                    documents_by_course[course_code].append(doc_info)
                    logger.debug(f"Added document to {course_code}: {filename}")
                else:
                    logger.debug(f"Skipping document without course code: {filename}")
        
        # Log grouping results
        for course_code, docs in documents_by_course.items():
            logger.info(f"Course {course_code}: {len(docs)} documents")
            for doc in docs:
                logger.info(f"  - {doc['filename']}")
        
        return dict(documents_by_course)
    
    def find_course_framework(self, course_code: str) -> Optional[Dict]:
        """
        Tìm Course framework node tương ứng với course code
        
        Args:
            course_code: Course code (ví dụ: CMP3025)
            
        Returns:
            Course framework info hoặc None
        """
        query = """
        MATCH (c:Course {code: $course_code})
        WHERE NOT c:__Entity__  // Không phải entity được extract
        RETURN c.code as code, c.name as name, ID(c) as course_id, c as course
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, course_code=course_code)
            record = result.single()
            
            if record:
                course_info = {
                    'course_id': record['course_id'],
                    'code': record['code'],
                    'name': record['name'],
                    'course': record['course']
                }
                logger.debug(f"Found course framework: {course_code} - {course_info['name']}")
                return course_info
            else:
                logger.warning(f"No course framework found for {course_code}")
                return None
    
    def create_course_consolidation_node(self, course_code: str, documents: List[Dict]) -> Optional[int]:
        """
        Tạo một node tổng hợp cho tất cả documents của một course code
        
        Args:
            course_code: Course code (ví dụ: CMP3025)
            documents: List of document info for this course
            
        Returns:
            Node ID của consolidation node hoặc None nếu thất bại
        """
        # Tạo tên node duy nhất cho course
        node_name = f"{course_code}_CourseConsolidation"
        
        # Tạo description từ tất cả document names
        doc_names = [doc['filename'] for doc in documents]
        description = f"Consolidation node for course {course_code} containing {len(documents)} documents: " + ", ".join(doc_names[:3])
        if len(documents) > 3:
            description += f" and {len(documents) - 3} more documents"
        
        query = """
        MERGE (a:CourseConsolidation {name: $node_name, course_code: $course_code})
        SET a.description = $description,
            a.document_count = $document_count,
            a.created_at = datetime(),
            a.last_updated = datetime()
        RETURN ID(a) as node_id
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query, 
                node_name=node_name,
                course_code=course_code,
                description=description,
                document_count=len(documents)
            )
            record = result.single()
            
            if record:
                node_id = record['node_id']
                logger.info(f"Created/updated course consolidation node: {node_name} (ID: {node_id})")
                return node_id
        
        return None
    
    def create_document_specific_nodes(self, course_code: str, documents: List[Dict]) -> List[int]:
        """
        Tạo các node riêng biệt cho từng document trong course
        
        Args:
            course_code: Course code
            documents: List of document info
            
        Returns:
            List of document-specific node IDs
        """
        document_node_ids = []
        
        for doc in documents:
            # Tạo tên node riêng cho từng document
            doc_name_clean = re.sub(r'[^\w\s-]', '', doc['filename'])[:50]  # Clean và giới hạn độ dài
            node_name = f"{course_code}_{doc_name_clean}_{doc['doc_id']}"
            
            query = """
            MERGE (d:DocumentLink {
                name: $node_name, 
                course_code: $course_code,
                original_filename: $filename,
                document_id: $doc_id
            })
            SET d.schema = $schema,
                d.created_at = datetime(),
                d.last_updated = datetime()
            RETURN ID(d) as node_id
            """
            
            with self.driver.session(database=self.database) as session:
                result = session.run(
                    query,
                    node_name=node_name,
                    course_code=course_code,
                    filename=doc['filename'],
                    doc_id=doc['doc_id'],
                    schema=doc['schema']
                )
                record = result.single()
                
                if record:
                    node_id = record['node_id']
                    document_node_ids.append(node_id)
                    logger.info(f"Created document-specific node: {node_name} (ID: {node_id})")
        
        return document_node_ids
    
    def create_course_relationships(self, course_id: int, consolidation_node_id: int, 
                                  document_node_ids: List[int], documents: List[Dict]):
        """
        Tạo tất cả relationships cho một course
        
        Args:
            course_id: Course framework node ID
            consolidation_node_id: Course consolidation node ID
            document_node_ids: List of document-specific node IDs
            documents: List of document info
        """
        with self.driver.session(database=self.database) as session:
            # 1. Course framework -> Course consolidation
            session.run("""
                MATCH (c:Course), (cc:CourseConsolidation)
                WHERE ID(c) = $course_id AND ID(cc) = $consolidation_node_id
                MERGE (c)-[:HAS_MATERIALS]->(cc)
            """, course_id=course_id, consolidation_node_id=consolidation_node_id)
            
            # 2. Course consolidation -> Document-specific nodes
            for doc_node_id in document_node_ids:
                session.run("""
                    MATCH (cc:CourseConsolidation), (dl:DocumentLink)
                    WHERE ID(cc) = $consolidation_node_id AND ID(dl) = $doc_node_id
                    MERGE (cc)-[:CONTAINS_DOCUMENT]->(dl)
                """, consolidation_node_id=consolidation_node_id, doc_node_id=doc_node_id)
            
            # 3. Document-specific nodes -> Entities từ từng document
            for i, doc_node_id in enumerate(document_node_ids):
                doc_id = documents[i]['doc_id']
                
                # Link đến entities của document này
                result = session.run("""
                    MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
                    WHERE ID(d) = $doc_id
                    WITH collect(DISTINCT ID(e)) as entity_ids
                    
                    MATCH (dl:DocumentLink), (e:__Entity__)
                    WHERE ID(dl) = $doc_node_id AND ID(e) IN entity_ids
                    MERGE (dl)-[:EXTRACTED_ENTITY]->(e)
                    RETURN count(*) as relationships_created
                """, doc_id=doc_id, doc_node_id=doc_node_id)
                
                record = result.single()
                if record:
                    count = record['relationships_created']
                    logger.info(f"Created {count} EXTRACTED_ENTITY relationships for document {documents[i]['filename']}")
        
        logger.info(f"Created all relationships for course consolidation")
    
    def process_multi_document_course(self, course_code: str, documents: List[Dict]) -> bool:
        """
        Xử lý một course có nhiều documents
        
        Args:
            course_code: Course code
            documents: List of documents for this course
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Processing course {course_code} with {len(documents)} documents")
        
        # 1. Tìm course framework
        course_framework = self.find_course_framework(course_code)
        if not course_framework:
            logger.error(f"No course framework found for {course_code}")
            return False
        
        # 2. Tạo course consolidation node
        consolidation_node_id = self.create_course_consolidation_node(course_code, documents)
        if not consolidation_node_id:
            logger.error(f"Failed to create consolidation node for {course_code}")
            return False
        
        # 3. Tạo document-specific nodes
        document_node_ids = self.create_document_specific_nodes(course_code, documents)
        if len(document_node_ids) != len(documents):
            logger.error(f"Failed to create all document nodes for {course_code}")
            return False
        
        # 4. Tạo relationships
        self.create_course_relationships(
            course_framework['course_id'],
            consolidation_node_id,
            document_node_ids,
            documents
        )
        
        logger.info(f"Successfully processed course {course_code}")
        return True
    
    def process_all_multi_document_courses(self) -> Dict[str, any]:
        """
        Xử lý tất cả courses, đặc biệt focus vào multi-document courses
        
        Returns:
            Processing statistics
        """
        logger.info("Starting multi-document course processing...")
        
        # Lấy documents grouped by course
        documents_by_course = self.get_documents_grouped_by_course()
        
        if not documents_by_course:
            logger.info("No documents with course codes found")
            return {"total_courses": 0, "processed": 0, "failed": 0}
        
        stats = {
            "total_courses": len(documents_by_course),
            "single_document_courses": 0,
            "multi_document_courses": 0,
            "processed": 0,
            "failed": 0,
            "course_details": {}
        }
        
        for course_code, documents in documents_by_course.items():
            if len(documents) == 1:
                stats["single_document_courses"] += 1
                logger.info(f"Course {course_code}: Single document - {documents[0]['filename']}")
            else:
                stats["multi_document_courses"] += 1
                logger.info(f"Course {course_code}: Multiple documents ({len(documents)} files)")
                for doc in documents:
                    logger.info(f"  - {doc['filename']}")
            
            # Process course
            try:
                success = self.process_multi_document_course(course_code, documents)
                if success:
                    stats["processed"] += 1
                    stats["course_details"][course_code] = {
                        "status": "success",
                        "document_count": len(documents),
                        "documents": [doc['filename'] for doc in documents]
                    }
                else:
                    stats["failed"] += 1
                    stats["course_details"][course_code] = {
                        "status": "failed",
                        "document_count": len(documents),
                        "error": "Processing failed"
                    }
            except Exception as e:
                logger.error(f"Error processing course {course_code}: {str(e)}")
                stats["failed"] += 1
                stats["course_details"][course_code] = {
                    "status": "error",
                    "document_count": len(documents),
                    "error": str(e)
                }
        
        logger.info(f"Processing complete!")
        logger.info(f"Total courses: {stats['total_courses']}")
        logger.info(f"Single document courses: {stats['single_document_courses']}")
        logger.info(f"Multi-document courses: {stats['multi_document_courses']}")
        logger.info(f"Successfully processed: {stats['processed']}")
        logger.info(f"Failed: {stats['failed']}")
        
        return stats
    
    def get_multi_document_statistics(self) -> Dict:
        """
        Lấy thống kê về multi-document courses
        
        Returns:
            Statistics dictionary
        """
        query = """
        // Thống kê courses và documents
        MATCH (cc:CourseConsolidation)
        OPTIONAL MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl:DocumentLink)
        OPTIONAL MATCH (dl)-[:EXTRACTED_ENTITY]->(e:__Entity__)
        
        RETURN 
            cc.course_code as course_code,
            cc.document_count as document_count,
            count(DISTINCT dl) as document_nodes,
            count(DISTINCT e) as total_entities
        ORDER BY cc.course_code
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            
            statistics = {
                "courses": [],
                "total_consolidation_nodes": 0,
                "total_document_nodes": 0,
                "total_entities_linked": 0
            }
            
            for record in result:
                course_stat = {
                    "course_code": record["course_code"],
                    "document_count": record["document_count"],
                    "document_nodes": record["document_nodes"],
                    "total_entities": record["total_entities"]
                }
                statistics["courses"].append(course_stat)
                statistics["total_consolidation_nodes"] += 1
                statistics["total_document_nodes"] += record["document_nodes"]
                statistics["total_entities_linked"] += record["total_entities"]
        
        return statistics


def main():
    """Main function to run the multi-document curriculum linker"""
    # Database configuration
    uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Initialize linker
    linker = MultiDocumentCurriculumLinker(uri, username, password, database)
    
    try:
        # Process all multi-document courses
        stats = linker.process_all_multi_document_courses()
        
        print("\n" + "="*60)
        print("MULTI-DOCUMENT CURRICULUM LINKING RESULTS")
        print("="*60)
        print(f"Total courses found: {stats['total_courses']}")
        print(f"Single document courses: {stats['single_document_courses']}")
        print(f"Multi-document courses: {stats['multi_document_courses']}")
        print(f"Successfully processed: {stats['processed']}")
        print(f"Failed: {stats['failed']}")
        
        print("\nCourse Details:")
        for course_code, details in stats['course_details'].items():
            print(f"\n{course_code}:")
            print(f"  Status: {details['status']}")
            print(f"  Documents: {details['document_count']}")
            if details['status'] == 'success':
                for doc in details['documents']:
                    print(f"    - {doc}")
            elif 'error' in details:
                print(f"  Error: {details['error']}")
        
        # Show final statistics
        final_stats = linker.get_multi_document_statistics()
        print("\n" + "="*60)
        print("FINAL LINKING STATISTICS")
        print("="*60)
        print(f"Total consolidation nodes: {final_stats['total_consolidation_nodes']}")
        print(f"Total document nodes: {final_stats['total_document_nodes']}")
        print(f"Total entities linked: {final_stats['total_entities_linked']}")
        
        print("\nPer-course breakdown:")
        for course in final_stats['courses']:
            print(f"{course['course_code']}: {course['document_count']} docs, {course['total_entities']} entities")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise
    finally:
        linker.close()


if __name__ == "__main__":
    main()
