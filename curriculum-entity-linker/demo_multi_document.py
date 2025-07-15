"""
Demo script for Multi-Document Curriculum Linker

This script demonstrates how to handle multiple files with the same course code (e.g., CMP3025)
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from multi_document_linker import MultiDocumentCurriculumLinker
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_multi_document_processing():
    """Demo function showing multi-document processing"""
    
    print("="*70)
    print("MULTI-DOCUMENT CURRICULUM LINKER DEMO")
    print("="*70)
    print()
    print("This demo handles multiple files with same course code:")
    print("Example: CMP3025 có thể có:")
    print("  - [CMP3025] GIÁO TRÌNH THỰC HÀNH LẬP TRÌNH JAVA 2024 - 2005.pdf")
    print("  - [CMP3025] Bài tập thực hành Java.pdf") 
    print("  - [CMP3025] Lab exercises.pdf")
    print()
    
    # Database configuration
    uri = "neo4j://127.0.0.1:7687"
    username = "neo4j"
    password = "12345678"
    database = "neo4j"
    
    try:
        # Initialize linker
        print("Connecting to Neo4j...")
        linker = MultiDocumentCurriculumLinker(uri, username, password, database)
        
        print("\n1. Analyzing current documents by course code...")
        documents_by_course = linker.get_documents_grouped_by_course()
        
        if not documents_by_course:
            print("❌ No documents with course codes found!")
            print("Make sure you have documents with format: [CMP3025] Document Name")
            return
        
        print(f"\n📊 Found {len(documents_by_course)} unique course codes:")
        
        multi_doc_courses = []
        single_doc_courses = []
        
        for course_code, docs in documents_by_course.items():
            if len(docs) > 1:
                multi_doc_courses.append((course_code, docs))
                print(f"🔄 {course_code}: {len(docs)} documents (MULTI-DOCUMENT)")
                for doc in docs:
                    print(f"    📄 {doc['filename']}")
            else:
                single_doc_courses.append((course_code, docs))
                print(f"📄 {course_code}: 1 document")
                print(f"    📄 {docs[0]['filename']}")
        
        print(f"\n📈 Summary:")
        print(f"  • Multi-document courses: {len(multi_doc_courses)}")
        print(f"  • Single-document courses: {len(single_doc_courses)}")
        
        if multi_doc_courses:
            print(f"\n🎯 Multi-document courses requiring special handling:")
            for course_code, docs in multi_doc_courses:
                print(f"  {course_code}: {len(docs)} files")
        
        print(f"\n2. Processing all courses with enhanced multi-document support...")
        stats = linker.process_all_multi_document_courses()
        
        print(f"\n✅ Processing Results:")
        print(f"  • Total courses: {stats['total_courses']}")
        print(f"  • Single-document courses: {stats['single_document_courses']}")
        print(f"  • Multi-document courses: {stats['multi_document_courses']}")
        print(f"  • Successfully processed: {stats['processed']}")
        print(f"  • Failed: {stats['failed']}")
        
        if stats['failed'] > 0:
            print(f"\n⚠️  Failed courses:")
            for course_code, details in stats['course_details'].items():
                if details['status'] != 'success':
                    print(f"    {course_code}: {details.get('error', 'Unknown error')}")
        
        print(f"\n3. Getting final linking statistics...")
        final_stats = linker.get_multi_document_statistics()
        
        print(f"\n📊 Final Statistics:")
        print(f"  • Consolidation nodes created: {final_stats['total_consolidation_nodes']}")
        print(f"  • Document nodes created: {final_stats['total_document_nodes']}")
        print(f"  • Total entities linked: {final_stats['total_entities_linked']}")
        
        print(f"\n📋 Per-course breakdown:")
        for course in final_stats['courses']:
            print(f"  {course['course_code']}: {course['document_count']} docs → {course['total_entities']} entities")
        
        print(f"\n4. New Graph Structure Created:")
        print(f"")
        print(f"Course Framework")
        print(f"       ↓ [HAS_MATERIALS]")
        print(f"CourseConsolidation (per course code)")
        print(f"       ↓ [CONTAINS_DOCUMENT]")
        print(f"DocumentLink (per file)")
        print(f"       ↓ [EXTRACTED_ENTITY]")
        print(f"__Entity__ (from each file)")
        print(f"")
        
        print(f"✅ Multi-document curriculum linking completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.error(f"Demo failed: {e}")
        raise
    finally:
        if 'linker' in locals():
            linker.close()

def show_example_cypher_queries():
    """Show example Cypher queries for the new structure"""
    
    print("\n" + "="*70)
    print("EXAMPLE CYPHER QUERIES FOR MULTI-DOCUMENT STRUCTURE")
    print("="*70)
    
    queries = [
        {
            "title": "1. Find all documents for a specific course",
            "query": """
MATCH (c:Course {code: 'CMP3025'})-[:HAS_MATERIALS]->(cc:CourseConsolidation)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl:DocumentLink)
RETURN c.name as course_name, 
       cc.description as consolidation_info,
       dl.original_filename as document_name,
       dl.document_id as doc_id
            """
        },
        {
            "title": "2. Find all entities from all documents of a course",
            "query": """
MATCH (c:Course {code: 'CMP3025'})-[:HAS_MATERIALS]->(cc:CourseConsolidation)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl:DocumentLink)
MATCH (dl)-[:EXTRACTED_ENTITY]->(e:__Entity__)
RETURN c.name as course_name,
       dl.original_filename as from_document,
       e.name as entity_name,
       e.type as entity_type
ORDER BY dl.original_filename, e.name
            """
        },
        {
            "title": "3. Count entities per document within a course",
            "query": """
MATCH (c:Course {code: 'CMP3025'})-[:HAS_MATERIALS]->(cc:CourseConsolidation)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl:DocumentLink)
OPTIONAL MATCH (dl)-[:EXTRACTED_ENTITY]->(e:__Entity__)
RETURN dl.original_filename as document,
       count(e) as entity_count
ORDER BY entity_count DESC
            """
        },
        {
            "title": "4. Find courses with multiple documents",
            "query": """
MATCH (c:Course)-[:HAS_MATERIALS]->(cc:CourseConsolidation)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl:DocumentLink)
WITH c, cc, count(dl) as doc_count
WHERE doc_count > 1
RETURN c.code as course_code,
       c.name as course_name,
       doc_count as document_count,
       cc.description as consolidation_info
ORDER BY doc_count DESC
            """
        },
        {
            "title": "5. Cross-document entity analysis within same course",
            "query": """
MATCH (c:Course {code: 'CMP3025'})-[:HAS_MATERIALS]->(cc:CourseConsolidation)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl1:DocumentLink)
MATCH (cc)-[:CONTAINS_DOCUMENT]->(dl2:DocumentLink)
MATCH (dl1)-[:EXTRACTED_ENTITY]->(e1:__Entity__)
MATCH (dl2)-[:EXTRACTED_ENTITY]->(e2:__Entity__)
WHERE dl1 <> dl2 AND e1.name = e2.name
RETURN e1.name as shared_entity,
       dl1.original_filename as document1,
       dl2.original_filename as document2
            """
        }
    ]
    
    for i, query_info in enumerate(queries, 1):
        print(f"\n{query_info['title']}:")
        print("-" * len(query_info['title']))
        print(query_info['query'].strip())
        if i < len(queries):
            print()

if __name__ == "__main__":
    print("🚀 Starting Multi-Document Curriculum Linker Demo...")
    
    try:
        # Run the main demo
        demo_multi_document_processing()
        
        # Show example queries
        show_example_cypher_queries()
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"\nNext steps:")
        print(f"1. Check your Neo4j database for the new CourseConsolidation and DocumentLink nodes")
        print(f"2. Run the example Cypher queries to explore the data")
        print(f"3. Use this structure for cross-document analysis within courses")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        sys.exit(1)
