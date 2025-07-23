#!/usr/bin/env python3

from data_analyzer import DataAnalyzer

def simple_entity_check():
    analyzer = DataAnalyzer()
    try:
        with analyzer.driver.session() as session:
            print("=== SIMPLE DOCUMENT-ENTITY CHECK: ===")
            
            # Check document status
            query = '''
            MATCH (d:Document)
            RETURN d.fileName, d.folder_name, d.status
            ORDER BY d.folder_name
            '''
            result = session.run(query)
            
            for record in result:
                file_name = record['d.fileName']
                folder_name = record['d.folder_name']
                status = record['d.status']
                
                print(f"\n📄 {file_name}")
                print(f"   Folder: '{folder_name}'")
                print(f"   Status: '{status}'")
                
                # Count entities from this document (if any)
                query2 = '''
                MATCH (e)-[:FROM]->(d:Document)
                WHERE d.fileName = $fileName
                RETURN count(e) as count
                '''
                result2 = session.run(query2, fileName=file_name).single()
                entity_count = result2['count']
                print(f"   Entities: {entity_count}")
                
                if status != "Completed":
                    print(f"   ⚠️  Document not completed - no entities expected")
                elif entity_count == 0:
                    print(f"   ❌ No entities despite completed status")
                else:
                    print(f"   ✅ Has entities")
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    simple_entity_check()
