"""
Script để test Neo4j connection và troubleshoot network issues
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import logging

load_dotenv()

def test_neo4j_connection():
    """Test kết nối đến Neo4j database"""
    
    # Đọc cấu hình từ .env
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME') 
    password = os.getenv('NEO4J_PASSWORD')
    database = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    print("🔍 Neo4j Connection Configuration:")
    print(f"   URI: {uri}")
    print(f"   Username: {username}")
    print(f"   Database: {database}")
    print(f"   Password: {'*' * len(password) if password else 'None'}")
    print()
    
    if not all([uri, username, password]):
        print("❌ Missing required Neo4j credentials!")
        print("   Please check your .env file:")
        print("   NEO4J_URI=neo4j+s://013fb011.databases.neo4j.io")
        print("   NEO4J_USERNAME=neo4j")
        print("   NEO4J_PASSWORD=your_password")
        return False
    
    try:
        print("🔌 Attempting to connect to Neo4j...")
        
        # Tạo driver với timeout settings
        driver = GraphDatabase.driver(
            uri, 
            auth=(username, password),
            connection_timeout=30,  # 30 seconds timeout
            max_connection_lifetime=3600,  # 1 hour
            keep_alive=True
        )
        
        # Test connection với simple query
        with driver.session(database=database) as session:
            print("🔄 Running test query...")
            result = session.run("RETURN 'Hello Neo4j!' as message")
            record = result.single()
            
            if record:
                print(f"✅ Connection successful!")
                print(f"   Message: {record['message']}")
                
                # Test thêm thông tin về database
                print("\n📊 Database Information:")
                db_info = session.run("CALL dbms.components() YIELD name, edition, versions")
                for info in db_info:
                    print(f"   {info['name']}: {info['edition']} - {info['versions']}")
                
                # Check số nodes hiện tại
                node_count = session.run("MATCH (n) RETURN count(n) as count").single()
                print(f"   Total nodes: {node_count['count']}")
                
                # Check indexes
                indexes = session.run("SHOW INDEXES").data()
                print(f"   Total indexes: {len(indexes)}")
                
                driver.close()
                return True
                
    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"   Error: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        
        # Phân tích loại lỗi
        error_str = str(e).lower()
        
        if "network" in error_str or "timeout" in error_str:
            print("\n🌐 Network Issue Detected:")
            print("   Possible causes:")
            print("   1. Internet connection problems")
            print("   2. Neo4j Aura instance not running")
            print("   3. Firewall blocking connection")
            print("   4. DNS resolution issues")
            print("\n   Solutions:")
            print("   - Check internet connection")
            print("   - Verify Neo4j Aura instance is active at console.neo4j.io")
            print("   - Try different network (mobile hotspot)")
            print("   - Check firewall settings")
            
        elif "authentication" in error_str or "unauthorized" in error_str:
            print("\n🔐 Authentication Issue:")
            print("   - Check username/password in .env file")
            print("   - Verify credentials at console.neo4j.io")
            print("   - Password might have expired")
            
        elif "database" in error_str:
            print("\n🗄️ Database Issue:")
            print("   - Check database name is correct")
            print("   - Default database name is usually 'neo4j'")
            
        else:
            print(f"\n❓ Unknown error: {e}")
            
        return False

def test_neo4j_with_langchain():
    """Test Neo4j connection với LangChain Neo4jGraph"""
    try:
        print("\n🔗 Testing with LangChain Neo4jGraph...")
        from langchain_neo4j import Neo4jGraph
        
        uri = os.getenv('NEO4J_URI')
        username = os.getenv('NEO4J_USERNAME')
        password = os.getenv('NEO4J_PASSWORD')
        database = os.getenv('NEO4J_DATABASE', 'neo4j')
        
        graph = Neo4jGraph(
            url=uri,
            username=username, 
            password=password,
            database=database
        )
        
        # Test query
        result = graph.query("RETURN 'LangChain connection successful!' as message")
        print(f"✅ LangChain connection: {result[0]['message']}")
        
        # Test graph capabilities
        schema = graph.get_schema
        print(f"📋 Graph schema available: {'Yes' if schema else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("NEO4J CONNECTION DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Test 1: Basic Neo4j driver connection
    basic_success = test_neo4j_connection()
    
    # Test 2: LangChain connection (if basic works)
    if basic_success:
        langchain_success = test_neo4j_with_langchain()
    else:
        print("⏭️ Skipping LangChain test due to basic connection failure")
        
    print("\n" + "=" * 60)
    if basic_success:
        print("🎉 Neo4j connection is working!")
        print("   Your LLM Graph Builder should work properly.")
    else:
        print("❌ Neo4j connection issues detected.")
        print("   Please fix connection before using LLM Graph Builder.")
    print("=" * 60)
