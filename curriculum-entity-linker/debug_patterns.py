#!/usr/bin/env python3
"""
Debug script to find the actual relationship pattern for entities
"""

from curriculum_linker import CurriculumEntityLinker
import os
from dotenv import load_dotenv

load_dotenv()

def find_entity_relationship_pattern():
    """Find how entities are actually connected in the graph"""
    
    uri = os.getenv('NEO4J_URI', 'neo4j+s://013fb011.databases.neo4j.io')
    username = os.getenv('NEO4J_USERNAME', 'neo4j') 
    password = os.getenv('NEO4J_PASSWORD', 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')

    linker = CurriculumEntityLinker(uri, username, password, database)

    try:
        print("🔍 Finding actual entity relationship patterns...")
        
        # 1. Check all relationships FROM entities
        query1 = """
        MATCH (e:__Entity__)-[r]->(n)
        RETURN type(r) as relationship_type, 
               count(r) as count,
               collect(DISTINCT labels(n)) as target_labels
        ORDER BY count DESC
        LIMIT 10
        """
        
        print("\n📊 Relationships FROM entities:")
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query1)
            for record in result:
                print(f"  {record['relationship_type']}: {record['count']} -> {record['target_labels']}")
        
        # 2. Check all relationships TO entities
        query2 = """
        MATCH (n)-[r]->(e:__Entity__)
        RETURN type(r) as relationship_type, 
               count(r) as count,
               collect(DISTINCT labels(n)) as source_labels
        ORDER BY count DESC
        LIMIT 10
        """
        
        print("\n📊 Relationships TO entities:")
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query2)
            for record in result:
                print(f"  {record['relationship_type']}: {record['count']} <- {record['source_labels']}")
        
        # 3. Find entities related to the specific chunk
        chunk_id = '4a1621c605558c5ee06f59ebfe0f86b6745c3ec9'
        query3 = """
        MATCH (chunk:Chunk {id: $chunk_id})
        MATCH (chunk)-[r1]-(n1)-[r2]-(e:__Entity__)
        RETURN type(r1) as rel1_type, labels(n1) as intermediate_labels, 
               type(r2) as rel2_type, count(e) as entity_count,
               collect(e.id)[0..5] as sample_entity_ids
        ORDER BY entity_count DESC
        """
        
        print(f"\n🔍 Entities connected to chunk {chunk_id} (via intermediate nodes):")
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query3, chunk_id=chunk_id)
            for record in result:
                print(f"  Chunk-[{record['rel1_type']}]->{record['intermediate_labels']}-[{record['rel2_type']}]->Entity: {record['entity_count']} entities")
                if record['sample_entity_ids']:
                    print(f"    Sample IDs: {record['sample_entity_ids']}")
        
        # 4. Check direct connections to chunk
        query4 = """
        MATCH (chunk:Chunk {id: $chunk_id})-[r]-(e:__Entity__)
        RETURN type(r) as relationship_type, count(e) as entity_count,
               collect(e.id)[0..5] as sample_entity_ids
        """
        
        print(f"\n🔍 Direct entity connections to chunk {chunk_id}:")
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query4, chunk_id=chunk_id)
            for record in result:
                print(f"  {record['relationship_type']}: {record['entity_count']} entities")
                if record['sample_entity_ids']:
                    print(f"    Sample IDs: {record['sample_entity_ids']}")
        
        # 5. Check how entities are connected to documents in general
        query5 = """
        MATCH (d:Document)
        WHERE d.fileName CONTAINS 'CMP3025'
        MATCH (d)-[r1*1..3]-(e:__Entity__)
        RETURN d.fileName as filename, 
               count(DISTINCT e) as entity_count,
               collect(DISTINCT e.id)[0..10] as sample_entity_ids
        """
        
        print(f"\n🔍 Entities connected to CMP3025 document (any path):")
        with linker.driver.session(database=linker.database) as session:
            result = session.run(query5)
            for record in result:
                print(f"  Document: {record['filename']}")
                print(f"  Connected entities: {record['entity_count']}")
                if record['sample_entity_ids']:
                    print(f"  Sample IDs: {record['sample_entity_ids']}")
                    
    finally:
        linker.close()

if __name__ == "__main__":
    find_entity_relationship_pattern()
