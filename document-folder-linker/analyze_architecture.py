#!/usr/bin/env python3

from data_analyzer import DataAnalyzer

def analyze_document_chunk_entity_architecture():
    analyzer = DataAnalyzer()
    try:
        with analyzer.driver.session() as session:
            print('=== ARCHITECTURE ANALYSIS: Document -> Chunk -> Entity ===')
            
            # 1. Check Document -> Chunk relationships
            print('\n1. Document -> Chunk relationships:')
            query1 = '''MATCH (d:Document)-[r]->(c:Chunk) 
                        WHERE d.fileName CONTAINS 'beginningflutter'
                        RETURN type(r) as rel_type, count(c) as chunk_count'''
            result1 = session.run(query1)
            for record in result1:
                print(f'   {record["rel_type"]}: {record["chunk_count"]} chunks')
            
            # 2. Check Chunk -> Entity relationships  
            print('\n2. Chunk -> Entity relationships:')
            query2 = '''MATCH (c:Chunk)-[r]->(e)
                        WHERE (c)-[:PART_OF]->(:Document {fileName: '[CMP177] beginningflutter.pdf'})
                            AND NOT e:Document AND NOT e:Chunk
                        RETURN type(r) as rel_type, count(e) as entity_count, 
                               collect(DISTINCT labels(e)[0])[0..3] as entity_types
                        ORDER BY entity_count DESC'''
            result2 = session.run(query2)
            for record in result2:
                print(f'   {record["rel_type"]}: {record["entity_count"]} entities, types: {record["entity_types"]}')
            
            # 3. Check all relationships from chunks
            print('\n3. All relationships from chunks of beginningflutter:')
            query3 = '''MATCH (c:Chunk)-[r]->(target)
                        WHERE (c)-[:PART_OF]->(:Document {fileName: '[CMP177] beginningflutter.pdf'})
                        RETURN type(r) as rel_type, count(target) as target_count,
                               collect(DISTINCT labels(target)[0])[0..3] as target_types
                        ORDER BY target_count DESC'''
            result3 = session.run(query3) 
            for record in result3:
                print(f'   {record["rel_type"]}: {record["target_count"]} targets, types: {record["target_types"]}')
            
            # 4. Complete path analysis: Document -> Chunk -> Entity
            print('\n4. Complete path: Document -> Chunk -> Entity')
            query4 = '''MATCH (d:Document {fileName: '[CMP177] beginningflutter.pdf'})-[r1]->(c:Chunk)-[r2]->(e)
                        WHERE NOT e:Document AND NOT e:Chunk
                        RETURN type(r1) as doc_chunk_rel, type(r2) as chunk_entity_rel, 
                               count(e) as entity_count, collect(DISTINCT labels(e)[0])[0..5] as entity_types
                        ORDER BY entity_count DESC'''
            result4 = session.run(query4)
            for record in result4:
                print(f'   Document -[{record["doc_chunk_rel"]}]-> Chunk -[{record["chunk_entity_rel"]}]-> Entity')
                print(f'     Entities: {record["entity_count"]}, Types: {record["entity_types"]}')
            
            # 5. Check similar for other documents
            print('\n5. Architecture comparison for all documents:')
            query5 = '''MATCH (d:Document)-[r1]->(c:Chunk)-[r2]->(e)
                        WHERE d.folder_name IS NOT NULL AND NOT e:Document AND NOT e:Chunk
                        RETURN d.folder_name, d.fileName, type(r1) as doc_chunk_rel, 
                               type(r2) as chunk_entity_rel, count(e) as entity_count
                        ORDER BY d.folder_name, entity_count DESC'''
            result5 = session.run(query5)
            for record in result5:
                print(f'   📄 {record["d.fileName"]} (folder: {record["d.folder_name"]})')
                print(f'     {record["doc_chunk_rel"]} -> {record["chunk_entity_rel"]}: {record["entity_count"]} entities')
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    analyze_document_chunk_entity_architecture()
