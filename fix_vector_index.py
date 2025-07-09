#!/usr/bin/env python3
"""
Fix Vector Index Dimensions for LLM Graph Builder
This script fixes the vector index dimensions mismatch when changing embedding models.
"""

import os
import sys
from dotenv import load_dotenv
from neo4j_auto_connect import Neo4jAutoConnector

def main():
    print("=" * 60)
    print("🔧 FIXING VECTOR INDEX DIMENSIONS")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    load_dotenv("backend/.env")
    
    # Get current embedding model
    embedding_model = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')
    print(f"🔍 Current embedding model: {embedding_model}")
    
    # Initialize Neo4j connector
    connector = Neo4jAutoConnector()
    
    # Connect to Neo4j
    if not connector.validate_credentials():
        print("❌ Cannot connect to Neo4j. Please check your credentials.")
        sys.exit(1)
        
    if not connector.connect_driver():
        print("❌ Failed to connect to Neo4j driver.")
        sys.exit(1)
        
    if not connector.connect_langchain():
        print("❌ Failed to connect to LangChain Neo4j.")
        sys.exit(1)
        
    print("✅ Connected to Neo4j successfully!")
    
    # Check current vector index
    try:
        indexes = connector.graph.query("SHOW INDEXES")
        vector_index_exists = any(idx.get('name') == 'vector' for idx in indexes)
        
        if not vector_index_exists:
            print("ℹ️ No vector index found. Creating new one...")
            if connector.setup_indexes():
                print("✅ Vector index created successfully!")
            else:
                print("❌ Failed to create vector index.")
                sys.exit(1)
        else:
            print("ℹ️ Vector index exists. Checking dimensions...")
            
            # Get expected dimensions
            dimensions_map = {
                'all-MiniLM-L6-v2': 384,
                'BAAI/bge-m3': 1024,
                'text-embedding-ada-002': 1536,
                'text-embedding-3-small': 1536,
                'text-embedding-3-large': 3072
            }
            
            expected_dimension = dimensions_map.get(embedding_model, 1024)
            print(f"📊 Expected dimensions: {expected_dimension}")
            
            # Try to get current dimensions from index info
            try:
                index_info = connector.graph.query("CALL db.indexes() YIELD name, options WHERE name = 'vector' RETURN options")
                if index_info:
                    current_dimensions = index_info[0]['options'].get('vector.dimensions', 0)
                    print(f"📊 Current dimensions: {current_dimensions}")
                    
                    if current_dimensions != expected_dimension:
                        print("⚠️ Dimensions mismatch detected!")
                        print("🔄 Recreating vector index with correct dimensions...")
                        
                        if connector.recreate_vector_index():
                            print("✅ Vector index recreated successfully!")
                        else:
                            print("❌ Failed to recreate vector index.")
                            sys.exit(1)
                    else:
                        print("✅ Vector index dimensions are correct!")
                else:
                    print("⚠️ Could not check index dimensions. Recreating to be safe...")
                    if connector.recreate_vector_index():
                        print("✅ Vector index recreated successfully!")
                    else:
                        print("❌ Failed to recreate vector index.")
                        sys.exit(1)
            except Exception as e:
                print(f"⚠️ Could not check index dimensions: {str(e)}")
                print("🔄 Recreating vector index to be safe...")
                if connector.recreate_vector_index():
                    print("✅ Vector index recreated successfully!")
                else:
                    print("❌ Failed to recreate vector index.")
                    sys.exit(1)
                    
    except Exception as e:
        print(f"❌ Error checking vector index: {str(e)}")
        sys.exit(1)
        
    # Final verification
    try:
        indexes = connector.graph.query("SHOW INDEXES")
        vector_index = [idx for idx in indexes if idx.get('name') == 'vector']
        if vector_index:
            print("✅ Vector index verification successful!")
            print(f"📊 Index details: {vector_index[0]}")
        else:
            print("❌ Vector index not found after recreation!")
            sys.exit(1)
    except Exception as e:
        print(f"⚠️ Could not verify vector index: {str(e)}")
        
    print("=" * 60)
    print("🎉 VECTOR INDEX FIX COMPLETED!")
    print("=" * 60)
    print("✅ Your Neo4j vector index is now compatible with the current embedding model.")
    print("✅ You can now restart your backend server.")
    
    # Close connection
    if connector.driver:
        connector.driver.close()

if __name__ == "__main__":
    main()
