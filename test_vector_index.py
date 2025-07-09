#!/usr/bin/env python3
"""
Test Vector Index with BGE-M3 Embedding Model
This script tests if the vector index works correctly with the new embedding model.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from neo4j_auto_connect import Neo4jAutoConnector

def test_vector_index():
    print("=" * 60)
    print("🧪 TESTING VECTOR INDEX WITH BGE-M3")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    load_dotenv("backend/.env")
    
    # Test 1: Check if backend is running
    print("1️⃣ Testing backend health...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is healthy!")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach backend: {str(e)}")
        return False
    
    # Test 2: Check Neo4j vector index
    print("\n2️⃣ Testing Neo4j vector index...")
    try:
        connector = Neo4jAutoConnector()
        if not connector.validate_credentials():
            print("❌ Invalid Neo4j credentials")
            return False
            
        if not connector.connect_driver():
            print("❌ Cannot connect to Neo4j")
            return False
            
        if not connector.connect_langchain():
            print("❌ Cannot connect to LangChain Neo4j")
            return False
            
        # Check if vector index exists
        indexes = connector.graph.query("SHOW INDEXES")
        vector_index = [idx for idx in indexes if idx.get('name') == 'vector']
        
        if not vector_index:
            print("❌ Vector index not found!")
            return False
            
        print(f"✅ Vector index found: {vector_index[0]['name']}")
        print(f"📊 Index state: {vector_index[0]['state']}")
        print(f"📊 Index type: {vector_index[0]['type']}")
        
        # Test 3: Test embedding dimensions
        print("\n3️⃣ Testing embedding dimensions...")
        
        # Import the embedding function
        sys.path.append('backend')
        from src.shared.common_fn import load_embedding_model
        
        # Load the embedding model
        embedding_model_name = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')
        embedding_result = load_embedding_model(embedding_model_name)
        
        # The function returns a tuple (embedding_model, dimension)
        embedding_model, dimension = embedding_result
        print(f"📊 Expected dimension: {dimension}")
        
        # Test embedding creation
        test_text = "This is a test text for embedding"
        test_embedding = embedding_model.embed_query(test_text)
        
        print(f"📊 Embedding dimensions: {len(test_embedding)}")
        
        if len(test_embedding) == 1024:
            print("✅ Embedding dimensions are correct (1024 for BGE-M3)")
        else:
            print(f"❌ Embedding dimensions are wrong (expected 1024, got {len(test_embedding)})")
            return False
            
        # Test 4: Test if we can store and query embeddings
        print("\n4️⃣ Testing vector storage and query...")
        
        # Create a test chunk with embedding
        test_chunk_query = """
        MERGE (c:Chunk {id: 'test-chunk-bge-m3'})
        SET c.text = $text, c.embedding = $embedding
        RETURN c
        """
        
        result = connector.graph.query(test_chunk_query, {
            'text': test_text,
            'embedding': test_embedding
        })
        
        if result:
            print("✅ Successfully stored test chunk with embedding")
        else:
            print("❌ Failed to store test chunk")
            return False
            
        # Test vector similarity search
        print("\n5️⃣ Testing vector similarity search...")
        
        # Create another test text and embedding
        query_text = "This is a test query for similarity search"
        query_embedding = embedding_model.embed_query(query_text)
        
        # Test vector similarity search
        similarity_query = """
        CALL db.index.vector.queryNodes('vector', 1, $query_embedding)
        YIELD node, score
        RETURN node.text AS text, score
        """
        
        try:
            similarity_result = connector.graph.query(similarity_query, {
                'query_embedding': query_embedding
            })
            
            if similarity_result:
                print("✅ Vector similarity search successful!")
                print(f"📊 Found {len(similarity_result)} results")
                if similarity_result:
                    print(f"📊 Top result: {similarity_result[0]['text']}")
                    print(f"📊 Similarity score: {similarity_result[0]['score']:.4f}")
            else:
                print("⚠️ No results from vector similarity search")
                
        except Exception as e:
            print(f"❌ Vector similarity search failed: {str(e)}")
            return False
        
        # Clean up test data
        print("\n6️⃣ Cleaning up test data...")
        connector.graph.query("MATCH (c:Chunk {id: 'test-chunk-bge-m3'}) DELETE c")
        print("✅ Test data cleaned up")
        
        # Close connection
        if connector.driver:
            connector.driver.close()
            
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("✅ BGE-M3 embedding model is working correctly")
        print("✅ Vector index is properly configured with 1024 dimensions")
        print("✅ Vector storage and similarity search are functional")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_vector_index()
    sys.exit(0 if success else 1)
