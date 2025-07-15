#!/usr/bin/env python3
"""
Debug script to check document entity relationships
"""

from curriculum_linker import CurriculumEntityLinker
import os
from dotenv import load_dotenv

load_dotenv()

def debug_document_entities():
    """Debug document-entity relationships"""
    
    uri = os.getenv('NEO4J_URI', 'neo4j+s://013fb011.databases.neo4j.io')
    username = os.getenv('NEO4J_USERNAME', 'neo4j') 
    password = os.getenv('NEO4J_PASSWORD', 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')

    linker = CurriculumEntityLinker(uri, username, password, database)

    try:
        # Get documents with course codes
        docs = linker.get_documents_with_course_codes()
        print(f"Found {len(docs)} documents with course codes")
        
        if docs:
            test_doc = docs[0]
            print(f"\nTesting document: {test_doc}")
            
            # Check if document has entities
            query = """
            MATCH (d:Document)-[:HAS_ENTITY]->(e)
            WHERE ID(d) = $doc_id
            RETURN ID(d) as doc_id, d.fileName as filename, 
                   count(e) as entity_count, 
                   collect(DISTINCT labels(e)) as entity_labels,
                   collect(DISTINCT e.id)[0..5] as sample_entity_ids
            """
            
            with linker.driver.session(database=linker.database) as session:
                result = session.run(query, doc_id=test_doc['doc_id'])
                record = result.single()
                
                if record:
                    print(f"Document has {record['entity_count']} entities")
                    print(f"Entity labels: {record['entity_labels']}")
                    print(f"Sample entity IDs: {record['sample_entity_ids']}")
                    
                    if record['entity_count'] == 0:
                        print("❌ NO ENTITIES FOUND! This is the problem.")
                        
                        # Check if document exists at all
                        check_query = """
                        MATCH (d:Document)
                        WHERE ID(d) = $doc_id
                        RETURN d.fileName as filename, d.schema as schema
                        """
                        result2 = session.run(check_query, doc_id=test_doc['doc_id'])
                        record2 = result2.single()
                        if record2:
                            print(f"Document exists: {record2['filename']}")
                        else:
                            print("Document doesn't exist!")
                else:
                    print("❌ No result returned from entity query")
                    
            # Test the create_have_to_relationships query manually
            print("\n🔍 Testing create_have_to_relationships query:")
            test_query = """
            MATCH (d:Document)-[:HAS_ENTITY]->(e)
            WHERE ID(d) = $doc_id
            WITH collect(ID(e)) as entity_ids
            RETURN entity_ids, size(entity_ids) as count
            """
            
            with linker.driver.session(database=linker.database) as session:
                result = session.run(test_query, doc_id=test_doc['doc_id'])
                record = result.single()
                if record:
                    print(f"Entity IDs collected: {record['entity_ids'][:5]}... (showing first 5)")
                    print(f"Total entity count: {record['count']}")
                else:
                    print("❌ No entities collected by the query")
            
        else:
            print("❌ No documents found with course codes")
            
    finally:
        linker.close()

if __name__ == "__main__":
    debug_document_entities()
