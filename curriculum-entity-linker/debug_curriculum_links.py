#!/usr/bin/env python3
"""
Debug Script - Curriculum Link Analysis

Script này phân tích tại sao số lượng CurriculumLink nodes ít hơn số lượng Document nodes.
Kiểm tra các nguyên nhân có thể:
1. Document không có course code trong filename
2. Course code không match với curriculum framework
3. Document đã được link rồi (duplicate prevention)
4. Lỗi trong quá trình xử lý
"""

import os
import re
import logging
from typing import List, Dict, Tuple
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


class CurriculumLinkDebugger:
    """Class để debug curriculum linking issues"""
    
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
    
    def extract_course_code(self, filename: str) -> str:
        """Extract course code from filename using regex"""
        pattern = r'\[([A-Z]{3}\d{3,4})\]'
        match = re.search(pattern, filename)
        return match.group(1) if match else None
    
    def get_all_documents(self) -> List[Dict]:
        """Get all Document nodes with details"""
        query = """
        MATCH (d:Document)
        RETURN ID(d) as doc_id, 
               d.fileName as filename,
               d.schema as schema
        ORDER BY d.fileName
        """
        
        documents = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            for record in result:
                documents.append({
                    'doc_id': record['doc_id'],
                    'filename': record['filename'],
                    'schema': record['schema']
                })
        
        return documents
    
    def get_all_curriculum_links(self) -> List[Dict]:
        """Get all CurriculumLink nodes"""
        query = """
        MATCH (cl:CurriculumLink)
        RETURN ID(cl) as link_id,
               cl.name as name,
               cl.created_at as created_at
        ORDER BY cl.name
        """
        
        links = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            for record in result:
                links.append({
                    'link_id': record['link_id'],
                    'name': record['name'],
                    'created_at': record['created_at']
                })
        
        return links
    
    def get_available_courses(self) -> List[Dict]:
        """Get all Course framework nodes (not extracted entities)"""
        query = """
        MATCH (c:Course)
        WHERE NOT c:__Entity__
        RETURN c.code as code, 
               c.name as name,
               ID(c) as course_id
        ORDER BY c.code
        """
        
        courses = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            for record in result:
                courses.append({
                    'code': record['code'],
                    'name': record['name'],
                    'course_id': record['course_id']
                })
        
        return courses
    
    def check_document_entities(self, doc_id: int) -> int:
        """Check how many entities are linked to a document"""
        query = """
        MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
        WHERE ID(d) = $doc_id
        RETURN count(DISTINCT e) as entity_count
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, doc_id=doc_id)
            record = result.single()
            return record['entity_count'] if record else 0
    
    def check_existing_links_for_document(self, doc_id: int) -> List[Dict]:
        """Check if document already has CurriculumLink connections"""
        query = """
        MATCH (d:Document)
        WHERE ID(d) = $doc_id
        
        OPTIONAL MATCH (c:Course)-[:POINT_TO]->(cl:CurriculumLink)-[:HAVE_TO]->(e:__Entity__)
        WHERE (d)-[:FIRST_CHUNK]->(:Chunk)-[:HAS_ENTITY]->(e)
        
        RETURN c.code as course_code, 
               cl.name as link_name, 
               count(e) as linked_entities
        """
        
        links = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query, doc_id=doc_id)
            for record in result:
                if record['course_code']:  # Only include actual links
                    links.append({
                        'course_code': record['course_code'],
                        'link_name': record['link_name'],
                        'linked_entities': record['linked_entities']
                    })
        
        return links
    
    def analyze_all_documents(self) -> Dict:
        """Comprehensive analysis of all documents"""
        documents = self.get_all_documents()
        curriculum_links = self.get_all_curriculum_links()
        available_courses = self.get_available_courses()
        
        course_codes = {course['code'] for course in available_courses}
        
        analysis = {
            'total_documents': len(documents),
            'total_curriculum_links': len(curriculum_links),
            'available_courses': len(available_courses),
            'documents_with_course_code': 0,
            'documents_with_valid_course_code': 0,
            'documents_with_entities': 0,
            'documents_already_linked': 0,
            'documents_should_be_processed': 0,
            'detailed_analysis': []
        }
        
        for doc in documents:
            doc_id = doc['doc_id']
            filename = doc['filename']
            schema = doc['schema']
            
            # Extract course code
            course_code = self.extract_course_code(filename)
            
            # Check entities
            entity_count = self.check_document_entities(doc_id)
            
            # Check existing links
            existing_links = self.check_existing_links_for_document(doc_id)
            
            # Analyze this document
            doc_analysis = {
                'doc_id': doc_id,
                'filename': filename,
                'schema': schema,
                'course_code': course_code,
                'has_course_code': course_code is not None,
                'valid_course_code': course_code in course_codes if course_code else False,
                'entity_count': entity_count,
                'has_entities': entity_count > 0,
                'existing_links': existing_links,
                'already_linked': len(existing_links) > 0,
                'should_be_processed': False
            }
            
            # Determine if should be processed
            if (doc_analysis['has_course_code'] and 
                doc_analysis['valid_course_code'] and 
                doc_analysis['has_entities'] and 
                not doc_analysis['already_linked']):
                doc_analysis['should_be_processed'] = True
                analysis['documents_should_be_processed'] += 1
            
            # Update counters
            if doc_analysis['has_course_code']:
                analysis['documents_with_course_code'] += 1
            
            if doc_analysis['valid_course_code']:
                analysis['documents_with_valid_course_code'] += 1
            
            if doc_analysis['has_entities']:
                analysis['documents_with_entities'] += 1
            
            if doc_analysis['already_linked']:
                analysis['documents_already_linked'] += 1
            
            analysis['detailed_analysis'].append(doc_analysis)
        
        return analysis
    
    def print_detailed_report(self, analysis: Dict):
        """Print detailed analysis report"""
        print("="*80)
        print("🔍 CURRICULUM LINK DEBUG ANALYSIS REPORT")
        print("="*80)
        
        print(f"\n📊 OVERVIEW:")
        print(f"  • Total Documents: {analysis['total_documents']}")
        print(f"  • Total CurriculumLink nodes: {analysis['total_curriculum_links']}")
        print(f"  • Available Course codes: {analysis['available_courses']}")
        
        print(f"\n📋 DOCUMENT ANALYSIS:")
        print(f"  • Documents with course code in filename: {analysis['documents_with_course_code']}")
        print(f"  • Documents with VALID course code: {analysis['documents_with_valid_course_code']}")
        print(f"  • Documents with extracted entities: {analysis['documents_with_entities']}")
        print(f"  • Documents already linked: {analysis['documents_already_linked']}")
        print(f"  • Documents should be processed: {analysis['documents_should_be_processed']}")
        
        print(f"\n🎯 EXPECTED vs ACTUAL:")
        expected_links = analysis['documents_should_be_processed']
        actual_links = analysis['total_curriculum_links']
        print(f"  • Expected CurriculumLink nodes: {expected_links}")
        print(f"  • Actual CurriculumLink nodes: {actual_links}")
        
        if expected_links != actual_links:
            print(f"  ⚠️  MISMATCH DETECTED: {abs(expected_links - actual_links)} difference")
        else:
            print(f"  ✅ Numbers match perfectly!")
        
        print(f"\n📄 DETAILED DOCUMENT BREAKDOWN:")
        print("-" * 80)
        
        for i, doc in enumerate(analysis['detailed_analysis'], 1):
            status_icons = []
            
            if not doc['has_course_code']:
                status_icons.append("❌ No course code")
            elif not doc['valid_course_code']:
                status_icons.append("⚠️  Invalid course code")
            elif not doc['has_entities']:
                status_icons.append("📭 No entities")
            elif doc['already_linked']:
                status_icons.append("🔗 Already linked")
            elif doc['should_be_processed']:
                status_icons.append("✅ Ready to process")
            
            status = " | ".join(status_icons) if status_icons else "❓ Unknown"
            
            print(f"\n{i:2d}. {doc['filename'][:60]}...")
            print(f"    Course Code: {doc['course_code'] or 'None'}")
            print(f"    Schema: {doc['schema'] or 'None'}")
            print(f"    Entities: {doc['entity_count']}")
            print(f"    Status: {status}")
            
            if doc['existing_links']:
                print(f"    Existing Links: {len(doc['existing_links'])}")
                for link in doc['existing_links']:
                    print(f"      → {link['course_code']}: {link['linked_entities']} entities")
        
        print(f"\n💡 POSSIBLE REASONS FOR MISMATCH:")
        
        no_course_code = analysis['total_documents'] - analysis['documents_with_course_code']
        invalid_course_code = analysis['documents_with_course_code'] - analysis['documents_with_valid_course_code']
        no_entities = analysis['documents_with_valid_course_code'] - analysis['documents_with_entities']
        
        if no_course_code > 0:
            print(f"  • {no_course_code} documents don't have course code in filename")
        
        if invalid_course_code > 0:
            print(f"  • {invalid_course_code} documents have invalid/unrecognized course codes")
        
        if no_entities > 0:
            print(f"  • {no_entities} documents don't have extracted entities")
        
        if analysis['documents_already_linked'] > 0:
            print(f"  • {analysis['documents_already_linked']} documents are already linked")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        
        if expected_links > actual_links:
            print(f"  1. Run curriculum_linker.py to create missing {expected_links - actual_links} links")
            
        if no_course_code > 0:
            print(f"  2. Check filename format for {no_course_code} documents (should contain [CODE] pattern)")
            
        if invalid_course_code > 0:
            print(f"  3. Verify {invalid_course_code} course codes exist in curriculum framework")
            
        if no_entities > 0:
            print(f"  4. Check why {no_entities} documents have no extracted entities")


def main():
    """Main function"""
    # Database configuration
    uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    print("🔍 Curriculum Link Debugger")
    print("Analyzing why 15 documents only created 9 CurriculumLink nodes...")
    print("="*70)
    
    # Initialize debugger
    debugger = CurriculumLinkDebugger(uri, username, password, database)
    
    try:
        # Perform analysis
        analysis = debugger.analyze_all_documents()
        
        # Print detailed report
        debugger.print_detailed_report(analysis)
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        print(f"\n❌ Error: {e}")
        
    finally:
        debugger.close()


if __name__ == "__main__":
    main()
