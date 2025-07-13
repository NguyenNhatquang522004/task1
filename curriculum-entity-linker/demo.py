#!/usr/bin/env python3
"""
Quick demo script for Curriculum Entity Linker
Chạy script này để test functionality mà không cần Neo4j connection thực tế
"""

import re
import os

def demo_course_code_extraction():
    """Demo việc extract course code"""
    sample_filenames = [
        "[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows.pdf",
        "[MAT101] Đại số tuyến tính - Semester 1.docx", 
        "[COS135] Nhập môn cơ sở dữ liệu.pdf",
        "[CMP1074] Cơ sở lập trình - Java.pdf",
        "[POS104] Triết học Mác - Lênin.pdf",
        "Document without code.pdf",
        "[INVALID123] Wrong format.pdf"
    ]
    
    print("🔍 DEMO: Course Code Extraction")
    print("=" * 50)
    
    pattern = r'\[([A-Z]{3}\d{3,4})\]'
    
    for filename in sample_filenames:
        match = re.search(pattern, filename)
        if match:
            course_code = match.group(1)
            print(f"✅ {filename}")
            print(f"   → Course Code: {course_code}")
        else:
            print(f"❌ {filename}")
            print(f"   → No valid course code found")
        print()

def demo_node_naming():
    """Demo việc tạo tên cho intermediate nodes"""
    test_cases = [
        ("giáo_trình", "[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows"),
        ("curriculum", "[MAT101] Đại số tuyến tính"),
        (None, "[COS135] Nhập môn cơ sở dữ liệu"),
        ("syllabus_v2", "[CMP1074] Cơ sở lập trình"),
    ]
    
    print("🏷️  DEMO: Intermediate Node Naming")
    print("=" * 50)
    
    for schema, filename in test_cases:
        # Extract course code
        course_code_match = re.search(r'\[([A-Z]{3}\d{3,4})\]', filename)
        course_code = course_code_match.group(1) if course_code_match else "UNKNOWN"
        
        # Create node name
        if schema:
            node_name = f"{schema}_{filename}"
        else:
            node_name = f"curriculum_{filename}"
        
        # Clean up name
        node_name = re.sub(r'[^\w\s-]', '', node_name)
        node_name = re.sub(r'\s+', '_', node_name)
        
        print(f"Schema: {schema or 'None'}")
        print(f"Filename: {filename}")
        print(f"Course Code: {course_code}")
        print(f"Node Name: {node_name}")
        print("-" * 30)

def demo_curriculum_preview():
    """Demo preview curriculum data"""
    cql_file_path = os.path.join(os.path.dirname(__file__), '..', 'curriculum-syllabus-example.cql')
    
    print("📚 DEMO: Curriculum Framework Preview")
    print("=" * 50)
    
    if not os.path.exists(cql_file_path):
        print("❌ curriculum-syllabus-example.cql not found")
        print(f"Expected path: {cql_file_path}")
        return
    
    try:
        with open(cql_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Count different elements
        course_merges = content.count('MERGE (c:Course')
        major_merges = content.count('MERGE (m:Major')
        block_merges = content.count('KnowledgeBlock')
        
        print(f"📊 Statistics:")
        print(f"   Courses: {course_merges}")
        print(f"   Majors: {major_merges}")
        print(f"   Knowledge Blocks: {block_merges}")
        print()
        
        # Extract sample courses
        course_pattern = r"code: '([^']+)'.*?name: '([^']+)'"
        matches = re.findall(course_pattern, content)
        
        print("📋 Sample Courses:")
        for i, (code, name) in enumerate(matches[:10]):
            print(f"   {i+1:2d}. {code} - {name}")
        
        if len(matches) > 10:
            print(f"   ... and {len(matches) - 10} more courses")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def demo_cypher_queries():
    """Demo the Cypher queries that will be used"""
    queries = {
        "Find Documents with Course Codes": """
MATCH (d:Document)
WHERE d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
RETURN d.fileName, d.schema, 
       [x IN split(d.fileName, '[') WHERE x CONTAINS ']'][0] as bracket_part
""",
        
        "Find Course Framework": """
MATCH (c:Course {code: 'CMP170'})
WHERE NOT c:__Entity__
RETURN c.code, c.name, ID(c)
""",
        
        "Create Intermediate Node": """
MERGE (a:CurriculumLink {name: 'giáo_trình_CMP170_...'})
ON CREATE SET a.created_at = datetime()
RETURN ID(a), a.name
""",
        
        "Link Everything": """
// Course → CurriculumLink
MATCH (c:Course {code: 'CMP170'}), (a:CurriculumLink)
WHERE a.name CONTAINS 'CMP170'
MERGE (c)-[:POINT_TO]->(a)

// CurriculumLink → Entities  
MATCH (d:Document)-[:HAS_ENTITY]->(e)
WHERE d.fileName CONTAINS '[CMP170]'
MATCH (a:CurriculumLink) WHERE a.name CONTAINS 'CMP170'
MERGE (a)-[:HAVE_TO]->(e)
"""
    }
    
    print("💻 DEMO: Sample Cypher Queries")
    print("=" * 50)
    
    for title, query in queries.items():
        print(f"🔸 {title}:")
        print(query.strip())
        print("-" * 30)

def main():
    """Run all demos"""
    print("🚀 Curriculum Entity Linker - DEMO")
    print("=" * 60)
    print()
    
    demo_course_code_extraction()
    print("\n")
    
    demo_node_naming() 
    print("\n")
    
    demo_curriculum_preview()
    print("\n")
    
    demo_cypher_queries()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("\n📋 Next Steps:")
    print("1. Install dependencies: python setup.py")
    print("2. Configure .env file with Neo4j credentials")
    print("3. Load curriculum framework into Neo4j")
    print("4. Run: python curriculum_linker.py")

if __name__ == "__main__":
    main()
