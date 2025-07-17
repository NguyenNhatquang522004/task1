#!/usr/bin/env python3
"""
So sánh courses có và không có curriculum framework
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def compare_curriculum_frameworks():
    # Database connection
    uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            print("🔍 SO SÁNH COURSES CÓ VÀ KHÔNG CÓ CURRICULUM FRAMEWORK:")
            print("="*70)
            
            # Courses có curriculum framework
            result = session.run("""
                MATCH (c:Course)-[:HAS_TOPIC]->(t:Topic)
                RETURN DISTINCT c.code as code, c.name as name, count(t) as topic_count
                ORDER BY c.code
            """)
            
            courses_with_curriculum = list(result)
            print(f"✅ COURSES CÓ CURRICULUM FRAMEWORK ({len(courses_with_curriculum)}):")
            for course in courses_with_curriculum:
                print(f"   {course['code']}: {course['name']} - {course['topic_count']} topics")
            
            print()
            
            # Courses không có curriculum framework
            result = session.run("""
                MATCH (c:Course)
                WHERE NOT (c)-[:HAS_TOPIC]->()
                RETURN c.code as code, c.name as name
                ORDER BY c.code
            """)
            
            courses_without_curriculum = list(result)
            print(f"❌ COURSES KHÔNG CÓ CURRICULUM FRAMEWORK ({len(courses_without_curriculum)}):")
            for course in courses_without_curriculum:
                print(f"   {course['code']}: {course['name']}")
            
            print()
            
            # Kiểm tra missing courses
            missing_codes = ['CMP175', 'CMP376', 'CMP187', 'COS340']
            print("🎯 MISSING COURSES TRONG DANH SÁCH:")
            for code in missing_codes:
                found_in_with = any(c['code'] == code for c in courses_with_curriculum)
                found_in_without = any(c['code'] == code for c in courses_without_curriculum)
                
                if found_in_with:
                    print(f"   {code}: ✅ CÓ curriculum framework")
                elif found_in_without:
                    print(f"   {code}: ❌ THIẾU curriculum framework")
                else:
                    print(f"   {code}: ⚠️  KHÔNG TÌM THẤY")
            
            print()
            print("🎯 GIẢI THÍCH:")
            print("Curriculum linker chỉ tạo CurriculumLink khi:")
            print("1. Course có curriculum framework (Topics + Concepts)")
            print("2. Entities từ documents match với Concepts")
            print("3. Nếu Course chỉ có code/name mà không có framework → KHÔNG link được")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    compare_curriculum_frameworks()
