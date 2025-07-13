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
