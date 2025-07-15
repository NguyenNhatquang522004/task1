#!/usr/bin/env python3
"""
Debug script to check why HAVE_TO relationships are not being created
"""

from curriculum_linker import CurriculumEntityLinker
import os
from dotenv import load_dotenv

load_dotenv()

def debug_have_to_creation():
    """Debug why HAVE_TO relationships are not being created"""
    
    uri = os.getenv('NEO4J_URI', 'neo4j+s://013fb011.databases.neo4j.io')
    username = os.getenv('NEO4J_USERNAME', 'neo4j') 
    password = os.getenv('NEO4J_PASSWORD', 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')

    linker = CurriculumEntityLinker(uri, username, password, database)

    try:
        # Get the document we just processed
        docs = linker.get_documents_with_course_codes()
        if docs:
            test_doc = docs[0]
            doc_id = test_doc['doc_id']
            print(f"Testing document: {test_doc}")
            
            # Step 1: Check if document has chunk relationships
            query1 = """
            MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)
            WHERE ID(d) = $doc_id
            RETURN count(chunk) as chunk_count, collect(chunk.id)[0..3] as sample_chunk_ids
            """
            
            with linker.driver.session(database=linker.database) as session:
                result = session.run(query1, doc_id=doc_id)
                record = result.single()
                if record:
                    print(f"Step 1 - Chunks connected to document: {record['chunk_count']}")
                    print(f"Sample chunk IDs: {record['sample_chunk_ids']}")
                else:
                    print("❌ No chunks found connected to document!")
                    
            # Step 2: Check if chunks have PART_OF relationships to entities
            query2 = """
            MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)<-[:PART_OF]-(e:__Entity__)
            WHERE ID(d) = $doc_id
            RETURN count(e) as entity_count, 
                   collect(DISTINCT labels(e)) as entity_labels,
                   collect(e.id)[0..5] as sample_entity_ids
            """
            
            with linker.driver.session(database=linker.database) as session:
                result = session.run(query2, doc_id=doc_id)
                record = result.single()
                if record:
                    print(f"Step 2 - Entities connected via PART_OF: {record['entity_count']}")
                    print(f"Entity labels: {record['entity_labels']}")
                    print(f"Sample entity IDs: {record['sample_entity_ids']}")
                    
                    if record['entity_count'] == 0:
                        print("❌ NO ENTITIES found via PART_OF relationship!")
                        
                        # Check alternative patterns
                        alt_query = """
                        MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)
                        WHERE ID(d) = $doc_id
                        WITH chunk
                        MATCH (chunk)<-[r]-(e)
                        WHERE e:__Entity__
                        RETURN type(r) as rel_type, count(e) as entity_count,
                               collect(DISTINCT labels(e)) as entity_labels
                        """
                        
                        alt_result = session.run(alt_query, doc_id=doc_id)
                        for alt_record in alt_result:
                            print(f"Alternative: {alt_record['rel_type']} -> {alt_record['entity_count']} entities")
                            print(f"Labels: {alt_record['entity_labels']}")
                else:
                    print("❌ Query returned no results")
                    
            # Step 3: Check what CurriculumLink was created
            query3 = """
            MATCH (a:CurriculumLink)
            WHERE a.name CONTAINS 'CMP3025'
            RETURN ID(a) as link_id, a.name as link_name
            """
            
            with linker.driver.session(database=linker.database) as session:
                result = session.run(query3)
                record = result.single()
                if record:
                    print(f"Step 3 - CurriculumLink found: ID={record['link_id']}, Name={record['link_name']}")
                    
                    # Step 4: Test the exact query that should create HAVE_TO relationships
                    test_query = """
                    MATCH (d:Document)-[:FIRST_CHUNK]->(chunk:Chunk)<-[:PART_OF]-(e:__Entity__)
                    WHERE ID(d) = $doc_id
                    WITH collect(DISTINCT ID(e)) as entity_ids
                    RETURN entity_ids, size(entity_ids) as entity_count
                    """
                    
                    test_result = session.run(test_query, doc_id=doc_id)
                    test_record = test_result.single()
                    if test_record:
                        print(f"Step 4 - Entity IDs collected: {test_record['entity_count']}")
                        if test_record['entity_count'] > 0:
                            print(f"Sample entity IDs: {test_record['entity_ids'][:5]}")
                        else:
                            print("❌ No entity IDs collected by the query!")
                else:
                    print("❌ No CurriculumLink found for CMP3025")
                    
    finally:
        linker.close()

if __name__ == "__main__":
    debug_have_to_creation()
