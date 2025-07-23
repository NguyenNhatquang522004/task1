#!/usr/bin/env python3

from data_analyzer import DataAnalyzer

def check_folder_relationships():
    analyzer = DataAnalyzer()
    try:
        with analyzer.driver.session() as session:
            # Check all HAVE relationships
            print("=== HAVE RELATIONSHIPS STATISTICS: ===")
            query = 'MATCH (f)-[:HAVE]->(e) RETURN count(*) as total'
            result = session.run(query).single()
            total = result['total']
            print(f'Total HAVE relationships: {total}')
            
            # Check folder nodes count
            query2 = '''MATCH (f) WHERE f.name IS NOT NULL AND f.course_code = 'CMP177' 
                        RETURN count(*) as folder_count'''
            result2 = session.run(query2).single() 
            folder_count = result2['folder_count']
            print(f'CMP177 folder nodes: {folder_count}')
            
            # Check any HAVE from CMP177 folders
            query3 = '''MATCH (f)-[:HAVE]->(e) WHERE f.course_code = 'CMP177' 
                        RETURN f.name, count(e) as count'''
            result3 = session.run(query3)
            relationships = list(result3)
            print(f'CMP177 folder relationships: {len(relationships)}')
            for record in relationships:
                print(f'  {record["f.name"]}: {record["count"]} entities')
            
            if not relationships:
                print("❌ No HAVE relationships found for CMP177 folders")
                
                # Check if folders exist
                query4 = '''MATCH (f) WHERE f.course_code = 'CMP177' 
                           RETURN f.name, labels(f) as labels'''
                result4 = session.run(query4)
                folders = list(result4)
                print(f"\n📁 CMP177 folders found: {len(folders)}")
                for record in folders:
                    print(f"  - {record['labels']} '{record['f.name']}'")
                
                # Check total HAVE relationships by folder name
                print("\n=== CHECKING HAVE BY FOLDER NAME: ===")
                for folder in folders:
                    folder_name = folder['f.name']
                    query5 = f'''MATCH (f)-[:HAVE]->(e) WHERE f.name = '{folder_name}' 
                                RETURN count(e) as count'''
                    result5 = session.run(query5).single()
                    count = result5['count']
                    print(f"  '{folder_name}': {count} relationships")
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    check_folder_relationships()
