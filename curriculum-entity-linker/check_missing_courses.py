#!/usr/bin/env python3
"""
Kiểm tra các course codes bị thiếu CurriculumLink nodes
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_missing_courses():
    # Database connection
    uri = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "12345678")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    print("🔍 KIỂM TRA CÁC COURSE CODES BỊ THIẾU:")
    print("="*60)
    
    missing_codes = ['CMP175', 'CMP376', 'CMP187', 'COS340']
    
    try:
        with driver.session() as session:
            for code in missing_codes:
                print(f"\n🎯 Checking {code}:")
                print("-" * 30)
                
                # 1. Kiểm tra Course node
                result = session.run("""
                    MATCH (c:Course {code: $code}) 
                    RETURN c.code as code, c.name as name, ID(c) as course_id
                """, code=code)
                course_record = result.single()
                
                if course_record:
                    print(f"✅ Course found: {code} - {course_record['name']}")
                    course_id = course_record['course_id']
                else:
                    print(f"❌ Course NOT found: {code}")
                    continue
                
                # 2. Kiểm tra Document
                result = session.run("""
                    MATCH (d:Document) 
                    WHERE d.fileName CONTAINS $code 
                    RETURN d.fileName as filename, ID(d) as doc_id
                """, code=code)
                docs = list(result)
                
                print(f"📄 Documents: {len(docs)} found")
                for doc in docs:
                    print(f"   - {doc['filename']} (ID: {doc['doc_id']})")
                
                if not docs:
                    print("   ⚠️  No documents found for this course code")
                    continue
                
                # 3. Kiểm tra CurriculumLink
                result = session.run("""
                    MATCH (cl:CurriculumLink)-[:POINT_TO]->(c:Course {code: $code}) 
                    RETURN cl.name as name, ID(cl) as link_id
                """, code=code)
                links = list(result)
                
                print(f"🔗 CurriculumLinks: {len(links)} found")
                for link in links:
                    print(f"   - {link['name']} (ID: {link['link_id']})")
                
                # 4. Kiểm tra entities từ document
                for doc in docs:
                    doc_id = doc['doc_id']
                    result = session.run("""
                        MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
                        WHERE ID(d) = $doc_id
                        RETURN count(e) as entity_count
                    """, doc_id=doc_id)
                    entity_record = result.single()
                    
                    if entity_record:
                        print(f"   🎯 Entities in {doc['filename']}: {entity_record['entity_count']}")
                
                # 5. Kiểm tra linking status
                for doc in docs:
                    doc_id = doc['doc_id']
                    result = session.run("""
                        MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)<-[:HAVE_TO]-(cl:CurriculumLink)-[:POINT_TO]->(c:Course)
                        WHERE ID(d) = $doc_id
                        RETURN count(cl) as link_count, c.code as linked_course_code
                    """, doc_id=doc_id)
                    link_record = result.single()
                    
                    if link_record and link_record['link_count'] > 0:
                        print(f"   ✅ Document {doc['filename']} is linked to course {link_record['linked_course_code']}")
                    else:
                        print(f"   ❌ Document {doc['filename']} is NOT linked to any course")
                
                # 6. Kiểm tra lý do tại sao không link được
                print(f"\n🔧 Debugging linking process for {code}:")
                
                # Kiểm tra có curriculum entities không
                result = session.run("""
                    MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
                    WHERE d.fileName CONTAINS $code
                    WITH e
                    MATCH (c:Course {code: $code})-[:HAS_TOPIC]->(t:Topic)-[:HAS_CONCEPT]->(concept:Concept)
                    WHERE toLower(e.id) CONTAINS toLower(concept.name) 
                       OR toLower(concept.name) CONTAINS toLower(e.id)
                       OR toLower(e.id) CONTAINS toLower(concept.id)
                    RETURN count(DISTINCT e) as matching_entities, 
                           count(DISTINCT concept) as matching_concepts
                """, code=code)
                match_record = result.single()
                
                if match_record:
                    print(f"   🎯 Matching entities: {match_record['matching_entities']}")
                    print(f"   🎯 Matching concepts: {match_record['matching_concepts']}")
                    
                    if match_record['matching_entities'] == 0:
                        print("   ⚠️  No entities match curriculum concepts!")
                        
                        # Show sample entities and concepts for comparison
                        result = session.run("""
                            MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)-[:HAS_ENTITY]->(e:__Entity__)
                            WHERE d.fileName CONTAINS $code
                            RETURN e.id as entity_id LIMIT 5
                        """, code=code)
                        entities = list(result)
                        
                        result = session.run("""
                            MATCH (c:Course {code: $code})-[:HAS_TOPIC]->(t:Topic)-[:HAS_CONCEPT]->(concept:Concept)
                            RETURN concept.name as concept_name, concept.id as concept_id LIMIT 5
                        """, code=code)
                        concepts = list(result)
                        
                        print("   📋 Sample entities:")
                        for entity in entities:
                            print(f"      - {entity['entity_id']}")
                        
                        print("   📋 Sample concepts:")
                        for concept in concepts:
                            print(f"      - {concept['concept_name']} ({concept['concept_id']})")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    check_missing_courses()
