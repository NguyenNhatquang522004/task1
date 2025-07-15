import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

try:
    print('Testing Neo4j connection...')
    graph = Neo4jGraph(
        url=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        username=os.getenv('NEO4J_USERNAME', 'neo4j'),
        password=os.getenv('NEO4J_PASSWORD', 'password'),
        database=os.getenv('NEO4J_DATABASE', 'neo4j')
    )
    
    print('✅ Neo4j connection successful!')
    print(f'Schema loaded: {len(graph.schema)} characters')
    graph.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
