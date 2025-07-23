#!/usr/bin/env python3
"""
Script to fix failed document processing by resetting status
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_neo4j import Neo4jGraph
from dotenv import load_dotenv

def fix_failed_document():
    """Fix the failed document by resetting its status"""
    
    # Load environment variables
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
    
    # Neo4j connection from environment
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME') 
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    file_name = "[CMP177] beginningflutter.pdf"
    
    print(f"🔧 Fixing failed document: {file_name}")
    print(f"🔗 Connecting to: {uri}")
    print(f"🔗 Database: {database}")
    print(f"🔗 Username: {username}")
    
    try:
        # Connect to Neo4j
        graph = Neo4jGraph(
            url=uri,
            username=username,
            password=password,
            database=database
        )
        
        print(f"✅ Connected to Neo4j at {uri}")
        
        # 1. Check current status
        check_query = """
        MATCH (d:Document {fileName: $filename})
        RETURN d.fileName as fileName, d.status as status, 
               d.total_chunks as total_chunks, d.processed_chunk as processed_chunk,
               d.created_at as created_at
        """
        
        result = graph.query(check_query, params={"filename": file_name})
        
        if result:
            doc = result[0]
            print(f"\n📋 Current Document Status:")
            print(f"  - File Name: {doc['fileName']}")
            print(f"  - Status: {doc['status']}")
            print(f"  - Total Chunks: {doc['total_chunks']}")
            print(f"  - Processed Chunks: {doc['processed_chunk']}")
            print(f"  - Created At: {doc['created_at']}")
        else:
            print(f"❌ Document not found: {file_name}")
            return
        
        # 2. Check if chunks exist
        chunks_query = """
        MATCH (d:Document {fileName: $filename})
        OPTIONAL MATCH (d)<-[:PART_OF|FIRST_CHUNK]-(c:Chunk)
        RETURN count(c) as chunk_count, collect(c.id)[0..5] as sample_chunk_ids
        """
        
        chunks_result = graph.query(chunks_query, params={"filename": file_name})
        chunk_count = chunks_result[0]['chunk_count'] if chunks_result else 0
        sample_chunks = chunks_result[0]['sample_chunk_ids'] if chunks_result else []
        
        print(f"\n📊 Chunks Status:")
        print(f"  - Chunks in database: {chunk_count}")
        print(f"  - Sample chunk IDs: {sample_chunks}")
        
        # 3. Decision on how to fix
        if chunk_count > 0:
            print(f"\n✅ Chunks exist! The issue might be with document status.")
            print(f"🔧 Resetting document status to allow reprocessing...")
            
            # Reset status to allow reprocessing
            reset_query = """
            MATCH (d:Document {fileName: $filename})
            SET d.status = 'New',
                d.processed_chunk = 0,
                d.updated_at = datetime()
            RETURN d.status as new_status
            """
            
            reset_result = graph.query(reset_query, params={"filename": file_name})
            print(f"✅ Document status reset to: {reset_result[0]['new_status']}")
            
        else:
            print(f"\n❌ No chunks found! Need to delete document and re-upload.")
            print(f"🗑️ Deleting failed document node...")
            
            # Delete the document node so it can be re-uploaded
            delete_query = """
            MATCH (d:Document {fileName: $filename})
            DELETE d
            RETURN count(*) as deleted_count
            """
            
            delete_result = graph.query(delete_query, params={"filename": file_name})
            print(f"✅ Deleted document. Count: {delete_result[0]['deleted_count']}")
            print(f"💡 Now you can re-upload the file from scratch.")
        
        # 4. Final verification
        final_check = graph.query(check_query, params={"filename": file_name})
        
        if final_check:
            doc = final_check[0]
            print(f"\n🎯 Final Status:")
            print(f"  - Status: {doc['status']}")
            print(f"  - Ready for reprocessing: {'✅' if doc['status'] in ['New', 'Ready'] else '❌'}")
        else:
            print(f"\n🎯 Document removed from database - ready for fresh upload")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_failed_document()
