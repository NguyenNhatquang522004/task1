#!/usr/bin/env python3
"""
Debug script to check entity structure in Neo4j database
"""

from curriculum_linker import CurriculumEntityLinker
import os
from dotenv import load_dotenv

load_dotenv()

def debug_entity_structure():
    """Debug entity structure and relationships"""
    
    uri = os.getenv('NEO4J_URI', 'neo4j+s://013fb011.databases.neo4j.io')
    username = os.getenv('NEO4J_USERNAME', 'neo4j') 
    password = os.getenv('NEO4J_PASSWORD', 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')

    linker = CurriculumEntityLinker(uri, username, password, database)

    try:
        # Check if entities exist at all
        print("🔍 Checking entity structure...")
        
        # 1. Check for any __Entity__ nodes
        query1 = """
        MATCH (e:__Entity__)
        RETURN count(e) as total_entities, 
               collect(DISTINCT labels(e)) as entity_labels,
               collect(DISTINCT e.id)[0..10] as sample_ids
        """
        
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query1)
            record = result.single()
            if record:
                print(f"Total __Entity__ nodes: {record['total_entities']}")
                print(f"Entity labels: {record['entity_labels']}")
                print(f"Sample entity IDs: {record['sample_ids']}")
            else:
                print("❌ No __Entity__ nodes found")
        
        # 2. Check for HAS_ENTITY relationships
        query2 = """
        MATCH (d:Document)-[r:HAS_ENTITY]->(e)
        RETURN count(r) as total_has_entity_rels,
               count(DISTINCT d) as docs_with_entities,
               collect(DISTINCT labels(e)) as target_labels
        """
        
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query2)
            record = result.single()
            if record:
                print(f"\nHAS_ENTITY relationships: {record['total_has_entity_rels']}")
                print(f"Documents with entities: {record['docs_with_entities']}")
                print(f"Target labels: {record['target_labels']}")
            else:
                print("❌ No HAS_ENTITY relationships found")
        
        # 3. Check all relationship types from Documents
        query3 = """
        MATCH (d:Document)-[r]->(n)
        RETURN type(r) as relationship_type, 
               count(r) as count,
               collect(DISTINCT labels(n)) as target_labels
        ORDER BY count DESC
        """
        
        print(f"\n📊 All relationships from Document nodes:")
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query3)
            for record in result:
                print(f"  {record['relationship_type']}: {record['count']} -> {record['target_labels']}")
        
        # 4. Check specific document structure
        docs = linker.get_documents_with_course_codes()
        if docs:
            test_doc = docs[0]
            print(f"\n🔍 Analyzing document: {test_doc['filename']}")
            
            query4 = """
            MATCH (d:Document)-[r]->(n)
            WHERE ID(d) = $doc_id
            RETURN type(r) as rel_type, 
                   count(n) as target_count,
                   collect(DISTINCT labels(n)) as target_labels,
                   collect(n.id)[0..3] as sample_target_ids
            ORDER BY target_count DESC
            """
            
            with linker.driver.session(database=linker.database) as session:
                result = session.run(query4, doc_id=test_doc['doc_id'])
                for record in result:
                    print(f"  {record['rel_type']}: {record['target_count']} -> {record['target_labels']}")
                    if record['sample_target_ids']:
                        print(f"    Sample IDs: {record['sample_target_ids']}")
        
        # 5. Look for alternative relationship patterns
        print(f"\n🔍 Looking for alternative patterns...")
        
        # Check for PART_OF relationships (common in LLM Graph Builder)
        query5 = """
        MATCH (d:Document)<-[:PART_OF]-(e)
        WHERE d.fileName =~ '.*\\[CMP.*\\].*'
        RETURN d.fileName as filename, 
               count(e) as entities_part_of,
               collect(DISTINCT labels(e)) as entity_labels,
               collect(e.id)[0..5] as sample_ids
        """
        
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query5)
            for record in result:
                print(f"Document: {record['filename']}")
                print(f"  Entities with PART_OF: {record['entities_part_of']}")
                print(f"  Labels: {record['entity_labels']}")
                print(f"  Sample IDs: {record['sample_ids']}")
                
    finally:
        linker.close()

if __name__ == "__main__":
    debug_entity_structure()
