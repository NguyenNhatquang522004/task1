"""
Debug script to check folder name matching issues
"""
from data_analyzer import DataAnalyzer

def debug_folder_matching():
    analyzer = DataAnalyzer()
    try:
        with analyzer.driver.session() as session:
            # Step 1: Check all labels in database
            print("=== STEP 1: ALL NODE LABELS: ===")
            query_labels = '''
            CALL db.labels() YIELD label
            RETURN label
            '''
            result = session.run(query_labels)
            labels = [record['label'] for record in result]
            print(f'All labels in database: {sorted(labels)}')
            print()
            
            # Step 2: Find nodes with folder-like names
            print("=== STEP 2: SEARCHING FOR FOLDER NODES: ===")
            query_search = '''
            MATCH (n)
            WHERE (n.name CONTAINS 'tham khảo' OR n.name CONTAINS 'giáo trình' OR n.name CONTAINS 'đề cương')
                AND n.course_code = 'CMP177'
            RETURN n, labels(n) as labels
            '''
            result = session.run(query_search)
            folder_nodes = []
            for record in result:
                node = dict(record['n'])
                labels = record['labels']
                folder_nodes.append({'node': node, 'labels': labels})
                print(f'� {labels}')
                print(f'   name: "{node.get("name", "N/A")}"')
                print(f'   course_code: "{node.get("course_code", "N/A")}"')
                print(f'   All properties: {list(node.keys())}')
                print()
            
            # Step 3: Check for HAVE relationships
            print("=== STEP 3: CHECKING HAVE RELATIONSHIPS: ===")
            query_have = '''
            MATCH (f)-[r:HAVE]->(d:Document)
            WHERE f.course_code = 'CMP177'
            RETURN f.name as folder_name, labels(f) as folder_labels,
                   d.fileName as doc_file, d.folder_name as doc_folder_name
            LIMIT 20
            '''
            result = session.run(query_have)
            relationships = list(result)
            if relationships:
                print(f'Found {len(relationships)} HAVE relationships for CMP177:')
                for record in relationships:
                    print(f'📁 {record["folder_labels"]} "{record["folder_name"]}"')
                    print(f'   -[HAVE]-> 📄 "{record["doc_file"]}" (folder_name: "{record["doc_folder_name"]}")')
                    print()
            else:
                print("No HAVE relationships found for CMP177")
            
            # Step 4: Check for CMP177 nodes with ANY label
            print("=== STEP 4: ALL CMP177 NODES: ===")
            query_cmp177 = '''
            MATCH (n)
            WHERE n.course_code = 'CMP177'
            RETURN n, labels(n) as labels
            LIMIT 10
            '''
            result = session.run(query_cmp177)
            for record in result:
                node = dict(record['n'])
                labels = record['labels']
                print(f'🏷️ {labels}')
                print(f'   name: "{node.get("name", "N/A")}"')
                print(f'   course_code: "{node.get("course_code", "N/A")}"')
                if node.get('name') and any(keyword in node['name'] for keyword in ['tham khảo', 'giáo trình', 'đề cương']):
                    print(f'   ⭐ CONTAINS FOLDER KEYWORDS!')
                print()
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    debug_folder_matching()
