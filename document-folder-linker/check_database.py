from neo4j import GraphDatabase

# Connect to Neo4j
driver = GraphDatabase.driver(
    'neo4j+s://013fb011.databases.neo4j.io', 
    auth=('neo4j', 'NH43Qy392yswBCfUFNrjYjIIvr4B_LcJB4eMRNzHrp4')
)

session = driver.session()

# Check entity types
print("=== AVAILABLE ENTITY TYPES ===")
result = session.run('''
MATCH (n) 
WHERE NOT n:Document AND NOT n:Chunk 
RETURN DISTINCT labels(n) as labels, count(*) as count 
ORDER BY count DESC LIMIT 10
''')

for record in result:
    print(f"- {record['labels']}: {record['count']}")

# Check documents with folder_name and course_code
print("\n=== DOCUMENTS WITH PROPERTIES ===")
result = session.run('''
MATCH (d:Document) 
WHERE d.folder_name IS NOT NULL AND d.course_code IS NOT NULL
RETURN d.fileName, d.folder_name, d.course_code
''')

for record in result:
    print(f"- {record['d.fileName']} (folder: {record['d.folder_name']}, course: {record['d.course_code']})")

# Check folder nodes
print("\n=== FOLDER NODES ===")
result = session.run('''
MATCH (f)
WHERE size(labels(f)) = 1 
    AND f.name IS NOT NULL 
    AND f.course_code IS NOT NULL
    AND NOT f:Document AND NOT f:Course
RETURN labels(f)[0] as folder_type, f.name, f.course_code, count(*) as node_count
ORDER BY f.course_code, folder_type
LIMIT 20
''')

for record in result:
    print(f"- {record['folder_type']}: {record['f.name']} ({record['f.course_code']}) - {record['node_count']} nodes")

driver.close()
