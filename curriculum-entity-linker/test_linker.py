#!/usr/bin/env python3
"""
Test script for Curriculum Entity Linker
"""

import os
import sys
import re

def test_course_code_extraction():
    """Test course code extraction logic"""
    test_cases = [
        "[CMP170] Đề cương HP Lap Trinh Tren Moi Truong Windows",
        "[MAT101] Đại số tuyến tính", 
        "[COS135] Nhập môn cơ sở dữ liệu",
        "[CMP1074] Cơ sở lập trình",
        "No brackets here",
        "[INVALID] Invalid code",
        "[CMP170]",
        "Multiple [CMP170] and [MAT101] codes"
    ]
    
    pattern = r'\[([A-Z]{3}\d{3,4})\]'
    
    print("Testing course code extraction:")
    print("=" * 50)
    
    for test_case in test_cases:
        match = re.search(pattern, test_case)
        if match:
            course_code = match.group(1)
            print(f"✅ '{test_case}' → '{course_code}'")
        else:
            print(f"❌ '{test_case}' → No match")
    
    print("\n")

def preview_cql_file():
    """Preview curriculum CQL file structure"""
    cql_file_path = os.path.join(os.path.dirname(__file__), '..', 'curriculum-syllabus-example.cql')
    
    if not os.path.exists(cql_file_path):
        print(f"❌ CQL file not found: {cql_file_path}")
        return
    
    print("Preview of curriculum CQL file:")
    print("=" * 50)
    
    try:
        with open(cql_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Count different types of statements
        course_merges = [line for line in lines if 'MERGE (c:Course' in line]
        major_merges = [line for line in lines if 'MERGE (m:Major' in line]
        block_merges = [line for line in lines if 'MERGE (b' in line and 'KnowledgeBlock' in line]
        
        print(f"Total lines: {len(lines)}")
        print(f"Course MERGE statements: {len(course_merges)}")
        print(f"Major MERGE statements: {len(major_merges)}")
        print(f"KnowledgeBlock MERGE statements: {len(block_merges)}")
        
        print("\nSample Course nodes:")
        for i, line in enumerate(course_merges[:5]):
            if 'code:' in line:
                # Extract course info
                match = re.search(r"code: '([^']+)'.*name: '([^']+)'", line)
                if match:
                    code, name = match.groups()
                    print(f"  - {code}: {name}")
        
        print("\n")
        
    except Exception as e:
        print(f"❌ Error reading CQL file: {e}")

def check_neo4j_connection():
    """Check if Neo4j connection can be established"""
    try:
        from neo4j import GraphDatabase
        from dotenv import load_dotenv
        
        load_dotenv()
        
        uri = os.getenv('NEO4J_URI', 'neo4j://localhost:7687')
        username = os.getenv('NEO4J_USERNAME', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'password')
        
        print("Testing Neo4j connection:")
        print("=" * 50)
        print(f"URI: {uri}")
        print(f"Username: {username}")
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record['test'] == 1:
                print("✅ Neo4j connection successful!")
            else:
                print("❌ Neo4j connection failed!")
        
        driver.close()
        
    except ImportError:
        print("❌ Neo4j driver not installed. Install with: pip install neo4j")
    except Exception as e:
        print(f"❌ Neo4j connection error: {e}")
    
    print("\n")

def preview_sample_queries():
    """Show sample queries that will be used"""
    queries = {
        "Find Documents with Course Codes": """
        MATCH (d:Document)
        WHERE d.fileName IS NOT NULL AND d.fileName =~ '.*\\[([A-Z]{3}\\d{3,4})\\].*'
        RETURN d.fileName as filename, d.schema as schema
        LIMIT 10
        """,
        
        "Find Course Framework Nodes": """
        MATCH (c:Course)
        WHERE NOT c:__Entity__
        RETURN c.code as code, c.name as name
        LIMIT 10
        """,
        
        "Check Existing Extracted Entities": """
        MATCH (d:Document)-[:HAS_ENTITY]->(e)
        RETURN d.fileName, labels(e) as entity_labels, e.id
        LIMIT 10
        """
    }
    
    print("Sample queries to be used:")
    print("=" * 50)
    
    for title, query in queries.items():
        print(f"\n{title}:")
        print("-" * len(title))
        print(query.strip())

def main():
    """Run all tests"""
    print("Curriculum Entity Linker - Test Suite")
    print("=" * 60)
    print()
    
    test_course_code_extraction()
    preview_cql_file()
    check_neo4j_connection()
    preview_sample_queries()
    
    print("Test suite completed!")

if __name__ == "__main__":
    main()
