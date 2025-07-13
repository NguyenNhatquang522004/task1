#!/usr/bin/env python3
"""
Curriculum Entity Linker

Script này liên kết curriculum framework với extracted entities từ LLM Graph Builder.

Workflow:
1. Load curriculum framework 
2. Extract course codes từ document filenames
3. Match với course framework nodes
4. Tạo intermediate nodes và relationships
"""

import os
import re
import logging
from typing import List, Dict, Optional, Tuple
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CurriculumEntityLinker:
    """Main class for linking curriculum framework with extracted entities"""
    
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
        - '[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows' → 'CMP170'
        - '[MAT101] Đại số tuyến tính' → 'MAT101'
        
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
    
    def load_curriculum_framework(self, cql_file_path: str) -> bool:
        """
        Load curriculum framework từ CQL file
        
        Args:
            cql_file_path: Path to curriculum-syllabus-example.cql
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(cql_file_path, 'r', encoding='utf-8') as file:
                cql_content = file.read()
            
            # Split các statements CQL
            statements = [stmt.strip() for stmt in cql_content.split(';') if stmt.strip()]
            
            with self.driver.session(database=self.database) as session:
                for statement in statements:
                    if statement:
                        session.run(statement)
                        logger.debug(f"Executed: {statement[:100]}...")
                        
            logger.info(f"Successfully loaded curriculum framework from {cql_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading curriculum framework: {e}")
            return False
    
    def get_documents_with_course_codes(self) -> List[Dict]:
        """
        Lấy tất cả Document nodes và extract course codes
        
        Returns:
            List of dictionaries with document info and course codes
        """
        query = """
        MATCH (d:Document)
        WHERE d.fileName IS NOT NULL
        RETURN d.fileName as filename, d.schema as schema, 
               ID(d) as doc_id, d as document
        """
        
        documents = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            
            for record in result:
                filename = record['filename']
                schema = record['schema']
                doc_id = record['doc_id']
                
                course_code = self.extract_course_code(filename)
                
                if course_code:
                    documents.append({
                        'doc_id': doc_id,
                        'filename': filename,
                        'schema': schema,
                        'course_code': course_code
                    })
                    logger.info(f"Found document with course code: {course_code} - {filename}")
        
        logger.info(f"Found {len(documents)} documents with course codes")
        return documents
    
    def is_document_already_linked(self, doc_id: int) -> bool:
        """
        Kiểm tra xem document đã được link chưa
        
        Args:
            doc_id: Document node ID
            
        Returns:
            True nếu đã được link, False nếu chưa
        """
        query = """
        MATCH (d:Document)-[:HAS_ENTITY]->(e)<-[:HAVE_TO]-(a:CurriculumLink)<-[:POINT_TO]-(c:Course)
        WHERE ID(d) = $doc_id
        RETURN count(a) as link_count
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, doc_id=doc_id)
            record = result.single()
            
            if record and record['link_count'] > 0:
                logger.debug(f"Document ID {doc_id} is already linked")
                return True
            
        return False
    
    def get_unlinked_documents(self) -> List[Dict]:
        """
        Lấy các documents chưa được link
        
        Returns:
            List of dictionaries with unlinked document info
        """
        all_docs = self.get_documents_with_course_codes()
        unlinked_docs = []
        
        for doc in all_docs:
            if not self.is_document_already_linked(doc['doc_id']):
                unlinked_docs.append(doc)
            else:
                logger.info(f"Skipping already linked document: {doc['course_code']} - {doc['filename']}")
        
        logger.info(f"Found {len(unlinked_docs)} unlinked documents out of {len(all_docs)} total")
        return unlinked_docs
    
    def find_course_framework(self, course_code: str) -> Optional[Dict]:
        """
        Tìm Course framework node tương ứng với course code
        
        Args:
            course_code: Course code (ví dụ: CMP170)
            
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
                    'name': record['name']
                }
                logger.debug(f"Found course framework: {course_code} - {record['name']}")
                return course_info
            
        logger.debug(f"No course framework found for: {course_code}")
        return None
    
    def create_intermediate_node(self, schema: str, filename: str) -> str:
        """
        Tạo node trung gian (Node A) với tên = schema + filename
        
        Args:
            schema: Schema name
            filename: Document filename
            
        Returns:
            Node name
        """
        # Tạo tên node từ schema và filename
        if schema:
            node_name = f"{schema}_{filename}"
        else:
            node_name = f"curriculum_{filename}"
        
        # Làm sạch tên node (loại bỏ ký tự đặc biệt)
        node_name = re.sub(r'[^\w\s-]', '', node_name)
        node_name = re.sub(r'\s+', '_', node_name)
        
        query = """
        MERGE (a:CurriculumLink {name: $node_name})
        ON CREATE SET a.created_at = datetime()
        RETURN ID(a) as node_id, a.name as name
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, node_name=node_name)
            record = result.single()
            
            if record:
                logger.info(f"Created/found intermediate node: {node_name}")
                return record['node_id']
        
        return None
    
    def create_point_to_relationship(self, course_id: int, intermediate_node_id: int):
        """
        Tạo relationship POINT_TO từ Course framework đến intermediate node
        
        Args:
            course_id: Course framework node ID
            intermediate_node_id: Intermediate node ID
        """
        query = """
        MATCH (c:Course), (a:CurriculumLink)
        WHERE ID(c) = $course_id AND ID(a) = $intermediate_node_id
        MERGE (c)-[:POINT_TO]->(a)
        """
        
        with self.driver.session(database=self.database) as session:
            session.run(query, course_id=course_id, intermediate_node_id=intermediate_node_id)
            logger.debug(f"Created POINT_TO relationship: Course({course_id}) -> CurriculumLink({intermediate_node_id})")
    
    def create_have_to_relationships(self, intermediate_node_id: int, doc_id: int):
        """
        Tạo relationship HAVE_TO từ intermediate node đến extracted entities
        
        Args:
            intermediate_node_id: Intermediate node ID
            doc_id: Document ID để tìm related entities
        """
        # Tìm tất cả entities liên quan đến document này
        query = """
        MATCH (d:Document)-[:HAS_ENTITY]->(e)
        WHERE ID(d) = $doc_id
        WITH collect(ID(e)) as entity_ids
        
        MATCH (a:CurriculumLink), (e)
        WHERE ID(a) = $intermediate_node_id AND ID(e) IN entity_ids
        MERGE (a)-[:HAVE_TO]->(e)
        RETURN count(*) as relationships_created
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, intermediate_node_id=intermediate_node_id, doc_id=doc_id)
            record = result.single()
            
            if record:
                count = record['relationships_created']
                logger.info(f"Created {count} HAVE_TO relationships for intermediate node {intermediate_node_id}")
    
    def process_all_documents(self, force_relink: bool = False):
        """
        Xử lý tất cả documents và tạo các liên kết
        
        Args:
            force_relink: Nếu True, sẽ link lại tất cả documents (kể cả đã link)
        """
        logger.info("Starting document processing...")
        
        # Lấy documents cần xử lý
        if force_relink:
            logger.info("Force relink mode: Processing all documents")
            documents = self.get_documents_with_course_codes()
        else:
            logger.info("Normal mode: Processing only unlinked documents")
            documents = self.get_unlinked_documents()
        
        if not documents:
            logger.info("No documents to process")
            return
        
        processed_count = 0
        skipped_count = 0
        
        for doc in documents:
            course_code = doc['course_code']
            filename = doc['filename']
            schema = doc['schema']
            doc_id = doc['doc_id']
            
            logger.info(f"Processing: {course_code} - {filename}")
            
            # Tìm course framework
            course_framework = self.find_course_framework(course_code)
            
            if not course_framework:
                logger.warning(f"No course framework found for {course_code}, skipping...")
                skipped_count += 1
                continue
            
            # Tạo intermediate node
            intermediate_node_id = self.create_intermediate_node(schema, filename)
            
            if not intermediate_node_id:
                logger.error(f"Failed to create intermediate node for {filename}")
                skipped_count += 1
                continue
            
            # Tạo relationships
            self.create_point_to_relationship(course_framework['course_id'], intermediate_node_id)
            self.create_have_to_relationships(intermediate_node_id, doc_id)
            
            processed_count += 1
            logger.info(f"Successfully processed: {course_code} - {filename}")
        
        logger.info(f"Processing complete! Processed: {processed_count}, Skipped: {skipped_count}")
    
    def get_linking_status(self) -> Dict:
        """
        Lấy thống kê linking status
        
        Returns:
            Dictionary with linking statistics
        """
        query = """
        // Đếm tổng documents có course code
        MATCH (d:Document)
        WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        WITH count(d) as total_docs_with_code
        
        // Đếm documents đã được link
        MATCH (d:Document)-[:HAS_ENTITY]->(e)<-[:HAVE_TO]-(a:CurriculumLink)<-[:POINT_TO]-(c:Course)
        WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        WITH total_docs_with_code, count(DISTINCT d) as linked_docs
        
        // Đếm CurriculumLink nodes
        MATCH (a:CurriculumLink)
        WITH total_docs_with_code, linked_docs, count(a) as total_links
        
        // Đếm total entities được link
        MATCH (a:CurriculumLink)-[:HAVE_TO]->(e)
        RETURN total_docs_with_code, linked_docs, total_links, count(e) as total_linked_entities
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            record = result.single()
            
            if record:
                return {
                    'total_documents_with_code': record['total_docs_with_code'],
                    'linked_documents': record['linked_docs'],
                    'unlinked_documents': record['total_docs_with_code'] - record['linked_docs'],
                    'total_curriculum_links': record['total_links'],
                    'total_linked_entities': record['total_linked_entities']
                }
            
        return {
            'total_documents_with_code': 0,
            'linked_documents': 0,
            'unlinked_documents': 0,
            'total_curriculum_links': 0,
            'total_linked_entities': 0
        }


def main():
    """Main function"""
    import sys
    
    # Parse command line arguments
    force_relink = '--force' in sys.argv or '-f' in sys.argv
    status_only = '--status' in sys.argv or '-s' in sys.argv
    
    # Get environment variables
    uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
    username = os.getenv('NEO4J_USERNAME', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    # Initialize linker
    linker = CurriculumEntityLinker(uri, username, password, database)
    
    try:
        # Show current status
        if status_only or force_relink:
            logger.info("Checking current linking status...")
            status = linker.get_linking_status()
            
            print("\n" + "="*50)
            print("📊 LINKING STATUS REPORT")
            print("="*50)
            print(f"📋 Total documents with course codes: {status['total_documents_with_code']}")
            print(f"✅ Already linked documents: {status['linked_documents']}")
            print(f"⏳ Unlinked documents: {status['unlinked_documents']}")
            print(f"🔗 Total CurriculumLink nodes: {status['total_curriculum_links']}")
            print(f"📊 Total linked entities: {status['total_linked_entities']}")
            print("="*50)
            
            if status_only:
                return
        
        # Load curriculum framework
        cql_file_path = os.path.join(os.path.dirname(__file__), '..', 'curriculum-syllabus-example.cql')
        
        logger.info("Loading curriculum framework...")
        if linker.load_curriculum_framework(cql_file_path):
            logger.info("Curriculum framework loaded successfully")
        else:
            logger.error("Failed to load curriculum framework")
            return
        
        # Process documents
        if force_relink:
            logger.info("🔄 Force relink mode: Processing ALL documents")
            linker.process_all_documents(force_relink=True)
        else:
            logger.info("🆕 Normal mode: Processing only NEW/unlinked documents")
            linker.process_all_documents(force_relink=False)
        
        # Show final status
        logger.info("Checking final status...")
        final_status = linker.get_linking_status()
        
        print("\n" + "="*50)
        print("🎉 FINAL STATUS")
        print("="*50)
        print(f"✅ Linked documents: {final_status['linked_documents']}")
        print(f"⏳ Unlinked documents: {final_status['unlinked_documents']}")
        print(f"🔗 Total links created: {final_status['total_curriculum_links']}")
        print(f"📊 Total entities linked: {final_status['total_linked_entities']}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        
    finally:
        linker.close()


if __name__ == "__main__":
    import sys
    
    # Show usage if help requested
    if '--help' in sys.argv or '-h' in sys.argv:
        print("""
Curriculum Entity Linker - Usage:

python curriculum_linker.py              # Normal mode: Link only new documents
python curriculum_linker.py --force      # Force mode: Relink ALL documents  
python curriculum_linker.py --status     # Status mode: Show linking statistics only

Options:
  --force, -f     Force relink all documents (including already linked)
  --status, -s    Show linking status only (no processing)
  --help, -h      Show this help message
        """)
        sys.exit(0)
    
    main()
