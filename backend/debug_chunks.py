#!/usr/bin/env python3
"""
Debug script to check chunks in Neo4j database
"""
import sys
import os
import logging

# Add the current directory to the Python path to import src modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.shared.common_fn import create_graph_database_connection
from src.graph_query import execute_graph_query
from src.shared.constants import QUERY_TO_GET_CHUNKS
from dotenv import load_dotenv

def debug_chunks():
    """Debug chunks in the database for specific files"""
    
    load_dotenv()
    
    # Database connection
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME') 
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    print(f"🔍 Debugging chunks in Neo4j...")
    print(f"URI: {uri}")
    print(f"Database: {database}")
    
    try:
        graph = create_graph_database_connection(uri, username, password, database)
        print(f"✅ Connected to Neo4j")
        
        # Check all documents first
        documents_query = """
        MATCH (d:Document)
        RETURN d.fileName as fileName, d.status as status, d.total_chunks as total_chunks
        ORDER BY d.created_at DESC
        LIMIT 10
        """
        
        documents = execute_graph_query(graph, documents_query)
        print(f"\n📄 Recent Documents in Database:")
        for doc in documents:
            print(f"  - {doc['fileName']} | Status: {doc['status']} | Total Chunks: {doc['total_chunks']}")
        
        # Focus on the problematic file
        file_name = "[CMP177] beginningflutter.pdf"
        print(f"\n🔍 Checking chunks for file: {file_name}")
        
        # Get chunks using the same query as the main code
        chunks = execute_graph_query(graph, QUERY_TO_GET_CHUNKS, params={"filename": file_name})
        
        print(f"📊 Query Results:")
        print(f"  - Number of chunks returned: {len(chunks)}")
        
        if chunks:
            print(f"  - First chunk sample:")
            first_chunk = chunks[0]
            print(f"    * ID: {first_chunk.get('id')}")
            print(f"    * Text: {first_chunk.get('text', 'None')[:100] if first_chunk.get('text') else 'None'}...")
            print(f"    * Position: {first_chunk.get('position')}")
            
            # Check for None/empty text issue
            none_chunks = [c for c in chunks if not c.get('text') or c.get('text') == ""]
            print(f"  - Chunks with None/empty text: {len(none_chunks)}")
            
            if none_chunks:
                print(f"  - Sample problematic chunk: {none_chunks[0]}")
        else:
            print(f"  - No chunks found!")
            
        # Check document status specifically
        doc_status_query = """
        MATCH (d:Document {fileName: $filename})
        RETURN d.status as status, d.total_chunks as total_chunks, 
               d.processed_chunk as processed_chunk, d.created_at as created_at
        """
        
        doc_result = execute_graph_query(graph, doc_status_query, params={"filename": file_name})
        
        if doc_result:
            doc = doc_result[0]
            print(f"\n📋 Document Status:")
            print(f"  - Status: {doc['status']}")
            print(f"  - Total Chunks: {doc['total_chunks']}")
            print(f"  - Processed Chunks: {doc['processed_chunk']}")
            print(f"  - Created At: {doc['created_at']}")
        else:
            print(f"\n❌ Document not found in database: {file_name}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chunks()
