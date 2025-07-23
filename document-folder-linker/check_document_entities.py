#!/usr/bin/env python3

from data_analyzer import DataAnalyzer

def check_document_entities():
    analyzer = DataAnalyzer()
    try:
        with analyzer.driver.session() as session:
            print("=== DOCUMENT ENTITY ANALYSIS: ===")
            
            # Get all documents with their folder_name
            query_docs = '''
            MATCH (d:Document)
            RETURN d.fileName, d.folder_name, d.course_code, d.status
            ORDER BY d.folder_name
            '''
            result = session.run(query_docs)
            docs = list(result)
            
            for doc in docs:
                file_name = doc['d.fileName']
                folder_name = doc['d.folder_name'] 
                course_code = doc['d.course_code']
                status = doc['d.status']
                
                print(f"\n📄 Document: {file_name}")
                print(f"   folder_name: '{folder_name}'")
                print(f"   course_code: '{course_code}'")  
                print(f"   status: '{status}'")
                
                # Check entities from this document (using correct relationship)
                query_entities = '''
                MATCH (e)-[:PART_OF]->(d:Document)
                WHERE d.fileName = $fileName
                RETURN count(e) as entity_count, collect(DISTINCT labels(e)[0])[0..5] as entity_types
                '''
                result_entities = session.run(query_entities, fileName=file_name).single()
                entity_count = result_entities['entity_count']
                entity_types = result_entities['entity_types']
                
                print(f"   📊 Entities: {entity_count}")
                if entity_count > 0:
                    print(f"   🏷️  Types: {entity_types}")
                else:
                    print(f"   ❌ No entities found!")
                
                # Check if folder exists for this document
                query_folder = '''
                MATCH (f)
                WHERE f.name = $folder_name AND f.course_code = $course_code
                RETURN f, labels(f) as labels
                '''
                result_folder = session.run(query_folder, 
                                          folder_name=folder_name, 
                                          course_code=course_code).single()
                
                if result_folder:
                    folder_labels = result_folder['labels']
                    print(f"   📁 Folder exists: {folder_labels}")
                    
                    # Check relationships from this folder
                    query_folder_rels = '''
                    MATCH (f)-[:HAVE]->(e)
                    WHERE f.name = $folder_name AND f.course_code = $course_code
                    RETURN count(e) as rel_count
                    '''
                    result_rels = session.run(query_folder_rels,
                                            folder_name=folder_name,
                                            course_code=course_code).single()
                    rel_count = result_rels['rel_count']
                    print(f"   🔗 HAVE relationships: {rel_count}")
                    
                    if entity_count > 0 and rel_count == 0:
                        print(f"   ⚠️  MISMATCH: Has entities but no folder relationships!")
                    elif entity_count == 0 and rel_count == 0:
                        print(f"   ℹ️  No entities = no relationships (expected)")
                    else:
                        print(f"   ✅ Entities and relationships match")
                        
                else:
                    print(f"   ❌ No matching folder found!")
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    check_document_entities()
