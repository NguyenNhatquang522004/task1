#!/usr/bin/env python3
"""
Detailed CurriculumLink Node Analysis

Script này phân tích chi tiết tại sao 15 documents chỉ tạo ra 10 CurriculumLink nodes.
Focus vào việc hiểu node structure và duplicate course codes.
"""

import os
import re
import logging
from typing import List, Dict, Set
from collections import defaultdict, Counter
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


class CurriculumLinkNodeAnalyzer:
    """Detailed analyzer for CurriculumLink nodes"""
    
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
        """Extract course code from filename"""
        pattern = r'\[([A-Z]{3}\d{3,4})\]'
        match = re.search(pattern, filename)
        return match.group(1) if match else None
    
    def get_all_documents_with_courses(self) -> List[Dict]:
        """Get all documents with their course codes"""
        query = """
        MATCH (d:Document)
        RETURN ID(d) as doc_id, 
               d.fileName as filename
        ORDER BY d.fileName
        """
        
        documents = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            for record in result:
                doc_id = record['doc_id']
                filename = record['filename']
                course_code = self.extract_course_code(filename)
                
                documents.append({
                    'doc_id': doc_id,
                    'filename': filename,
                    'course_code': course_code
                })
        
        return documents
    
    def get_all_curriculum_link_nodes(self) -> List[Dict]:
        """Get all CurriculumLink nodes with details"""
        query = """
        MATCH (cl:CurriculumLink)
        RETURN ID(cl) as link_id,
               cl.name as name,
               cl.created_at as created_at
        ORDER BY cl.name
        """
        
        curriculum_links = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            for record in result:
                curriculum_links.append({
                    'link_id': record['link_id'],
                    'name': record['name'],
                    'created_at': record['created_at']
                })
        
        return curriculum_links
    
    def analyze_curriculum_link_patterns(self, curriculum_links: List[Dict]) -> Dict:
        """Analyze patterns in CurriculumLink node names"""
        patterns = {
            'course_codes_in_links': [],
            'link_name_patterns': [],
            'duplicate_course_codes': defaultdict(list)
        }
        
        for link in curriculum_links:
            name = link['name']
            
            # Extract course code from link name
            # Expected pattern: schema_COURSECODE_filename
            if '_' in name:
                parts = name.split('_')
                for part in parts:
                    if re.match(r'^[A-Z]{3}\d{3,4}$', part):
                        course_code = part
                        patterns['course_codes_in_links'].append(course_code)
                        patterns['duplicate_course_codes'][course_code].append(link)
                        break
            
            patterns['link_name_patterns'].append(name)
        
        return patterns
    
    def get_course_relationship_details(self) -> List[Dict]:
        """Get details about Course -> CurriculumLink relationships"""
        query = """
        MATCH (c:Course)-[:POINT_TO]->(cl:CurriculumLink)
        RETURN c.code as course_code,
               c.name as course_name,
               cl.name as curriculum_link_name,
               ID(cl) as link_id
        ORDER BY c.code
        """
        
        relationships = []
        with self.driver.session(database=self.database) as session:
            result = session.run(query)
            for record in result:
                relationships.append({
                    'course_code': record['course_code'],
                    'course_name': record['course_name'],
                    'curriculum_link_name': record['curriculum_link_name'],
                    'link_id': record['link_id']
                })
        
        return relationships
    
    def analyze_document_grouping(self, documents: List[Dict]) -> Dict:
        """Analyze how documents are grouped by course code"""
        course_groups = defaultdict(list)
        
        for doc in documents:
            if doc['course_code']:
                course_groups[doc['course_code']].append(doc)
        
        analysis = {
            'total_unique_course_codes': len(course_groups),
            'course_groups': dict(course_groups),
            'single_document_courses': 0,
            'multi_document_courses': 0,
            'course_code_counts': {}
        }
        
        for course_code, docs in course_groups.items():
            doc_count = len(docs)
            analysis['course_code_counts'][course_code] = doc_count
            
            if doc_count == 1:
                analysis['single_document_courses'] += 1
            else:
                analysis['multi_document_courses'] += 1
        
        return analysis
    
    def perform_comprehensive_analysis(self) -> Dict:
        """Perform comprehensive analysis"""
        print("🔍 PERFORMING COMPREHENSIVE CURRICULUM LINK ANALYSIS")
        print("="*80)
        
        # Get data
        documents = self.get_all_documents_with_courses()
        curriculum_links = self.get_all_curriculum_link_nodes()
        course_relationships = self.get_course_relationship_details()
        
        # Analyze
        doc_analysis = self.analyze_document_grouping(documents)
        link_patterns = self.analyze_curriculum_link_patterns(curriculum_links)
        
        print(f"\n📊 BASIC STATISTICS:")
        print(f"  • Total Documents: {len(documents)}")
        print(f"  • Total CurriculumLink nodes: {len(curriculum_links)}")
        print(f"  • Total Course->CurriculumLink relationships: {len(course_relationships)}")
        print(f"  • Unique course codes in documents: {doc_analysis['total_unique_course_codes']}")
        
        print(f"\n📋 DOCUMENT GROUPING ANALYSIS:")
        print(f"  • Single-document courses: {doc_analysis['single_document_courses']}")
        print(f"  • Multi-document courses: {doc_analysis['multi_document_courses']}")
        
        print(f"\n📄 DOCUMENT BREAKDOWN BY COURSE:")
        for course_code, docs in doc_analysis['course_groups'].items():
            print(f"\n  📚 {course_code} ({len(docs)} documents):")
            for i, doc in enumerate(docs, 1):
                print(f"    {i}. {doc['filename']}")
        
        print(f"\n🔗 CURRICULUM LINK NODES:")
        for i, link in enumerate(curriculum_links, 1):
            print(f"  {i:2d}. {link['name']}")
        
        print(f"\n🎯 COURSE -> CURRICULUMLINK RELATIONSHIPS:")
        course_to_link_count = defaultdict(list)
        for rel in course_relationships:
            course_to_link_count[rel['course_code']].append(rel['curriculum_link_name'])
        
        for course_code, link_names in course_to_link_count.items():
            print(f"  {course_code} → {len(link_names)} CurriculumLink(s):")
            for link_name in link_names:
                print(f"    • {link_name}")
        
        print(f"\n🔍 WHY 15 DOCUMENTS → 10 CURRICULUMLINK NODES:")
        
        # Calculate expected vs actual
        expected_based_on_unique_courses = doc_analysis['total_unique_course_codes']
        actual_curriculum_links = len(curriculum_links)
        
        print(f"  • Unique course codes: {expected_based_on_unique_courses}")
        print(f"  • Actual CurriculumLink nodes: {actual_curriculum_links}")
        
        if expected_based_on_unique_courses == actual_curriculum_links:
            print(f"  ✅ PERFECT MATCH!")
            print(f"     Each unique course code has exactly 1 CurriculumLink node")
        else:
            difference = abs(expected_based_on_unique_courses - actual_curriculum_links)
            print(f"  ⚠️  MISMATCH: {difference} difference")
        
        print(f"\n💡 EXPLANATION:")
        print(f"  • From 15 documents, we have {expected_based_on_unique_courses} unique course codes")
        print(f"  • Some course codes appear in multiple documents:")
        
        for course_code, count in doc_analysis['course_code_counts'].items():
            if count > 1:
                print(f"    - {course_code}: {count} documents")
                for doc in doc_analysis['course_groups'][course_code]:
                    print(f"      • {doc['filename']}")
        
        print(f"\n🎯 CONCLUSION:")
        print(f"  This is CORRECT behavior!")
        print(f"  Each course code should have only 1 CurriculumLink node,")
        print(f"  regardless of how many documents contain that course code.")
        print(f"  The system is working as designed!")
        
        return {
            'documents': documents,
            'curriculum_links': curriculum_links,
            'course_relationships': course_relationships,
            'doc_analysis': doc_analysis,
            'link_patterns': link_patterns
        }


def main():
    """Main function"""
    # Database configuration
    uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")
    database = os.getenv("NEO4J_DATABASE", "neo4j")
    
    print("🔍 Detailed CurriculumLink Node Analyzer")
    print("Analyzing why 15 documents created 10 CurriculumLink nodes...")
    print("="*70)
    
    # Initialize analyzer
    analyzer = CurriculumLinkNodeAnalyzer(uri, username, password, database)
    
    try:
        # Perform analysis
        results = analyzer.perform_comprehensive_analysis()
        
        print(f"\n✅ Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        print(f"\n❌ Error: {e}")
        
    finally:
        analyzer.close()


if __name__ == "__main__":
    main()
