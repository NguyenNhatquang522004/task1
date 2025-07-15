#!/usr/bin/env python3
"""
Query utilities for debugging and testing
"""

import os
import re
from typing import List, Dict

# Mock Neo4j queries for testing without actual database
class MockQueryResult:
    def __init__(self, data):
        self.data = data
    
    def __iter__(self):
        return iter(self.data)
    
    def single(self):
        return self.data[0] if self.data else None

def extract_course_code_regex(filename: str) -> str:
    """Extract course code using regex"""
    pattern = r'\[([A-Z]{3}\d{3,4})\]'
    match = re.search(pattern, filename)
    return match.group(1) if match else None

def preview_curriculum_data():
    """Preview curriculum data from CQL file"""
    cql_file_path = os.path.join(os.path.dirname(__file__), '..', 'curriculum-syllabus-example.cql')
    
    courses = []
    
    try:
        with open(cql_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract course information using regex
        course_pattern = r"MERGE \(c:Course \{code: '([^']+)'\}\) ON CREATE SET c = \{[^}]*name: '([^']+)'[^}]*\}"
        matches = re.findall(course_pattern, content)
        
        for code, name in matches:
            courses.append({'code': code, 'name': name})
        
        print(f"Found {len(courses)} courses in curriculum:")
        print("-" * 50)
        
        for i, course in enumerate(courses[:10]):  # Show first 10
            print(f"{i+1:2d}. {course['code']} - {course['name']}")
        
        if len(courses) > 10:
            print(f"... and {len(courses) - 10} more courses")
        
        return courses
        
    except Exception as e:
        print(f"Error reading curriculum file: {e}")
        return []

def generate_sample_cypher_queries():
    """Generate sample Cypher queries for manual testing"""
    
    queries = {
        "1. Load Curriculum Framework": """
        // Run the entire curriculum-syllabus-example.cql file first
        // This creates Course, Major, KnowledgeBlock nodes
        """,
        
        "2. Find Documents with Course Codes": """
        MATCH (d:Document)
        WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        WITH d, 
             [x IN split(d.fileName, '[') WHERE x CONTAINS ']'][0] as bracket_content,
             d.fileName as filename,
             d.schema as schema
        WITH d, filename, schema,
             [x IN split(bracket_content, ']')][0] as course_code
        WHERE course_code =~ '[A-Z]{3}\\d{3,4}'
        RETURN filename, schema, course_code, ID(d) as doc_id
        ORDER BY course_code
        """,
        
        "3. Find Course Framework (not extracted entities)": """
        MATCH (c:Course)
        WHERE NOT c:__Entity__  // Exclude LLM extracted entities
        RETURN c.code, c.name, ID(c) as course_id
        ORDER BY c.code
        """,
        
        "4. Sample: Create Intermediate Node": """
        // Example for CMP170 document with schema 'giáo_trình'
        MERGE (a:CurriculumLink {name: 'giáo_trình_CMP170_Đề_cương_HP_Lap_Trinh_Tren_Moi_Truong_Windows'})
        ON CREATE SET a.created_at = datetime()
        RETURN ID(a) as node_id, a.name as name
        """,
        
        "5. Sample: Create POINT_TO relationship": """
        // Link Course framework to CurriculumLink node
        MATCH (c:Course {code: 'CMP170'}), (a:CurriculumLink)
        WHERE a.name CONTAINS 'CMP170'
        MERGE (c)-[:POINT_TO]->(a)
        RETURN c.code, a.name
        """,
        
        "6. Sample: Create HAVE_TO relationships": """
        // Link CurriculumLink to extracted entities from document
        MATCH (d:Document)-[:HAS_ENTITY]->(e)
        WHERE d.fileName CONTAINS '[CMP170]'
        WITH collect(e) as entities
        
        MATCH (a:CurriculumLink)
        WHERE a.name CONTAINS 'CMP170'
        
        UNWIND entities as entity
        MERGE (a)-[:HAVE_TO]->(entity)
        RETURN a.name, count(entity) as entities_linked
        """,
        
        "7. Verify Complete Structure": """
        // Check the complete linking structure
        MATCH (c:Course)-[:POINT_TO]->(a:CurriculumLink)-[:HAVE_TO]->(e)
        RETURN c.code, c.name, a.name, labels(e) as entity_labels, count(e) as entity_count
        ORDER BY c.code
        """,
        
        "8. Clean up (if needed)": """
        // Remove all CurriculumLink nodes and relationships
        MATCH (a:CurriculumLink)
        DETACH DELETE a
        """,
        
        "9. Debug: Documents vs CurriculumLinks": """
        // Count total documents
        MATCH (d:Document)
        WITH count(d) as total_docs
        
        // Count documents with course codes
        MATCH (d:Document)
        WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        WITH total_docs, count(d) as docs_with_codes
        
        // Count CurriculumLink nodes
        MATCH (cl:CurriculumLink)
        WITH total_docs, docs_with_codes, count(cl) as curriculum_links
        
        RETURN total_docs, docs_with_codes, curriculum_links,
               (docs_with_codes - curriculum_links) as missing_links
        """,
        
        "10. Debug: Documents without course codes": """
        // Find documents that don't have course codes in filename
        MATCH (d:Document)
        WHERE NOT d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        RETURN d.fileName as filename, d.schema as schema
        ORDER BY d.fileName
        """,
        
        "11. Debug: Documents with invalid course codes": """
        // Find documents with course codes that don't exist in framework
        MATCH (d:Document)
        WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        WITH d, 
             [x IN split(d.fileName, '[') WHERE x CONTAINS ']'][0] as bracket_content,
             d.fileName as filename
        WITH d, filename,
             [x IN split(bracket_content, ']')][0] as course_code
        WHERE course_code =~ '[A-Z]{3}\\d{3,4}'
        
        // Check if course exists in framework
        OPTIONAL MATCH (c:Course {code: course_code})
        WHERE NOT c:__Entity__
        
        WITH d, filename, course_code, c
        WHERE c IS NULL
        RETURN filename, course_code as invalid_code
        ORDER BY course_code
        """,
        
        "12. Debug: Documents without entities": """
        // Find documents that have valid course codes but no extracted entities
        MATCH (d:Document)
        WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        WITH d, 
             [x IN split(d.fileName, '[') WHERE x CONTAINS ']'][0] as bracket_content,
             d.fileName as filename
        WITH d, filename,
             [x IN split(bracket_content, ']')][0] as course_code
        WHERE course_code =~ '[A-Z]{3}\\d{3,4}'
        
        // Check if course exists in framework
        MATCH (c:Course {code: course_code})
        WHERE NOT c:__Entity__
        
        // Check if document has entities
        OPTIONAL MATCH (d)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
        WITH d, filename, course_code, count(e) as entity_count
        WHERE entity_count = 0
        
        RETURN filename, course_code, entity_count
        ORDER BY course_code
        """,
        
        "13. Debug: Already linked documents": """
        // Find documents that are already linked via CurriculumLink
        MATCH (d:Document)
        WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        
        MATCH (d)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
        MATCH (cl:CurriculumLink)-[:HAVE_TO]->(e)
        MATCH (c:Course)-[:POINT_TO]->(cl)
        
        RETURN DISTINCT d.fileName as filename, 
               c.code as linked_course,
               cl.name as curriculum_link,
               count(e) as linked_entities
        ORDER BY c.code
        """
    }
    
    print("Sample Cypher Queries for Manual Testing:")
    print("=" * 60)
    
    for title, query in queries.items():
        print(f"\n{title}")
        print("-" * len(title))
        print(query.strip())
        print()

def test_regex_patterns():
    """Test regex patterns for course code extraction"""
    
    test_filenames = [
        "[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows",
        "[MAT101] Đại số tuyến tính",
        "[COS135] Nhập môn cơ sở dữ liệu",
        "[CMP1074] Cơ sở lập trình",
        "[POS104] Triết học Mác - Lênin",
        "No_brackets_here.pdf",
        "[INVALID] Invalid code",
        "Multiple [CMP170] and [MAT101] codes.pdf",
        "[CMP170]",
        "Prefix [CMP170] Suffix text"
    ]
    
    print("Testing Course Code Extraction:")
    print("=" * 50)
    
    pattern = r'\[([A-Z]{3}\d{3,4})\]'
    
    for filename in test_filenames:
        match = re.search(pattern, filename)
        if match:
            course_code = match.group(1)
            print(f"✅ '{filename[:50]}...' → '{course_code}'")
        else:
            print(f"❌ '{filename[:50]}...' → No match")

def main():
    """Run all utilities"""
    print("Curriculum Entity Linker - Query Utilities")
    print("=" * 60)
    
    print("\n1. Testing Regex Patterns:")
    test_regex_patterns()
    
    print("\n\n2. Preview Curriculum Data:")
    preview_curriculum_data()
    
    print("\n\n3. Sample Cypher Queries:")
    generate_sample_cypher_queries()

if __name__ == "__main__":
    main()
