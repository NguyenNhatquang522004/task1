"""
Auto-connect và setup Neo4j khi khởi động project
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_neo4j import Neo4jGraph

# Load environment variables
load_dotenv()
load_dotenv("backend/.env")
load_dotenv("frontend/.env")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Neo4jAutoConnector:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI')
        self.username = os.getenv('NEO4J_USERNAME')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.database = os.getenv('NEO4J_DATABASE', 'neo4j')
        self.driver = None
        self.graph = None
        
    def print_status(self, message, status="INFO"):
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{symbols.get(status, 'ℹ️')} {message}")
        
    def validate_credentials(self):
        """Validate Neo4j credentials"""
        if not all([self.uri, self.username, self.password]):
            self.print_status("Missing Neo4j credentials!", "ERROR")
            self.print_status("Please check your .env file:", "INFO")
            self.print_status(f"  NEO4J_URI: {self.uri or 'MISSING'}", "INFO")
            self.print_status(f"  NEO4J_USERNAME: {self.username or 'MISSING'}", "INFO")
            self.print_status(f"  NEO4J_PASSWORD: {'SET' if self.password else 'MISSING'}", "INFO")
            return False
        return True
        
    def connect_driver(self):
        """Establish Neo4j driver connection"""
        try:
            self.print_status("Connecting to Neo4j...", "INFO")
            
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                connection_timeout=30,
                max_connection_lifetime=3600,
                keep_alive=True
            )
            
            # Test connection
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 'Connection successful!' as message")
                message = result.single()['message']
                
            self.print_status(f"Neo4j Driver: {message}", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_status(f"Neo4j Driver connection failed: {str(e)}", "ERROR")
            return False
            
    def connect_langchain(self):
        """Establish LangChain Neo4j connection"""
        try:
            self.graph = Neo4jGraph(
                url=self.uri,
                username=self.username,
                password=self.password,
                database=self.database
            )
            
            # Test LangChain connection
            result = self.graph.query("RETURN 'LangChain connection successful!' as message")
            message = result[0]['message']
            
            self.print_status(f"LangChain Neo4j: {message}", "SUCCESS")
            return True
            
        except Exception as e:
            self.print_status(f"LangChain Neo4j connection failed: {str(e)}", "ERROR")
            return False
            
    def recreate_vector_index(self):
        """Recreate vector index with correct dimensions for current embedding model"""
        try:
            self.print_status("Recreating vector index with correct dimensions...", "INFO")
            
            # Get embedding dimension from environment
            embedding_model = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')
            
            # Default dimensions for common models
            dimensions_map = {
                'all-MiniLM-L6-v2': 384,
                'BAAI/bge-m3': 1024,
                'text-embedding-ada-002': 1536,
                'text-embedding-3-small': 1536,
                'text-embedding-3-large': 3072
            }
            
            dimension = dimensions_map.get(embedding_model, 1024)
            
            # Check if vector index exists
            indexes = self.graph.query("SHOW INDEXES")
            vector_index_exists = any(idx.get('name') == 'vector' for idx in indexes)
            
            if vector_index_exists:
                self.print_status("Dropping existing vector index...", "INFO")
                self.graph.query("DROP INDEX vector IF EXISTS")
                self.print_status("Existing vector index dropped", "SUCCESS")
            
            # Create new vector index with correct dimensions
            self.print_status(f"Creating vector index with {dimension} dimensions...", "INFO")
            
            vector_index_query = f"""
            CREATE VECTOR INDEX vector IF NOT EXISTS
            FOR (c:Chunk) ON (c.embedding)
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {dimension},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
            """
            
            self.graph.query(vector_index_query)
            self.print_status(f"Vector index recreated (dimension: {dimension})", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.print_status(f"Vector index recreation failed: {str(e)}", "ERROR")
            return False
            
    def setup_indexes(self):
        """Setup required indexes for LLM Graph Builder"""
        try:
            self.print_status("Setting up Neo4j indexes...", "INFO")
            
            # Check existing indexes
            indexes = self.graph.query("SHOW INDEXES")
            vector_index_exists = any(idx.get('name') == 'vector' for idx in indexes)
            
            if not vector_index_exists:
                self.print_status("Creating vector index for embeddings...", "INFO")
                
                # Get embedding dimension from environment
                embedding_model = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')
                
                # Default dimensions for common models
                dimensions_map = {
                    'all-MiniLM-L6-v2': 384,
                    'BAAI/bge-m3': 1024,
                    'text-embedding-ada-002': 1536,
                    'text-embedding-3-small': 1536,
                    'text-embedding-3-large': 3072
                }
                
                dimension = dimensions_map.get(embedding_model, 1024)
                
                vector_index_query = f"""
                CREATE VECTOR INDEX vector IF NOT EXISTS
                FOR (c:Chunk) ON (c.embedding)
                OPTIONS {{
                    indexConfig: {{
                        `vector.dimensions`: {dimension},
                        `vector.similarity_function`: 'cosine'
                    }}
                }}
                """
                
                self.graph.query(vector_index_query)
                self.print_status(f"Vector index created (dimension: {dimension})", "SUCCESS")
            else:
                self.print_status("Vector index already exists", "INFO")
                
                # Check if dimensions match current model
                embedding_model = os.getenv('EMBEDDING_MODEL', 'BAAI/bge-m3')
                dimensions_map = {
                    'all-MiniLM-L6-v2': 384,
                    'BAAI/bge-m3': 1024,
                    'text-embedding-ada-002': 1536,
                    'text-embedding-3-small': 1536,
                    'text-embedding-3-large': 3072
                }
                expected_dimension = dimensions_map.get(embedding_model, 1024)
                
                try:
                    # Try to get index info to check dimensions
                    index_info = self.graph.query("CALL db.indexes() YIELD name, options WHERE name = 'vector' RETURN options")
                    if index_info:
                        current_dimensions = index_info[0]['options'].get('vector.dimensions', 0)
                        if current_dimensions != expected_dimension:
                            self.print_status(f"Vector index dimensions mismatch (current: {current_dimensions}, expected: {expected_dimension})", "WARNING")
                            self.print_status("Recreating vector index with correct dimensions...", "INFO")
                            return self.recreate_vector_index()
                except Exception as e:
                    self.print_status(f"Could not check index dimensions: {str(e)}", "WARNING")
                
            # Show all indexes
            indexes = self.graph.query("SHOW INDEXES")
            self.print_status(f"Total indexes: {len(indexes)}", "INFO")
            
            return True
            
        except Exception as e:
            self.print_status(f"Index setup failed: {str(e)}", "ERROR")
            return False
            
    def get_database_info(self):
        """Get and display database information"""
        try:
            # Database components
            components = self.graph.query("CALL dbms.components() YIELD name, edition, versions")
            for comp in components:
                self.print_status(f"Database: {comp['name']} {comp['edition']} {comp['versions'][0]}", "INFO")
            
            # Node count
            node_count = self.graph.query("MATCH (n) RETURN count(n) as count")[0]['count']
            self.print_status(f"Total nodes: {node_count:,}", "INFO")
            
            # Relationship count  
            rel_count = self.graph.query("MATCH ()-[r]->() RETURN count(r) as count")[0]['count']
            self.print_status(f"Total relationships: {rel_count:,}", "INFO")
            
            # Document count
            doc_count = self.graph.query("MATCH (d:Document) RETURN count(d) as count")[0]['count']
            self.print_status(f"Documents processed: {doc_count}", "INFO")
            
            return True
            
        except Exception as e:
            self.print_status(f"Could not get database info: {str(e)}", "WARNING")
            return False
            
    def auto_connect(self):
        """Main auto-connect method"""
        print("=" * 60)
        print("🚀 NEO4J AUTO-CONNECTOR - LLM GRAPH BUILDER")
        print("=" * 60)
        
        # Step 1: Validate credentials
        if not self.validate_credentials():
            return False
            
        # Step 2: Connect driver
        if not self.connect_driver():
            return False
            
        # Step 3: Connect LangChain
        if not self.connect_langchain():
            return False
            
        # Step 4: Setup indexes
        if not self.setup_indexes():
            self.print_status("Index setup failed, but connection works", "WARNING")
            
        # Step 5: Get database info
        self.get_database_info()
        
        print("=" * 60)
        self.print_status("Neo4j is ready for LLM Graph Builder!", "SUCCESS")
        self.print_status(f"Database: {self.uri}", "INFO")
        self.print_status(f"Instance: {os.getenv('AURA_INSTANCENAME', 'Unknown')}", "INFO")
        print("=" * 60)
        
        return True
        
    def cleanup(self):
        """Cleanup connections"""
        if self.driver:
            self.driver.close()

def main():
    """Main function"""
    connector = Neo4jAutoConnector()
    
    try:
        success = connector.auto_connect()
        
        if success:
            print("\n🎉 Neo4j connection established successfully!")
            print("🔗 Your LLM Graph Builder backend can now connect to Neo4j")
            print("📊 Ready to process documents and create knowledge graphs")
            return True
        else:
            print("\n❌ Neo4j connection failed!")
            print("🔧 Please check your credentials and network connection")
            print("💡 Visit https://console.neo4j.io to verify your instance")
            return False
            
    except KeyboardInterrupt:
        print("\n⏸️  Connection test interrupted by user")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return False
    finally:
        connector.cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
